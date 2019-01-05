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
from nemoa.errors import InvalidTypeError, NotCallableError
from nemoa.types import Any, OrderedDict, Method, Mapping, Sequence
from nemoa.types import Tuple, OptType, SeqHom, SeqOp, AnyOp, Hashable, Union
from nemoa.types import Optional, OptOp, BoolOp, StrIter, OptStrIter, StrList

#
# Structural Types
#

# Parser Expression
ExprType = py_expression_eval.Expression

# Predicate
PredLike = Optional[Union[str, BoolOp]]

# Field identifiers
FieldID = Hashable # <field>
FieldIDs = Tuple[FieldID, ...] # <fields>
OptFieldIDs = Optional[FieldIDs]
OptKey = Optional[Union[FieldID, FieldIDs]]
Item = Tuple[FieldID, Any] # <field>, <value>

# Field variables
VarDefA = Tuple[FieldID] # <field>
VarDefB = Tuple[FieldID, FieldID] # id: <field> -> <variable>
VarDefC = Tuple[FieldID, AnyOp] # <operator>: <field> -> <field>
VarDefD = Tuple[FieldID, AnyOp, FieldID] # <operator>: <field> -> <variable>
VarDef = Union[FieldID, VarDefA, VarDefB, VarDefC, VarDefD]
VarsParams = Tuple[tuple, tuple, tuple]

# Categories
CatA = OptType
CatB = Tuple[OptType, FieldIDs]
Cat = Union[CatA, CatB]

#
# Generic Operator Classes
#

OperatorBase = collections.abc.Callable

class Identity(OperatorBase): # type: ignore
    """Class for universal identity operator."""

    _variables: OptFieldIDs

    def __init__(self, *variables: FieldID) -> None:
        self._variables = variables

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
        with contextlib.suppress(AttributeError):
            args = ', '.join(self._variables) # type: ignore
            return f"{name}({args})"
        return f'{name}()'

    #
    # Public
    #

    @property
    def variables(self) -> OptFieldIDs:
        with contextlib.suppress(AttributeError):
            return self._variables
        return None

@functools.lru_cache(maxsize=32)
def create_identity(*variables: FieldID) -> Identity:
    """Create identity operator with a fixed or variable number of arguments."""
    if not variables:
        return Identity()

    # If arguments are given, use them as argument names for the signature of
    # a new __call__ method
    op: AnyOp
    if len(variables) == 1:
        op = lambda self, arg: arg
    else:
        op = lambda self, *args: args
    new_cls = type(Identity.__name__, (Identity,), {'__call__': op})
    return new_cls(*variables)

identity = create_identity()

class Zero(OperatorBase): # type: ignore
    """Class for zero operators."""

    def __init__(self, target: OptType = None) -> None:
        if isinstance(target, type):
            self.zero = target() # Create zero object in target category
            self.target = target.__name__
        else:
            self.zero = None
            self.target = type(None).__name__

    def __call__(self, *args: Any) -> Any:
        return self.zero

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{type(self).__name__}({type(self.zero).__name__})"

@functools.lru_cache(maxsize=8)
def create_zero(target: OptType = None) -> AnyOp:
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
        Operator, that maps any argument to the zero object of a given target
        category.

    """
    return Zero(target)

class Lambda(OperatorBase): # type: ignore
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
        comp:

    """

    _expression: str
    _variables: StrIter
    _operator: AnyOp

    def __init__(
            self, expression: str = '', domain: OptType = None,
            variables: OptStrIter = None, default: OptOp = None,
            comp: bool = False) -> None:
        self._expression = expression
        self._variables = variables or []

        if expression:
            parser = py_expression_eval.Parser()
            valid_expression = self._get_valid_expression()
            expr = parser.parse(valid_expression).simplify({})
            if comp:
                self._compile_operator(expr, domain)
            else:
                self._bind_operator(expr, domain)
        elif callable(default):
            self._operator = default # type: ignore
        else:
            self._operator = create_zero() # type: ignore

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
            attrs = self._operator.variables # type: ignore
            if callable(attrs):
                return tuple(attrs())
            return attrs
        with contextlib.suppress(AttributeError):
            return self._variables
        return None

    #
    # Protected
    #

    def _bind_operator(
            self, expr: ExprType, domain: OptType = None) -> None:
        names = expr.variables() # type: ignore
        variables = self._get_valid_variables() or names # Set default values
        ops = [expr.evaluate] # type: ignore
        if domain != dict:
            ops.append(create_mapper(
                *names, domain=(domain, variables), target=dict))
        self._operator = compose(*ops) # type: ignore
        self._operator.variables = expr.variables # type: ignore

    def _compile_operator(
            self, expr: ExprType, domain: OptType = None) -> None:
        names = expr.variables() # type: ignore
        variables = self._get_valid_variables() or names # Set default values
        string = expr.toString().replace('^', '**') # type: ignore
        command = f"lambda {','.join(names)}:{string}"
        compiled = eval(command) # pylint: disable=W0123
        ops = [lambda obj: compiled(*obj)]
        if domain != tuple:
            ops.append(create_mapper(
                *names, domain=(domain, variables), target=tuple))
        self._operator = compose(*ops) # type: ignore
        self._variables = tuple(names)

    def _get_valid_variables(self) -> StrList:
        variables = self._variables
        if not self._variables:
            return []
        # Substitute Variables names
        # TODO: Enforce unique names!!!
        convert = lambda var: literal.encode(var, charset='UAX31', spacer='_')
        return list(map(convert, variables))

    def _get_valid_expression(self) -> str:
        expr = self._expression
        variables = self._variables
        valid_variables = self._get_valid_variables()
        for orig, subst in zip(variables, valid_variables):
            if orig == subst:
                continue
            expr = expr.replace(orig, subst)
        return expr

@functools.lru_cache(maxsize=64)
def create_lambda(
        expression: str = '', domain: OptType = None,
        variables: OptStrIter = None, default: OptOp = None,
        comp: bool = False) -> Lambda:
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
        comp:

    Returns:

    """
    return Lambda(
        expression=expression, domain=domain, variables=variables,
        default=default, comp=comp)

#
# Operator Inspection Functions
#

def get_parameters(op: AnyOp, *args: Any, **kwds: Any) -> OrderedDict:
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
    params = OrderedDict(args_list)

    # Update Keyword Arguments
    if spec.varkw:
        params.update(kwds)
    else:
        for key, val in kwds.items():
            if key in spec.args:
                params[key] = val

    # TODO: Split parameters in args and kwds
    return params

def split_var_params(*args: VarDef, default: OptOp = None) -> VarsParams:
    """Split field variable definitions into variable parameters.

    Args:
        *args: Definitions of :term:`field variables <field variable>`.
        default: Default operator which is used to map fields to field
            variables. By default the identity is used.

    """
    if not args:
        return tuple(), tuple(), tuple()

    # Set default values
    default = default or identity

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

    return zip(*params) # type: ignore

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
        *args: Operators, which are to be composed. If provided, any given
            argument, which truthness evaluates to None is omitted.

    """
    ops = tuple(filter(None, args))
    if not ops:
        return identity
    for op in ops:
        if not callable(op):
            raise NotCallableError('operator', op)
    circ: AnyOp = lambda f, g: lambda *args: f(g(*args))
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
# Factory functions for elementary operators
#

def create_mapper(
        *fields: FieldID, domain: Cat = None, target: Cat = None) -> AnyOp:
    """Create a converter.

    Args:
        *fields: Valid :term:`field identifiers <field identifier>` within the
            domain category.
        domain: Optional parameter, that specifies the domain category of the
            operator. If provided, the category has to be given in one of the
            following formats: For categories / types, that support named fields
            (like :class:`object` or like :class:`dict`), the parameter has to
            be given by the format `<domain>`, where `<domain>` is a supported
            :class:`type` or None. For domains, however, that only support
            positional fields (like :class:`tuple` or :class:`list`), the
            conversion to a target category, with field names (e.g. the
            attributes of an object), requires to specify the field names. In
            this case the domain has to be given by the format `(<domain>,
            <variables>)`, where `<variables>` is a tuple of valid field
            identifiers in the category of the domain and used to map the field
            names to their positions. Supported types are :class:`object`,
            subclasses of the class:`Mapping class <collection.abs.Mapping>` and
            subclasses of the :class:`Sequence class <collection.abs.Sequence>`.
            The default value for `<domain>` is None. In this case the fields
            are taken from the positional arguments, that are passes to the
            operator.
        target: Optional parameter, that specifies the target category of the
            operator. If provided, the category has to be given in one of the
            following formats: For categories / types, that only support
            positional field identifiers (like :class:`tuple` or :class:`list`),
            the target category has to be given by the format `<target>`, where
            `<target>` is a supported :class:`type` or None. Supported types are
            :class:`tuple`, :class:`list` and :dict:'dict'. For domains,
            however, that support field names (like :class:`dict`), the used
            field names can be included within the specification. In this case
            the target category has to be given by the format `(<target>,
            <components>)`, where `<components>` is a tuple of valid field
            identifiers in the category of the target and used to map the
            variable names of the domain to component names of the target. If no
            target is specified, the target category of the operator depends on
            the domain. In this case for the domain *object*, the target type is
            documented by the the builtin function :func:`~operator.attrgetter`,
            for other domains by the function :func:`~operator.itemgetter`.

    Returns:
        Operator that maps selected fields from its operand to fields of a
        given target type.

    """
    # Split parameter 'domain' into category and variables
    domain_type: OptType
    domain_vars: tuple
    if domain is None or isinstance(domain, type):
        domain_type = domain
        domain_vars = fields
    elif isinstance(domain, tuple):
        domain_type = domain[0]
        domain_vars = domain[1]
    else:
        raise InvalidTypeError('domain', domain, (type, tuple))

    # Split parameter 'target' into category and variables
    target_type: OptType
    target_vars: tuple
    if target is None or isinstance(target, type):
        target_type = target
        target_vars = fields
    elif isinstance(target, tuple):
        target_type = target[0]
        target_vars = target[1]
    else:
        raise InvalidTypeError('target', target, (type, tuple))

    # The default mapper without given field names is the zero operator of the
    # target category. For given field names it is the projection to the fields
    if not fields:
        return create_zero(target_type)
    if not (domain_type or target_type):
        return create_identity(*fields)

    # Create getter, using standard library operator.attrgetter and
    # operator.itemgetter
    getter: AnyOp
    if not domain_type:
        getter = lambda *args: args
    elif domain_type == object:
        # TODO: check if field ids are valid
        # check.has_iterable_type(...)
        getter = operator.attrgetter(*fields) # type: ignore
    elif issubclass(domain_type, Mapping):
        # TODO: check if field ids are valid
        getter = operator.itemgetter(*fields)
    elif issubclass(domain_type, Sequence):
        # TODO: check if field IDs are valid
        if domain_vars:
            ids = [
                domain_vars.index(field) for field in fields] # type: ignore
            getter = operator.itemgetter(*ids)
        else:
            getter = operator.itemgetter(*fields)
    else:
        raise InvalidTypeError('domain', domain, (object, Mapping, Sequence))

    # Create converter that maps the tuple retrived from the getter to a
    # specified target format
    converter: AnyOp
    if not target_type:
        converter = identity
    elif target_type == tuple:
        converter = lambda x: x if isinstance(x, tuple) else (x, )
    elif target_type == list:
        converter = lambda x: list(x) if isinstance(x, tuple) else [x]
    elif target_type == dict:
        dzip: AnyOp = lambda seq: dict(zip(target_vars, seq))
        name = target_vars[0]
        converter = lambda x: dzip(x) if isinstance(x, tuple) else {name: x}
    else:
        raise ValueError()
        # TODO: raise InvalidValueError('target', target, (tuple, list, dict))

    return compose(converter, getter)

def create_setter(*items: Item, domain: type = dict) -> AnyOp:
    """Create a setter operator with fixed values.

    Args:
        *items:
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.

    """
    # The default setter is the (void) zero operator
    if not items:
        return create_zero(None)

    if domain == object:
        # TODO: check if field names are identifiers
        # check.has_iterable_type(...)
        def attrsetter(obj: object) -> None:
            for name, val in items:
                setattr(obj, name, val) # type: ignore
        return attrsetter

    # For mappings use the respective .update() method
    if issubclass(domain, Mapping):
        updates = dict(items)
        return lambda obj: obj.update(updates)

    if issubclass(domain, Sequence):
        def seqsetter(seq: Sequence) -> None:
            for key, val in items:
                seq[key] = val # type: ignore
        return seqsetter

    # TODO: Use some kind of ValueEror for domain!
    raise InvalidTypeError('domain', domain, (object, Mapping, Sequence))

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
        *keys: FieldID, domain: Cat = None, reverse: bool = False) -> SeqHom:
    """Create a sorter with fixed sorting keys.

    Sorters are operators, that act on sequences of objects of a given category
    and change the order of the objects within the sequence.

    Args:
        *keys: Valid :term:`field identifiers <field identifier>` for the
            *sorting keys*, where the requirements and the concrete meaning
            depends on the domain of the operator.
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        reverse:

    Returns:
        Callable function which sorts a sequence of operands by specified
        content.

    """
    # Create getter operator for given keys
    getter = create_mapper(*keys, domain=domain) if keys else None

    # Create and return sorting operator
    return lambda seq: sorted(seq, key=getter, reverse=reverse)

def create_grouper(
        *keys: FieldID, domain: Cat = None, presorted: bool = False) -> SeqOp:
    """Create a grouping operator with fixed grouping keys.

    Args:
        *keys: Valid :term:`field identifiers <field identifier>` of the
            *grouping keys*, where the requirements and the concrete meaning
            depends on the domain of the operator.
        domain: Optional domain category of the operator. If provided, the
            category has to be given as a :class:`type`. Supported types are
            :class:`object`, subclasses of the class:`Mapping class
            <collection.abs.Mapping>` and subclasses of the :class:`Sequence
            class <collection.abs.Sequence>`. The default domain is object.
        presorted: The grouping operation splits in two consecutive steps: In
            the first step the input sequence is sorted by the given keys.
            Thereupon in the second steps the sorted sequence is partitioned in
            blocks, which are equal with respect to the keys. Consequently if
            the sequences are already sorted, the first step is not required and
            can be omitted to increase the performance of the operator. By
            default the input sequences are assumed not to be presorted.

    Returns:
        List of sequences containing objects of a given domain, which are equal
        with respect to given grouping keys.

    """
    # The default grouper groups all sequence elements into a single group
    if not keys:
        return lambda seq: [seq]

    # Create getter for given keys
    getter = create_mapper(*keys, domain=domain)

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
        *args: VarDef, domain: Cat = None, target: type = tuple) -> SeqOp:
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
    getfirst = operator.itemgetter(0) # Faster then: lambda seq: seq[0]
    fields, ops, names = split_var_params(*args, default=getfirst)

    # Create a getter, that maps the input sequence to a matrix
    getter = create_mapper(*fields, domain=domain, target=tuple)
    matrix: SeqOp = lambda seq: list(map(getter, seq))

    # Create operators, that transpose the matrix and aggregate the columns
    trans: SeqOp = lambda mat: tuple(list(col) for col in zip(*mat))
    aggreg: SeqOp = lambda arr: tuple(op(seq) for op, seq in zip(ops, arr))

    # If the requested type is tuple just compose the operators
    if target == tuple:
        return lambda seq: aggreg(trans(matrix(seq)))

    # For dictionaries a further type conversion is required
    if target == dict:
        return lambda seq: dict(zip(names, aggreg(trans(matrix(seq)))))

    raise ValueError(f"type '{target.__name__}' is not supported")

def create_group_aggregator(
        *args: VarDef, key: OptKey = None, domain: Cat = None,
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
