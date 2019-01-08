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
import py_expression_eval
from nemoa.base import literal
from nemoa.errors import InvalidTypeError
from nemoa.types import Any, Method, Mapping, Sequence, NoneType
from nemoa.types import Tuple, OptType, SeqHom, SeqOp, AnyOp, Hashable, Union
from nemoa.types import Optional, OptOp, BoolOp, StrList, Class

#
# Types and ClassInfos
#

# Expression
Expr = Any # TODO: Use py_expression_eval.Expression

# Field identifiers
FieldID = Hashable # <field>
FieldIDs = Tuple[FieldID, ...] # <fields>
OptFieldIDs = Optional[FieldIDs]
OptKey = Optional[Union[FieldID, FieldIDs]]
Item = Tuple[FieldID, Any] # <field>, <value>

# Field Variables
VarDefA = Tuple[FieldID] # <field>
VarDefB = Tuple[FieldID, FieldID] # id: <field> -> <variable>
VarDefC = Tuple[FieldID, AnyOp] # <operator>: <field> -> <field>
VarDefD = Tuple[FieldID, AnyOp, FieldID] # <operator>: <field> -> <variable>
FieldVar = Union[FieldID, VarDefA, VarDefB, VarDefC, VarDefD]

# Domains
DomLike = Union[OptType, Tuple[OptType, FieldIDs]]

#
# Parameter Classes
#

class Domain:
    """Class for the storage of domain parameters.

    Args:
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of a domain.
        default_type: Optional parameter, that specifies the default domain type
            which is used if no type is given within the argument `domain`. If
            provided, the argument has to be given as a :class:`type`.
        default_frame: Optional parameter, that specifies the default domain
            frame which is used if no frame is given within the argument
            `domain`. If provided, the argument has to be given as a
            :class:`tuple`.

    """
    __slots__ = ['type', 'frame']

    type: Class
    frame: tuple

    def __init__(
        self, domain: DomLike = None, default_type: Class = NoneType,
        default_frame: OptFieldIDs = None) -> None:
        if domain is None:
            self.type = default_type
            self.frame = default_frame or tuple()
        elif isinstance(domain, type):
            self.type = domain
            self.frame = default_frame or tuple()
        elif isinstance(domain, tuple):
            self.type = domain[0] or default_type
            self.frame = domain[1] or default_frame or tuple()

    def __repr__(self) -> str:
        name = type(self).__name__
        dtype = self.type.__name__
        frame = ', '.join(map(str, self.frame))
        if not frame:
            return f"{name}({dtype})"
        return f"{name}({dtype}, frame={frame})"

class FieldMap:
    """Class for the storage of field mapping parameters.

    Args:
        *args: Definitions of :term:`field variables <field variable>`.
        default: Default operator which is used to map fields to field
            variables. By default the identity is used.

    """
    __slots__ = ['fields', 'operators', 'variables']

    fields: FieldIDs
    operators: Tuple[AnyOp, ...]
    variables: tuple

    def __init__(self, *args: FieldVar, default: OptOp = None) -> None:
        if not args:
            self.fields = tuple()
            self.operators = tuple()
            self.variables = tuple()
            return

        # Set default values
        default = default or identity

        # Get list of parameters
        params: list = []
        for fvar in args:
            if isinstance(fvar, tuple):
                size = len(fvar)
                if size == 1:
                    params.append((fvar[0], default, fvar[0]))
                    continue
                if size == 2:
                    if callable(fvar[1]):
                        params.append((fvar[0], fvar[1], fvar[0]))
                        continue
                    params.append((fvar[0], default, fvar[1]))
                    continue
                params.append((fvar[0], fvar[1], fvar[2]))
                continue
            if isinstance(fvar, Hashable):
                params.append((fvar, default, fvar))
                continue
            raise InvalidTypeError(
                'field variable definition', fvar, (Hashable, tuple))

        par = tuple(zip(*params))
        self.fields = par[0]
        self.operators = par[1]
        self.variables = par[2]

#
# Operator Classes
#

class Operator(collections.abc.Callable): # type: ignore
    """Base Class for operators."""

    _domain: Domain
    _target: Domain

    @property
    def domain(self) -> Domain:
        if hasattr(self, '_domain'):
            return self._domain
        return Domain()

    @property
    def target(self) -> Domain:
        if hasattr(self, '_target'):
            return self._target
        return Domain()

class Identity(Operator):
    """Class for identity operators."""
    _require: int

    def __init__(self, *args: FieldID) -> None:
        self._domain = Domain(default_frame=args)
        self._target = Domain(default_frame=args)
        self._require = len(args) if args else 0

    def __call__(self, *args: Any) -> Any:
        if self._require:
            args_require = self._require
            args_given = len(args)
            if args_given != args_require:
                name = type(self).__name__
                arg = "argument" if args_require == 1 else "arguments"
                was = "was" if args_given == 1 else "were"
                raise TypeError(
                    f"{name} takes {args_require} positional {arg} "
                    f"but {args_given} {was} given")
        if not args:
            return None
        if len(args) == 1:
            return args[0]
        return args

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        name = type(self).__name__
        frame = self._domain.frame
        if not frame:
            return f'{name}()'
        return f"{name}({', '.join(map(str, frame))})"

class Zero(Operator):
    """Class for zero operators.

    Args:
        target:

    """
    _zero: Any

    def __init__(self, target: DomLike = None) -> None:
        self._domain = Domain()
        self._target = Domain(target)
        self._zero = self._target.type() # Create zero object in target type

    def __call__(self, *args: Any) -> Any:
        return self._zero

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        name = type(self).__name__
        target = self._target.type.__name__
        return f"{name}({target})"

class Lambda(Operator):
    """Class for operators, that are based on parsed expressions.

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
        trusted:

    """
    _expression: str
    _operator: Any # Usage of Callable leads to wrong interpretation by mypy

    def __init__(
            self, expression: str = '', domain: DomLike = None,
            default: OptOp = None, trusted: bool = True) -> None:
        self._expression = expression
        self._domain = Domain(domain)

        if expression:
            parser = py_expression_eval.Parser()
            valid_expression = self._get_valid_expression()
            expr = parser.parse(valid_expression).simplify({})
            if trusted:
                self._compile_operator(expr, domain)
            else:
                self._bind_operator(expr, domain)
        elif callable(default):
            self._operator = default
        else:
            self._operator = create_zero()

    def __call__(self, *args: Any) -> Any:
        return self._operator(*args)

    def __repr__(self) -> str:
        with contextlib.suppress(AttributeError):
            return f"{type(self).__name__}('{self._expression}')"
        with contextlib.suppress(AttributeError):
            return repr(self._operator)
        return f"{type(self).__name__}()"

    #
    # Public
    #

    @property
    def variables(self) -> FieldIDs:
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

    def _bind_operator(self, expr: Expr, domain: DomLike = None) -> None:
        names = expr.variables()
        variables = self._get_valid_variables() or names # Set default values
        ops = [expr.evaluate]
        if domain is not dict:
            ops.append(create_mapper(
                *names, domain=(domain, variables), target=dict))
        self._operator = compose(*ops)
        setattr(self._operator, 'variables', expr.variables)

    def _compile_operator(self, expr: Expr, domain: DomLike = None) -> None:
        names = expr.variables()
        variables = self._get_valid_variables() or names # Set default values
        string = expr.toString().replace('^', '**')
        command = f"lambda {','.join(names)}:{string}"
        # Note, that the command is a trusted expression, as it has been
        # created by using the expression parser
        compiled = eval(command) # pylint: disable=W0123
        ops = [lambda obj: compiled(*obj)]
        if domain is not tuple:
            ops.append(create_mapper(
                *names, domain=(domain, variables), target=tuple))
        self._operator = compose(*ops)
        self._domain.frame = tuple(names)

    def _get_valid_variables(self) -> StrList:
        variables = self._domain.frame
        if not variables:
            return []
        # Substitute Variables names
        # TODO: Enforce unique names!!!
        convert = lambda var: literal.encode(var, charset='UAX31', spacer='_')
        return list(map(convert, variables))

    def _get_valid_expression(self) -> str:
        expr = self._expression
        variables = self._domain.frame
        valid_variables = self._get_valid_variables()
        for orig, subst in zip(variables, valid_variables):
            if orig == subst:
                continue
            expr = expr.replace(orig, subst)
        return expr

#
# Operator Constructors
#

@functools.lru_cache(maxsize=32)
def create_identity(*args: FieldID) -> Identity:
    """Create identity operator."""
    return Identity(*args)

@functools.lru_cache(maxsize=8)
def create_zero(target: DomLike = None) -> AnyOp:
    """Create a zero operator.

    Args:
        target: Optional target category of the operator. If provided, the
            target category must by given as a :class:`type`, like
            :class:`int`, :class:`float`, :class:`str`, :class:`set`,
            :class:`tuple`, :class:`list`, :class:`dict` or :class:`object`.
            Then the returned operator maps all objects of any domain category
            to the zero object of the target category. By default the used zero
            object is None.

    Returns:
        Operator, that maps given arguments to the zero object of a given target
        type.

    """
    return Zero(target)

#
# Operator Constants
#

identity = create_identity()
zero = create_zero()



@functools.lru_cache(maxsize=64)
def create_lambda(
        expression: str = '', domain: DomLike = None,
        default: OptOp = None, trusted: bool = True) -> Lambda:
    """Create a lambda operator.

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
        trusted:

    Returns:

    """
    return Lambda(
        expression=expression, domain=domain, default=default, trusted=trusted)

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

def compose(*args: OptOp) -> AnyOp:
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
    # identity operator, since len(identity) == 0. If no arguments pass the
    # filter, retain the identity operator.
    ops = tuple(filter(None, args)) or (identity, )

    # Create and return composition of remaining arguments
    return functools.reduce(lambda f, g: lambda *p: f(g(*p)), ops)

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
# Factory functions for elementary operators
#

def create_getter(*args: FieldID, domain: DomLike = None) -> AnyOp:
    """Create a getter operator.

    This function uses the standard library module :mod:`operator` and returns
    an operator created by :func:`~operator.attrgetter`,
    :func:`~operator.itemgetter` or :func:`.create_identity`.

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

    Returns:
        Operator that retrieves specified fields from its operand and returns
        them as a single object for a single specified field or a tuple for
        multiple specified fields.

    """
    # If no fields are specified, the returned operator is the zero operator. If
    # fields are specified, but no domain is specified the returned operator is
    # the argument getter for the specified fields.
    if not args:
        return zero
    if not domain:
        return create_identity(*args) # TODO: create argument getter

    # Get domain
    dom = Domain(domain, default_frame=args)

    # Create getter
    if dom.type is NoneType:
        return identity # TODO: create argument getter
    validate: AnyOp
    if dom.type is object:
        # Check if field identifiers are attribute identifiers
        validate = lambda obj: isinstance(obj, str) and str.isidentifier
        if not all(map(validate, args)):
            raise InvalidTypeError('any field', args, 'an identifier')
        return operator.attrgetter(*args) # type: ignore
    if issubclass(dom.type, Mapping):
        # Check if field identifiers are mapping keys (hashable)
        validate = lambda obj: isinstance(obj, Hashable)
        if not all(map(validate, args)):
            raise InvalidTypeError('any field', args, 'hashable')
        return operator.itemgetter(*args)
    if issubclass(dom.type, Sequence):
        if dom.frame:
            getid = dom.frame.index
            return operator.itemgetter(*map(getid, args))
        # Check if field identifiers are sequence positions
        validate = lambda obj: isinstance(obj, int) and obj >= 0
        if not all(map(validate, args)):
            raise InvalidTypeError('any field', args, 'positive integer')
        return operator.itemgetter(*args)

    # TODO: raise InvalidValueError!
    raise InvalidTypeError('domain', domain, (object, Mapping, Sequence))

def create_setter(*args: Item, domain: DomLike = object) -> AnyOp:
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
        return zero

    # Get domain
    dom = Domain(domain)

    # Create setter
    if dom.type is object:
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
    if issubclass(dom.type, Mapping):
        # For mappings use the .update() method
        updates = dict(args)
        return lambda obj: obj.update(updates)
    if issubclass(dom.type, Sequence):
        if dom.frame: # If a frame is given get the item positions from index
            getid = dom.frame.index
            items = tuple((getid(arg[0]), arg[1]) for arg in args)
        else:
            items = tuple((int(arg[0]), arg[1]) for arg in args) # type: ignore
        def setitems(seq: Sequence) -> None:
            for key, val in items:
                seq[key] = val # type: ignore
        return setitems

    # TODO: Use some kind of ValueEror for domain!
    raise InvalidTypeError('domain', domain, (object, Mapping, Sequence))

def create_formatter(*args: FieldID, target: DomLike = None) -> AnyOp:
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
    # Get target
    tgt = Domain(target, default_frame=args)

    # Create formatter
    if tgt.type is NoneType:
        return create_identity('x')
    if tgt.type is tuple:
        return lambda x: x if isinstance(x, tuple) else (x, )
    if tgt.type is list:
        return lambda x: list(x) if isinstance(x, tuple) else [x]
    if tgt.type is dict:
        frame = tgt.frame
        if not frame:
            raise ValueError() # TODO: ...
        first = frame[0]
        d1: AnyOp = lambda x: {first: x} # arg -> dict
        dn: AnyOp = lambda x: dict(zip(frame, x)) # args -> dict
        return lambda x: dn(x) if isinstance(x, tuple) else d1(x)

    # TODO: raise InvalidValueError!
    raise InvalidTypeError('target', target, (tuple, list, dict))

def create_mapper(
        *args: FieldID, domain: DomLike = None,
        target: DomLike = None) -> AnyOp:
    """Create a mapping operator.

    Mapping operators are compositions of :func:`getters<create_getter>`
    and :func:`formatters<create_formatter>` and used to map selected fields
    from it's operand (or arguments) to the fields of a given target type.

    Args:
        *args: Valid :term:`field identifiers <field identifier>` within the
            domain type.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in :func:`create_getter`.
        target: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's target. The accepted
            parameter values are documented in :func:`create_formatter`.

    Returns:
        Operator that maps selected fields from its operand to fields of a
        given target type.

    """
    # If no fields are specified, the returned operator is the zero operator of
    # the target type. If fields are specified, but no domain and no target the
    # returned operator is the identity with a fixed number of arguments
    if not args:
        return create_zero(target)
    if not (domain or target):
        return create_identity(*args)

    # Create a getter with given domain and a formatter with given target
    getter = create_getter(*args, domain=domain)
    formatter = create_formatter(*args, target=target)

    # If the formatter is an identity operator, return getter. If the getter is
    # an identity operator, precede a 'boxing' operation.
    if isinstance(formatter, Identity):
        return getter
    if isinstance(getter, Identity):
        return compose(formatter, lambda *args: args)

    return compose(formatter, getter)

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
        *args: FieldID, domain: DomLike = None,
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
            parameter values are documented in :func:`create_getter`.
        reverse: Optional boolean parameter. If set to True, then the sequence
            elements are sorted as if each comparison were reversed.

    Returns:
        Callable function which sorts a sequence of objects of a given domain by
        given sorting keys.

    """
    # Create getter operator for given keys
    getter = create_getter(*args, domain=domain) if args else None

    # Create and return sorting operator
    return lambda seq: sorted(seq, key=getter, reverse=reverse)

def create_grouper(
        *args: FieldID, domain: DomLike = None,
        presorted: bool = False) -> SeqOp:
    """Create a grouping operator with fixed grouping keys.

    Args:
        *args: Optional *grouping keys*, which are used to group sequences of
            objects of given domain type. If provided, any grouping key is
            required to be a valid :term:`field identifier` for the domain type.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in :func:`create_getter`.
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
    getter = create_getter(*args, domain=domain)

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
        *args: FieldVar, domain: DomLike = None,
        target: type = tuple) -> SeqOp:
    """Creates an aggregation operator with specified field variables.

    Args:
        *args: Definitions of :term:`field variables <field variable>`.
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
    # The default operator is the zero operator (in the target category)
    if not args:
        return create_zero(target)

    # Split field variable parameters
    fmap = FieldMap(*args, default=operator.itemgetter(0))
    ops = fmap.operators

    # Create a getter, that maps the input sequence to a matrix
    getter = create_mapper(*fmap.fields, domain=domain, target=tuple)
    matrix: SeqOp = lambda seq: list(map(getter, seq))

    # Create operators, that transpose the matrix and aggregate the columns
    trans: SeqOp = lambda mat: tuple(list(col) for col in zip(*mat))
    aggreg: SeqOp = lambda arr: tuple(op(seq) for op, seq in zip(ops, arr))

    # If the requested type is tuple just compose the operators
    if target == tuple:
        return lambda seq: aggreg(trans(matrix(seq)))

    # For dictionaries a further type conversion is required
    if target == dict:
        names = fmap.variables
        return lambda seq: dict(zip(names, aggreg(trans(matrix(seq)))))

    raise ValueError(f"type '{target.__name__}' is not supported")

def create_group_aggregator(
        *args: FieldVar, key: OptKey = None, domain: DomLike = None,
        target: type = tuple, presorted: bool = False) -> SeqOp:
    """Creates a group aggregation operator.

    Args:
        *args: Definitions of :term:`field variables <field variable>`.
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
    # Group aggregators require field variables
    if not args:
        return identity

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
