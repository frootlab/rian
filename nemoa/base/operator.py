# -*- coding: utf-8 -*-
"""Operators and helper functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import ast
import collections
import contextlib
import functools
import inspect
import itertools
import operator
import re
from typing import NamedTuple, Dict, List, Optional, Tuple, Sequence, Union
from typing import Any, Hashable
import py_expression_eval
from nemoa.base import check, abc, stype
from nemoa.errors import InvalidTypeError
from nemoa.types import Method, Mapping, NoneType, Callable, OptOp, OptStrTuple
from nemoa.types import SeqHom, SeqOp, AnyOp
from nemoa.base.stype import FieldID, Frame

Expr = Any # TODO: Use py_expression_eval.Expression when typeshed is ready
Key = Optional[Union[FieldID, Frame]]
Item = Tuple[FieldID, Any]
VarLike = Union[
    str,                        # Variable((<name>, ), Identity, <name>)
    Tuple[str],                 # Variable((<name>, ), Identity, <name>)
    Tuple[str, FieldID],        # Variable((<id>, ), Identity, <name>)
    Tuple[str, Frame],          # Variable(<frame>, Identity, <name>
    Tuple[str, AnyOp],          # Variable((<name>, ), <operator>, <name>)
    Tuple[str, AnyOp, FieldID], # Variable((<id>, ), <operator>, <name>)
    Tuple[str, AnyOp, Frame]]   # Variable(<frame>, <operator>, <name>)

#
# Variables
#

class Variable(NamedTuple):
    """Class for the storage of variable definitions."""
    name: str
    operator: AnyOp
    frame: Frame

    def __call__(self, *args: Any) -> Any:
        return self.operator(*args)

#
# Constructors for Parameter Classes
#

def create_variable(var: VarLike, default: OptOp = None) -> Variable:
    """Create variable from variable definition.

    Args:

    Returns:

    """
    # Check Arguments
    check.has_type('var', var, (str, tuple))
    check.not_empty('var', var)

    # Get Defaults
    default = default or Identity()

    # Get Variable Arguments
    args: VarLike
    if isinstance(var, str):
        args = (var, default, (var, ))
    elif len(var) == 1:
        args = (var[0], default, (var[0], ))
    elif len(var) == 2:
        if callable(var[1]):
            args = (var[0], var[1], (var[0], ))
        elif isinstance(var[1], tuple):
            args = (var[0], default, var[1])
        else:
            args = (var[0], default, (var[1], ))
    elif isinstance(var[2], tuple):
        args = (var[0], var[1], var[2])
    else:
        args = (var[0], var[1], (var[2], ))

    # Check Variable Arguments
    check.has_type('variable name', args[0], str)
    check.has_type('variable operator', args[1], Callable)
    check.has_type('variable frame', args[2], tuple)

    # Create and return Variable
    return Variable(*args)

#
# Operator Classes
#

class Operator(collections.abc.Callable): # type: ignore
    """Abstract Base Class for operators."""
    __slots__: list = ['_domain', '_target']

    _domain: stype.Domain
    _target: stype.Domain

    def __init__(
        self, domain: stype.DomLike = None,
        target: stype.DomLike = None) -> None:
        self._domain = stype.create_domain(domain)
        self._target = stype.create_domain(target)

    @property
    def domain(self) -> stype.Domain:
        try:
            return self._domain
        except AttributeError:
            return stype.create_domain()

    @property
    def target(self) -> stype.Domain:
        try:
            return self._target
        except AttributeError:
            return stype.create_domain()

class Zero(Operator, abc.Multiton):
    """Class for zero operators.

    A zero operator (or zero morphism) maps all given arguments to the zero
    object (empty object) of a given target category.

    Args:
        target: Optional target category of the operator. If provided, the
            target category must by given as a :class:`type`, like
            :class:`int`, :class:`float`, :class:`str`, :class:`set`,
            :class:`tuple`, :class:`list`, :class:`dict` or :class:`object`.
            Then the returned operator maps all objects of any domain category
            to the zero object of the target category. By default the used zero
            object is None.

    """
    __slots__ = ['_zero']

    _zero: Any

    def __init__(self, target: stype.DomLike = None) -> None:
        super().__init__(domain=None, target=target)

        # Sanity check if the target type has a unique zero object
        target_type = self._target.type
        if not target_type() == target_type():
            raise ValueError(
                f"target type '{target_type.__name__}' is not supported: "
                "zero object is not unique") # TODO

        self._zero = self._target.type() # Create zero object in target type

    def __call__(self, *args: Any) -> Any:
        return self._zero

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        class_name = type(self).__name__
        target_type = self._target.type.__name__
        return f"{class_name}({target_type})"

class Identity(Operator, abc.Multiton):
    """Class for identity operators."""
    __slots__: list = []

    def __init__(self, domain: stype.DomLike = None) -> None:
        super().__init__(domain=domain, target=domain)

    def __call__(self, *args: Any) -> Any:
        if not args:
            return None
        if len(args) == 1:
            return args[0]
        return args

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        name = type(self).__name__
        dom_type = self.domain.type
        if dom_type == NoneType:
            return f'{type(self).__name__}'
        return f'{type(self).__name__}({dom_type.__name__})'

class Projection(Operator, abc.Multiton):
    """Class for Projections.

    A projection essentially is a compositions of a `getter`, that specified
    fields from a given domain and a `representer`, that represents the fetched
    fields as an object of given target.

    Args:
        *args: Valid :term:`field identifiers <field identifier>` within the
            domain type.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. Supported
            domain types are :class:`object`, subclasses of the :class:`Mapping
            class <collection.abs.Mapping>` and subclasses of the
            :class:`Sequence class <collection.abs.Sequence>`. If no domain type
            is specified (which is indicated by the default value None) the
            fields are identified by their argument positions of the operator.
        target: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's target. Supported
            target types are :class:`tuple`, :class:`list` and :class:`dict`. If
            no target is specified (which is indicated by the default value
            None) the target type depends on the arguments, that are passed to
            the operator. In this case for a single argument, the target type
            equals the type of the argument and for multiple argumnts, the
            target type is tuple.

    """
    __slots__ = ['_operator']

    _operator: Any

    def __new__(
            cls, *args: FieldID, domain: stype.DomLike = None,
            target: stype.DomLike = None) -> Operator:

        domain = stype.create_domain(domain, defaults={'fields': args})
        target = stype.create_domain(target, defaults={'fields': args})

        # If no fields are given, the projection is a zero operator.
        if not args:
            return Zero(target=target)

        # If the domain equals the target (type, frame and basis)
        if domain == target:
            return Identity(domain=domain)

        return super().__new__(cls)

    def __init__(self,
            *args: FieldID, domain: stype.DomLike = None,
            target: stype.DomLike = None) -> None:

        # Set domain and target
        domain = stype.create_domain(domain, defaults={'fields': args})
        target = stype.create_domain(target, defaults={'fields': args})
        super().__init__(domain=domain, target=target)

        # Build getter and formatter
        getter = self._build_getter(*args, domain=domain)
        formatter = create_formatter(*args, target=target)

        # If the formatter is an identity operator, return getter. If the getter
        # is an identity operator, precede a tuple 'packer' to the formatter
        if isinstance(formatter, Identity):
            self._operator = getter
        elif isinstance(getter, Identity):
            self._operator = compose(formatter, lambda *args: args)
        else:
            self._operator = compose(formatter, getter)

    def __call__(self, *args: Any) -> Any:
        return self._operator(*args)

    def __repr__(self) -> str:
        if isinstance(self._operator, Operator):
            return repr(self._operator)
        name = type(self).__name__
        try:
            frame = self._domain.frame
            return f"{name}({', '.join(map(repr, frame))})"
        except AttributeError:
            return f"{name}()"
        except TypeError:
            return f"{name}()"

    def __len__(self) -> int:
        try:
            return len(self._operator)
        except TypeError:
            return len(self._target.frame)

    def _build_getter(self, *args: FieldID, domain: stype.Domain) -> AnyOp:

        # If the domain type is NoneType, the returned operator fetches and
        # returns the fields directly from it's given arguments. In this case,
        # if the fields equal the domain frame, the returned operator is the
        # Identity. If the fields, however, do not equal the domain frame, the
        # returned operator is an item getter, that operates on the tuple of
        # arguments.
        if domain.type == NoneType:
            if domain.frame == args:
                return Identity(domain=domain)
            check.is_subset('fields', set(args), 'frame', set(domain.frame))
            igettr = operator.itemgetter(*map(domain.frame.index, args))
            return lambda *args: igettr(args)

        # If the domain type is object, check if the given field identifiers are
        # valid attribute identifiers. In this case return an attribute getter,
        # (created by attrgetter from the standard library module operator)
        if domain.type == object:
            for arg in args:
                if not (isinstance(arg, str) and arg.isidentifier):
                    raise InvalidTypeError(
                        'field', arg, 'a valid attribute name')
            return operator.attrgetter(*args) # type: ignore

        # If the domain is a mapping, check if field identifiers are valid
        # mapping keys and return itemgetter() from standard library module
        # operator
        if issubclass(domain.type, Mapping):
            for arg in args:
                if not isinstance(arg, Hashable):
                    raise InvalidTypeError('field', arg, 'a valid mapping key')
            return operator.itemgetter(*args)

        # If the domain is a sequence and a frame is given, check that all field
        # identifiers are contained within the frame. In this case the frame is
        # used to determine the positions and an itemgetter() from standard
        # library module operator is returned. If, however, no frame is given
        # the field identifiers are required to be valid positions. In this case
        # also an itemgetter() is returned.
        if issubclass(domain.type, Sequence):
            if domain.frame:
                if not set(args) <= set(domain.frame):
                    raise ValueError() # TODO: NotInList
                return operator.itemgetter(*map(domain.frame.index, args))
            for arg in args:
                if not isinstance(arg, int) or arg < 0:
                    raise InvalidTypeError(
                        'any field', args, 'positive integer')
            return operator.itemgetter(*args)

        # TODO: raise InvalidValueError!
        raise InvalidTypeError(
            'domain type', domain.type, (object, Mapping, Sequence))

class Mapper(collections.abc.Sequence, Operator, abc.Multiton):
    """Class for mapping operators.

    Args:
        *args: Optional definitions of the function components. If provided, any
            component has to be given as a valid :term:`variable definition`.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in the class :class:`Projection`.
        target: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's target. The accepted
            parameter values are documented in the class :class:`Projection`.
        default: Default operator which is used to map fields to field
            variables. By default the identity is used.

    """
    __slots__ = ['_variables', '_call_partial', '_call_total']

    _variables: Tuple[Variable, ...]
    _call_partial: Tuple[AnyOp, ...]
    _call_total: Any

    def __init__(
            self, *args: VarLike, domain: stype.DomLike = None,
            target: stype.DomLike = None, default: OptOp = None) -> None:
        super().__init__()

        self._update_variables(*args, default=default)
        self._update_domain(domain)
        self._update_target(target)
        self._update_call_partial()
        self._update_call_total()

    def __call__(self, *args: Any) -> Any:
        return self._call_total(*args)

    def __getitem__(self, pos: Union[int, slice]) -> Any:
        if isinstance(pos, int):
            return self._call_partial[pos]
        if isinstance(pos, slice):
            ops = self._call_partial[pos]
            return lambda *args: tuple(op(*args) for op in ops)
        raise InvalidTypeError('pos', pos, (int, slice))

    def __len__(self) -> int:
        return len(self._variables)

    def __repr__(self) -> str:
        name = type(self).__name__
        fields = ', '.join(map(repr, self.fields))
        if not fields:
            return f"{name}()"
        return f"{name}({fields})"

    @property
    def fields(self) -> Frame:
        if not hasattr(self, '_domain'):
            return tuple()
        if self._domain.frame:
            return self._domain.frame
        if not hasattr(self, '_variables'):
            return tuple()
        fields = []
        for var in self._variables:
            for field in var.frame:
                fields.append(field)
        return tuple(fields)

    @property
    def components(self) -> Tuple[str, ...]:
        if not hasattr(self, '_variables'):
            return tuple()
        return tuple(var.name for var in self._variables)

    def _update_variables(self, *args: VarLike, default: OptOp = None) -> None:
        var: AnyOp = lambda arg: create_variable(arg, default=default)
        self._variables = tuple(map(var, args))

    def _update_domain(self, domain: stype.DomLike = None) -> None:
        fields: List[FieldID] = []
        for var in self._variables:
            for field in var.frame:
                if not field in fields:
                    fields.append(field)
        defaults = {'fields': tuple(fields)}
        self._domain = stype.create_domain(domain, defaults=defaults)

    def _update_target(self, target: stype.DomLike = None) -> None:
        fields = tuple(var.name for var in self._variables)
        defaults = {'fields': fields}
        self._target = stype.create_domain(target, defaults=defaults)

    def _update_call_partial(self) -> None:
        # Check if all field identifiers are found within the frame. Note that
        # this is also True if no frame is used, since set() <= set()
        if not set(self.fields) <= set(self._domain.frame):
            raise ValueError() # TODO

        # Create operators for the partial (per component) evaluation of the
        # mapper
        ops: List[AnyOp] = []
        for var in self._variables:
            getter = Projection(*var.frame, domain=self.domain)
            if isinstance(var.operator, Identity):
                ops.append(getter)
            elif not var.frame:
                ops.append(var.operator)
            elif len(var.frame) == 1:
                ops.append(compose(var.operator, getter))
            else:
                ops.append(compose(var.operator, getter, unpack=True))
        self._call_partial = tuple(ops)

    def _update_call_total(self) -> None:
        variables = self._variables
        domain = self._domain
        target = self._target

        # If no variables are specified, the mapper is the zero operator of the
        # target type.
        if not variables:
            self._call_total = Zero(target)
            return

        # Check if the mapper can be implemented as a coordinate projection. In
        # this case create and return the projection
        equal: AnyOp = lambda var: (
            len(var.frame) == 1 and isinstance(var.operator, Identity))
        if all(map(equal, variables)):
            fields = tuple(var.frame[0] for var in variables)
            projection = Projection(
                *fields, domain=self.domain, target=self.target)
            if hasattr(projection, '_operator'):
                self._call_total = projection._operator
            else:
                self._call_total = projection
            return

        # If the mapper can not be implemented as a projection ...
        # TODO: Implement as follows:
        # 1. single getter
        # 2. apply all component operators ...
        # 3. single formatter
        mapper: AnyOp
        f = self._call_partial
        if len(self) == 1:
            mapper = f[0]
        elif len(self) == 2:
            mapper = lambda *args: (f[0](*args), f[1](*args))
        elif len(self) == 3:
            mapper = lambda *args: (f[0](*args), f[1](*args), f[2](*args))
        else:
            mapper = lambda *args: tuple(comp(*args) for comp in f)

        # Create formatter
        formatter = create_formatter(*self.components, target=self.target)

        # If the formatter is an identity operator, return mapper. If the mapper
        # is an identity operator, precede a tuple 'packer' to the formatter
        if isinstance(formatter, Identity):
            self._call_total = mapper
        elif isinstance(mapper, Identity):
            self._call_total = compose(formatter, lambda *args: args)
        else:
            self._call_total = compose(formatter, mapper)

class Lambda(Operator):
    """Class for operators, that are based on arithmetic expressions.

    Args:
        expression:
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        variables: Tuple of variable names. This parameter is only required, if
            the domain category is a subclass of the :class:`Sequence class
            <collection.abs.Sequence>`. In this case the variable names are used
            to map the fields (given as names) to their indices within the
            domain tuple.
        default:
        assemble: Optional Boolean parameter, which determines if the operator
            is compiled after it is parsed.

    """
    _expression: str
    _operator: Any

    def __init__(
            self, expression: str = '', domain: stype.DomLike = None,
            default: OptOp = None, assemble: bool = True) -> None:
        super().__init__(domain=domain, target=None)

        self._expression = expression

        # Create Operator
        if expression:
            self._create_operator(assemble=assemble)
        elif callable(default):
            self._operator = default
        else:
            self._operator = Zero()

    def __call__(self, *args: Any) -> Any:
        return self._operator(*args)

    def __repr__(self) -> str:
        with contextlib.suppress(AttributeError):
            if self._expression:
                return f"{type(self).__name__}('{self._expression}')"
        with contextlib.suppress(AttributeError):
            return repr(self._operator)
        return f"{type(self).__name__}()"

    #
    # Public
    #

    @property
    def variables(self) -> Frame:
        with contextlib.suppress(AttributeError):
            attrs = self._operator.variables
            if callable(attrs):
                return tuple(attrs())
            return attrs
        with contextlib.suppress(AttributeError):
            return self._domain.frame
        return None

    #
    # Protected
    #

    def _create_operator(self, assemble: bool) -> None:
        expr = self._expression
        dom = self._domain

        # If the domain uses a frame (e.g. if in create_lambda() the argument
        # 'variables' is given) create a mapping from the field identifiers
        # within the frame to valid variable names.
        var = self._get_variables(expr, dom.frame)

        # If the
        if var.components:
            pass

        # def repl(mo) -> str:
        #     if mo.group('var')
        #     ...
        # repl: AnyOp = lambda mo: 'x' if mo.group('var') else mo.group('text')
        # re_str = '"[^"]+"'
        # re_var = re.escape(var)
        # pattern = f"(?P<str>{re_str})|(?P<var>{re_var})"
        # new_expr = re.sub(pattern, repl, string)
        # get_var: AnyOp = lambda obj: obj.group('var')
        # while any(map(get_var, re.finditer(pattern, expr)))

        # Parse Expression
        parser = py_expression_eval.Parser()
        valid_expression = self._get_valid_expression()
        expr = parser.parse(valid_expression).simplify({})

        # Create Mapper
        names = tuple(expr.variables())
        dom_type = self._domain.type
        dom_frame = var.fields or names
        dom_like = (dom_type, dom_frame)
        mapper: AnyOp
        if assemble:
            if dom_type == list:
                mapper = Identity()
            else:
                mapper = Mapper(*names, domain=dom_like, target=list)
        else:
            if dom_type == dict:
                mapper = Identity()
            else:
                mapper = Mapper(*names, domain=dom_like, target=dict)

        # If the term is trusted create and compile lambda term. Note, that the
        # lambda term usually may be considered to be a trusted expression, as
        # it has been created by using the expression parser
        if assemble:
            term = expr.toString().replace('^', '**')
            term = f"lambda {','.join(names)}:{term}"
            compiled = eval(term) # pylint: disable=W0123
            runner: AnyOp = lambda x: compiled(*x)
            self._operator = compose(runner, mapper)
            self._domain = stype.create_domain((dom_type, tuple(names)))
        else:
            self._operator = compose(expr.evaluate, mapper)
            setattr(self._operator, 'variables', expr.variables)

    def _get_variables(self, expr: str, frame: Frame) -> Mapper:
        if not frame:
            return Mapper()

        # Create an operator that checks, if a given variable name <var> is
        # already occupied by the expression. Thereby ignore appearances within
        # quoted (single or double) terms.
        expr = self._expression
        quoted = "\"[^\"]+\"|'[^']+'" # RegEx for quoted terms
        raw = quoted + "|(?P<var>{var})" # Unformated RegEx for matches
        matches: AnyOp = lambda var: re.finditer(raw.format(var=var), expr)
        hit: AnyOp = lambda obj: obj.group('var') # Test if match is a var
        occupied: AnyOp = lambda var: any(map(hit, matches(var)))

        # Use the operator to create a field mapping from the set of field IDs
        # in the frame to valid variable names.
        fields = set(frame)
        mapping: Dict[FieldID, str] = {}
        var_counter = itertools.count()
        next_var: AnyOp = lambda: 'X{i}'.format(i=next(var_counter))
        var_name = next_var()
        for field in fields:
            if isinstance(field, str) and field.isidentifier():
                mapping[field] = field
                continue
            while occupied(var_name):
                var_name = next_var()
            mapping[field] = var_name

        # Create variable
        get_var: AnyOp = lambda field: mapping.get(field, '')
        args = tuple(zip(frame, map(get_var, frame)))

        return Mapper(*args)

    def _get_valid_expression(self) -> str:
        expr = self._expression
        frame = self._domain.frame
        variables = self._get_variables(expr, frame).components
        for orig, subst in zip(frame, variables):
            if orig == subst:
                continue
            expr = expr.replace(str(orig), subst)
        return expr

#
# Operator Builders
#

@functools.lru_cache(maxsize=64)
def create_lambda(
        expression: str = '', domain: stype.DomLike = None,
        variables: OptStrTuple = None, default: OptOp = None,
        assemble: bool = True) -> Lambda:
    """Create a lambda operator.

    Args:
        expression:
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        variables: Optional tuple with variable names. This parameter is only
            required, if the domain category is a subclass of the
            :class:`Sequence class <collection.abs.Sequence>`. In this case the
            variable names are used to map the fields (given as names) to their
            indices within the domain tuple.
        default:
        assemble: Optional Boolean parameter, which determines if the operator
            is compiled after it is parsed.

    Returns:

    """
    domain = stype.create_domain(domain, defaults={'fields': variables})
    return Lambda(
        expression=expression, domain=domain, default=default,
        assemble=assemble)

#
# Operator Inspection Functions
#

def get_parameters(
        op: AnyOp, *args: Any, **kwds: Any) -> collections.OrderedDict:
    """Get parameters of an operator.

    Args:
        op: Callable object
        *args: Arbitrary arguments, that are zipped into the returned
            parameter dictionary.
        **kwds: Arbitrary keyword arguments, that respectively - if declared
            within the callable object - are merged into the returned parameter
            dictionary. If the callable object allows a variable number of
            keyword arguments, all given keyword arguments are merged into the
            parameter dictionary.

    Returns:
        Ordered Dictionary of parameters.

    Examples:
        >>> get_parameters(get_parameters)
        OrderedDict()
        >>> get_parameters(get_parameters, list)
        OrderedDict([('operator', list)])

    """
    # Get all arguments
    spec = inspect.getfullargspec(op)
    spec_args = spec.args
    spec_defaults = spec.defaults or []
    args_list = list(zip(spec_args, args))

    # Update Defaults
    args_keys = dict(args_list).keys()
    defaults_list = list(zip(spec_args, spec_defaults[::-1]))[::-1]
    for key, val in defaults_list:
        if key not in args_keys:
            args_list.append((key, val))
    params = collections.OrderedDict(args_list)

    # Update Keyword Arguments
    if spec.varkw:
        params.update(kwds)
    else:
        for key, val in kwds.items():
            if key in spec.args:
                params[key] = val

    # TODO: Split parameters in args and kwds
    return params

def parse_call(text: str) -> Tuple[str, tuple, dict]:
    """Split an function call in the function name, it's arguments and keywords.

    Args:
        text: Function call given as valid Python code.

    Returns:
        A tuple consisting of the function name as string, the arguments as
        tuple and the keywords as dictionary.

    """
    # Get function name
    try:
        tree = ast.parse(text)
        obj = getattr(tree.body[0], 'value')
        name = getattr(getattr(obj, 'func'), 'id')
    except SyntaxError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err
    except AttributeError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err

    # Get Arguments
    args = []
    for ast_arg in getattr(obj, 'args'):
        typ = ast_arg._fields[0]
        val = getattr(ast_arg, typ)
        args.append(val)

    # Get Keyword Arguments
    kwds = []
    for ast_kwd in getattr(obj, 'keywords'):
        typ = ast_kwd.value._fields[0]
        key = ast_kwd.arg
        val = getattr(ast_kwd.value, typ)
        kwds.append((key, val))

    return name, tuple(args), dict(kwds)

#
# Operators that act on Operators
#

def compose(*args: OptOp, unpack: bool = False) -> AnyOp:
    """Compose operators.

    Args:
        *args: Operators, which shall be composed. If provided, any given
            operator is required to be a callable or None.

    Returns:
        Composition of all arguments, that do not evaluate to False. If all
        arguments evaluate to False, the identity operator is returned.

    """
    # Check type of arguments
    if not all(map(lambda arg: arg is None or callable(arg), args)):
        raise InvalidTypeError('every argument', args, 'callable or None')

    # Filter all arguments which evaluate to False. This includes None and the
    # identity operator, since len(Identity()) == 0. If no arguments pass the
    # filter, the the default operator given by the identity is used.
    ops = tuple(filter(None, args)) or (Identity(), )

    # Create pairwise composition operator and apply it to the remaining
    # arguments
    circ: AnyOp
    if unpack:
        circ = lambda f, g: lambda *p: f(*g(*p))
    else:
        circ = lambda f, g: lambda *p: f(g(*p))
    return functools.reduce(circ, ops)

def evaluate(op: AnyOp, *args: Any, **kwds: Any) -> Any:
    """Evaluate operator for given parameter values.

    Securely evaluates an operator for the subset of given parameters, which is
    known to the operators signature.

    Args:
        operator: Callable object
        *args: Arbitrary arguments
        **kwds: Arbitrary keyword arguments

    """
    return op(**get_parameters(op, *args, **kwds))

#
# Builders for elementary operators
#

def create_setter(*args: Item, domain: stype.DomLike = object) -> AnyOp:
    """Create a setter operator.

    Args:
        *args: Optional pairs containing field values. If provided, the pairs
            have to be given in the format `(<field>, <value>)`, where `<field>`
            is a valid :term:`field identifier` within the domain type and
            `<value>` an arbitrary object.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. Supported
            domain types are :class:`object`, subclasses of the class:`Mapping
            class <collection.abs.Mapping>` and subclasses of the
            :class:`Sequence class <collection.abs.Sequence>`. If no domain type
            is specified (which is indicated by the default value None) the
            returned operator ir the zero operator.

    """
    # If no field-value pairs are specified, the returned operator is the zero
    # operator.
    if not args:
        return Zero()

    # Get domain
    domain = stype.create_domain(domain)

    # Create attribute setter
    if domain.type == object:
        # TODO: check if field names are identifiers
        # check.has_iterable_type(...)
        if len(args) == 1:
            name, val = args[0]
            return lambda obj: setattr(obj, name, val) # type: ignore
        def attrsetter(obj: object) -> None:
            set_item = lambda item: setattr(obj, *item)
            iterator = map(set_item, args) # type: ignore
            collections.deque(iterator, maxlen=0) # avoid creation of list
        return attrsetter

    # Create item setter for mappings
    if issubclass(domain.type, Mapping):
        # For mappings use the .update() method
        updates = dict(args)
        return lambda obj: obj.update(updates)

    # Create item setter for sequences
    if issubclass(domain.type, Sequence):
        if domain.frame: # If a frame is given get the item positions from index
            getid = domain.frame.index
            items = tuple((getid(arg[0]), arg[1]) for arg in args)
        else:
            items = tuple((int(arg[0]), arg[1]) for arg in args) # type: ignore
        def setitems(seq: Sequence) -> None:
            for key, val in items:
                seq[key] = val # type: ignore
        return setitems

    # TODO: Use some kind of ValueEror for domain!
    raise InvalidTypeError(
        'domain type', domain.type, (object, Mapping, Sequence))

def create_formatter(*args: FieldID, target: stype.DomLike = None) -> AnyOp:
    """Create a formatter operator.

    Args:
        *args: Valid :term:`field identifiers <field identifier>` within the
            target type.
        target: Optional :term:`domain like` parameter, that specifies the
            type and (if required) the frame of the operator's target. Supported
            target types are :class:`tuple`, :class:`list` and :dict:'dict'. If
            no target is specified (which is indicated by the default value
            None) the target type depends on the arguments, that are passed to
            the operator. In this case for a single argument, the target type
            equals the type of the argument and for multiple argumnts, the
            target type is tuple.

    Returns:
        Operator that represents fields, ether given as a non-tuple argument
        for a single field or a tuple argument for multiple fields, in a given
        target type.

    """
    debuginfo = (args, target)

    # Get target
    target = stype.create_domain(target, defaults={'fields': args})

    # Create formatter
    if target.type == NoneType:
        return Identity()
    if target.type == tuple:
        return lambda x: x if isinstance(x, tuple) else (x, )
    if target.type == list:
        return lambda x: list(x) if isinstance(x, tuple) else [x]
    if target.type == dict:
        frame = target.frame
        if not frame:
            raise ValueError(
                "target type 'dict' requires, that a frame is given")
        first = frame[0]
        d1: AnyOp = lambda x: {first: x} # arg -> dict
        dn: AnyOp = lambda x: dict(zip(frame, x)) # args -> dict
        return lambda x: dn(x) if isinstance(x, tuple) else d1(x)

    # TODO: raise InvalidValueError!
    raise InvalidTypeError('target type', target.type, (tuple, list, dict))

def create_wrapper(**attrs: Any) -> AnyOp:
    """Create a function wrapper that adds attributes.

    Args:
        **attrs: Arbitrary keyword arguments

    Returns:
        Function wrapper for given function, with additional specified
        attributes.

    """
    def wrapper(op): # type: ignore
        def meth(self, *args, **kwds): # type: ignore
            return op(*args, **kwds)
        def func(*args, **kwds): # type: ignore
            return op(*args, **kwds)
        caller = meth if isinstance(op, Method) else func
        caller.__dict__.update(attrs)
        caller.__doc__ = op.__doc__
        return caller
    return wrapper

#
# Factory functions for sequence operators
#

def create_sorter(
        *args: FieldID, domain: stype.DomLike = None,
        reverse: bool = False) -> SeqHom:
    """Create a sorter with fixed sorting keys.

    Sorters are operators, that act on sequences of objects of a given category
    and change the order of the objects within the sequence.

    Args:
        *args: Optional *sorting keys*, which in hierarchically descending order
            are used to sort sequences of objects of given domain type. If
            provided, any sorting key is required to be a valid :term:`field
            identifier` for the domain type.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in the class :class:`Projection`.
        reverse: Optional boolean parameter. If set to True, then the sequence
            elements are sorted as if each comparison were reversed.

    Returns:
        Callable function which sorts a sequence of objects of a given domain by
        given sorting keys.

    """
    # Create getter operator for given keys
    getter = Projection(*args, domain=domain) if args else None

    # Create and return sorting operator
    return lambda seq: sorted(seq, key=getter, reverse=reverse)

def create_grouper(
        *args: FieldID, domain: stype.DomLike = None,
        presorted: bool = False) -> SeqOp:
    """Create a grouping operator with fixed grouping keys.

    Args:
        *args: Optional *grouping keys*, which are used to group sequences of
            objects of given domain type. If provided, any grouping key is
            required to be a valid :term:`field identifier` for the domain type.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in the class :class:`Projection`.
        presorted: The grouping operation splits in two consecutive steps: In
            the first step the input sequence is sorted by the given keys.
            Thereupon in the second step the sorted sequence is partitioned in
            blocks, which are equal with respect to the keys. Consequently if
            the sequences are already sorted, the first step is not required and
            can be omitted to increase the performance of the operator. By
            default the input sequences are assumed not to be presorted.

    Returns:
        List of sequences containing objects of a given domain typr, which are
        equal with respect to given grouping keys.

    """
    # The default grouper groups all sequence elements into a single group
    if not args:
        return lambda seq: [seq]

    # Create getter for given keys
    getter = Projection(*args, domain=domain)

    # Create list mapper for groups
    group = operator.itemgetter(1)
    mapper: SeqOp = lambda gseq: list(map(list, map(group, gseq)))

    # Create grouper for sorted sequences
    grouper: SeqOp = lambda seq: mapper( # type: ignore
        itertools.groupby(seq, key=getter))
    if presorted:
        return grouper

    # Create grouper for unsorted sequences
    return lambda seq: grouper(sorted(seq, key=getter))

def create_aggregator(
        *args: VarLike, domain: stype.DomLike = None,
        target: type = tuple) -> SeqOp:
    """Creates an aggregation operator with specified variables.

    Args:
        *args: Optional :term:`variable definitions<variable definition>`. If
            provided the operators given within the variable definitions are
            required to be valid :term:`aggregation functions <aggregation
            function>`
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        target: Optional target category of the operator. If provided, the
            category has to be given as a type. Supported types are
            :class:`tuple` and :dict:'dict'. If no target type is specified, the
            target category of the operator depends on the domain. In this case
            for the domain *object*, the target type is documented by the the
            builtin function :func:`~operator.attrgetter`, for other domains by
            the function :func:`~operator.itemgetter`.

    Return:

    """
    # The default operator is the zero operator (in the target type)
    if not args:
        return Zero(target)

    # Create mapper object
    f = Mapper(*args, default=operator.itemgetter(0))

    # Create an operator, that converts data stored in rows to columns.
    # 1. At first fetch the rows from the input sequence
    # 2. Create a Matrix from the sequence (a list of rows)
    # 3. Transpose a Matrix (to a tuple of columns)
    # 4. Compose Matrix creation and transposition
    fetch = Projection(*f.fields, domain=domain, target=tuple)
    matrix: SeqOp = lambda seq: list(map(fetch, seq))
    trans: SeqOp = lambda mat: tuple(list(col) for col in zip(*mat))
    columns: SeqOp = lambda seq: trans(matrix(seq))

    # If the requested type is tuple return an operator, that evaluates the
    # multivariate variable for the columns
    if target == tuple:
        return lambda seq: f(*columns(seq))

    # For dictionaries a further type conversion is required
    if target == dict:
        components = f.components
        return lambda seq: dict(zip(components, f(*columns(seq))))

    raise ValueError(f"type '{target.__name__}' is not supported")

def create_group_aggregator(
        *args: VarLike, key: Key = None, domain: stype.DomLike = None,
        target: type = tuple, presorted: bool = False) -> SeqOp:
    """Creates a group aggregation operator.

    Args:
        *args: Optional :term:`variable definitions<variable definition>`. If
            provided the operators given within the variable definitions are
            required to be valid :term:`aggregation functions <aggregation
            function>`. If not provided, the returned operator is the identity.
        key: Optional grouping key. If provided, the grouping key can be a
            :term:`field identifier` or a composite key, given by a tuple of
            field identifiers. Thereby the type and the concrete meaning of the
            field identifiers depends on the domain of the operator.
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        target: Optional target category of the operator. If provided, the
            category has to be given as a type. Supported types are
            :class:`tuple` and :dict:'dict'. If no target type is specified, the
            target category of the operator depends on the domain. In this case
            for the domain *object*, the target type is documented by the the
            builtin function :func:`~operator.attrgetter`, for other domains by
            the function :func:`~operator.itemgetter`.
        target: Optional target type of the operator. Supported types are
            :class:`tuple` and :dict:'dict'. If no target type is specified, the
            target of the operator depends on the domain. In this caser for the
            domain object, the target type is documented by the the builtin
            function :func:`~operator.attrgetter`, for other domains by the
            function :func:`~operator.itemgetter`.
        presorted: The operation splits in three consecutive steps, where in
            the first step the input sequence is sorted by the given keys.
            Consequently if the sequences are already sorted, the first step is
            not required and can be omitted to increase the performance of the
            operator. By default the input sequences are assumed not to be
            presorted.

    Returns:

    """
    # Group aggregators require variable definitions
    if not args:
        return Identity(domain=domain)

    # Create Grouper
    if key is None:
        group = create_grouper() # Trivial grouper
    elif isinstance(key, tuple):
        group = create_grouper(*key, domain=domain, presorted=presorted)
    elif isinstance(key, Hashable):
        group = create_grouper(key, domain=domain, presorted=presorted)

    # Create Aggregator
    contract = create_aggregator(*args, domain=domain, target=target)

    # Map Aggregator to Groups
    return lambda seq: map(contract, group(seq))
