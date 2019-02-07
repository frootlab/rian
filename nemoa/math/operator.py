# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Classes and functions for functional programming."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import collections
import functools
import itertools
import operator
from typing import List, Optional, Tuple, Sequence, Union
from typing import Any, Hashable
from nemoa.base import abc, check, parser
from nemoa.errors import InvalidTypeError
from nemoa.math import stype
from nemoa.types import Method, Mapping, NoneType, OptOp, SeqHom
from nemoa.types import SeqOp, AnyOp, StrList, StrTuple
from nemoa.math.stype import FieldID, Frame

Key = Optional[Union[FieldID, Frame]]
Item = Tuple[FieldID, Any]

#
# Operator Classes
#

class Operator(collections.abc.Callable, abc.Multiton): # type: ignore
    """Abstract Base Class for operators.

    Args:
        *args:
        domain:
        target:

    """
    __slots__: StrList = ['_domain', '_target']

    _domain: stype.Domain
    _target: stype.Domain

    def __init__(
            self, *args: FieldID, domain: stype.DomLike = None,
            target: stype.DomLike = None) -> None:
        self._domain = stype.create_domain(domain, defaults={'fields': args})
        self._target = stype.create_domain(target, defaults={'fields': args})

        # If a target frame is given, build a len function and bind it to the
        # method __call__. Note: This is only possible, since the Multiton base
        # class isolates classes per instances.
        if self._target.frame:
            size = len(self._target.frame)
            func: AnyOp = lambda: size
            meth = staticmethod(func)
            setattr(type(self), '__len__', meth)

    def __call__(self, *args: Any) -> Any:
        raise NotImplementedError() # TODO

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

class Zero(Operator):
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
    __slots__: StrList = []

    def __init__(self, target: stype.DomLike = None) -> None:
        super().__init__(domain=None, target=target)
        self._validate()
        self._build()

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        name = type(self).__name__
        target_type = self._target.type.__name__
        return f"{name}({target_type})"

    def _validate(self) -> None:
        tgt = self._target

        # Zero operators require an empty target frame
        if tgt.frame:
            raise ValueError(
                "the target frame is required to be empty")

        # Sanity check if the target type has a unique empty object
        if not tgt.type() == tgt.type():
            raise ValueError(
                f"target type '{tgt.type.__name__}' is not supported: "
                "zero object is not unique")

    def _build(self) -> None:
        # Create zero object in target type, build a zero morphism and bind it
        # to the method __call__. Note: This is only possible, since the
        # Multiton base class implements class isolation.
        zero = self._target.type()
        func = lambda *args: zero
        meth = staticmethod(func)
        setattr(type(self), '__call__', meth)

class Identity(Operator):
    """Class for identity operators.

    Args:
        domain:

    """
    __slots__: StrList = []

    def __init__(self, domain: stype.DomLike = None) -> None:
        super().__init__(domain=domain, target=domain)
        self._build()

    def _build(self) -> None:
        # Declare identity functions for (A) a variable number of arguments, (B)
        # a single argument (C) two argumnts (D) four argumnts (E) for multiple
        # arguments
        def func_varargs(*args: Any) -> Any:
            if not args:
                return None
            if len(args) == 1:
                return args[0]
            return args
        def func_1arg(arg: Any) -> Any:
            return arg
        def func_2arg(arg1: Any, arg2: Any) -> Tuple[Any, Any]:
            return (arg1, arg2)
        def func_3arg(arg1: Any, arg2: Any, arg3: Any) -> Tuple[Any, Any, Any]:
            return (arg1, arg2, arg3)
        def func_args(*args: Any) -> Tuple[Any, ...]:
            return args

        # Build an identity operator by using the type and the frame size of the
        # domain. If a domain type is given, then the function allways expects a
        # single object of given type. If, however, the domain type is NoneType,
        # then the number of argumnts depends on the size of the domain frame.
        # If no frame is specified, that the number is variable.
        # TODO: dynamically build operator with argument names and types, taken
        # from domain
        dom = self._domain
        func: AnyOp
        if dom.type is not NoneType:
            func = func_1arg
        elif not dom.frame:
            func = func_varargs
        elif len(dom.frame) == 1:
            func = func_1arg
        elif len(dom.frame) == 2:
            func = func_2arg
        elif len(dom.frame) == 3:
            func = func_3arg
        else:
            func = func_args

        # Bind the identity operator as a static method to the attribute
        # __call__. Note: This is only possible, since the Multiton base class
        # implements class isolation.
        setattr(type(self), '__call__', staticmethod(func))

    def __repr__(self) -> str:
        name = type(self).__name__
        dtype = self.domain.type
        if dtype == NoneType:
            return f'{name}'
        return f'{name}({dtype.__name__})'

class Getter(Operator):
    """Class for Getters.

    A getter essentially is the composition of a `fetch` operation, that
    specifies the fields of a given domain type and a subsequent
    `representation` of the fetched fields as an object of given target type, by
    using the target frame (if given) as field identifiers.

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
    __slots__: StrList = []

    def __new__(
            cls, *args: FieldID, domain: stype.DomLike = None,
            target: stype.DomLike = None) -> Operator:
        domain = stype.create_domain(domain, defaults={'fields': args})
        target = stype.create_domain(target, defaults={'fields': args})

        # If no fields are given, the Getter operator is a Zero morphism onto
        # the target
        if not args:
            return Zero(target=target)

        # If the domain equals the target (type, frame and basis), then the
        # Getter operator is the Identity operator of the domain
        if domain == target:
            return Identity(domain=domain)

        return super().__new__(cls)

    def __init__(
            self, *args: FieldID, domain: stype.DomLike = None,
            target: stype.DomLike = None) -> None:
        # Initialize Base Class
        super().__init__(*args, domain=domain, target=target)

        # Build Getter Operator
        self._build(*args)

    @classmethod
    def __subclasshook__(cls, other: type) -> bool:
        # Pretend that the Zero and Identity class are subclasses
        if cls is Getter and issubclass(other, (Zero, Identity)):
            return True
        return NotImplemented

    def __repr__(self) -> str:
        name = type(self).__name__
        try:
            frame = self._domain.frame
            return f"{name}({', '.join(map(repr, frame))})"
        except AttributeError:
            return f"{name}()"
        except TypeError:
            return f"{name}()"

    def _build(self, *args: Any) -> None:
        # Build fetch and format operators
        fetch = self._build_fetch(*args, domain=self._domain)
        formatter = self._build_formatter(*args, target=self._target)

        # Build a getter operator by composing the fetch and the formatter
        # operator. If the formatter is an identity operator, return getter. If
        # the fetch operator is an identity operator, precede a 'boxing'
        # operator to the formatter
        getter: AnyOp
        if isinstance(formatter, Identity):
            getter = fetch
        elif isinstance(fetch, Identity):
            getter = compose(formatter, lambda *args: args)
        else:
            getter = compose(formatter, fetch)

        # Bind the identity operator as a static method to the attribute
        # __call__. Note: This is only possible, since the Multiton base class
        # implements class isolation.
        setattr(type(self), '__call__', staticmethod(getter))

    def _build_fetch(self, *args: FieldID, domain: stype.Domain) -> AnyOp:
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
            itemgetter = operator.itemgetter(*map(domain.frame.index, args))
            return lambda *args: itemgetter(args)

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
                pos = map(domain.frame.index, args)
                return operator.itemgetter(*pos)
            for arg in args:
                if not isinstance(arg, int) or arg < 0:
                    raise InvalidTypeError(
                        'any field', args, 'positive integer')
            return operator.itemgetter(*args)

        # TODO: raise InvalidValueError!
        raise InvalidTypeError(
            'domain type', domain.type, (object, Mapping, Sequence))

    def _build_formatter(self, *args: FieldID, target: stype.Domain) -> AnyOp:
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
                    "target type 'dict' requires the specification of fields")
            first = frame[0]
            d1: AnyOp = lambda x: {first: x} # arg -> dict
            dn: AnyOp = lambda x: dict(zip(frame, x)) # args -> dict
            return lambda x: dn(x) if isinstance(x, tuple) else d1(x)

        # TODO: raise InvalidValueError!
        raise InvalidTypeError('target type', target.type, (tuple, list, dict))

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
        compile: Optional Boolean parameter, which determines if the operator
            is compiled after it is parsed.

    """
    __slots__ = ['_expression', '_variables']

    _expression: str
    _variables: StrTuple

    def __new__(
            cls, expression: str = '', domain: stype.DomLike = None,
            variables: StrTuple = tuple(), default: OptOp = None,
            compile: bool = True) -> Operator: # pylint: disable=W0622
        # If no expression and no default operator is given, the Lambda operator
        # is a zero operator.
        if not expression and not default:
            return Zero()

        # If the expression ether is an identifier or contained within the
        # domain frame, the Lambda operator is a Getter operator
        domain = stype.create_domain(domain, defaults={'fields': variables})
        if expression.isidentifier() or expression in domain.frame:
            target = (None, (expression, ))
            return Getter(expression, domain=domain, target=target)

        return super().__new__(cls)

    def __init__(
            self, expression: str = '', domain: stype.DomLike = None,
            variables: StrTuple = tuple(), default: OptOp = None,
            compile: bool = True) -> None: # pylint: disable=W0622
        # Initialize Base Class
        target = (None, (expression, ))
        super().__init__(*variables, domain=domain, target=target)

        # Bind Attributes
        self._expression = expression

        # Build Operator
        self._build(compile=compile, default=default)

    def __repr__(self) -> str:
        name = type(self).__name__
        try:
            return f"{name}('{self._expression}')"
        except AttributeError:
            return f"{name}()"

    @classmethod
    def __subclasshook__(cls, other: type) -> bool:
        # Pretend that the Getter classes are subclasses
        if cls is Lambda and issubclass(other, Getter):
            return True
        return NotImplemented

    #
    # Public
    #

    @property
    def variables(self) -> Frame:
        try:
            return self._variables
        except AttributeError:
            return self._domain.frame

    #
    # Protected
    #

    def _build(
            self, compile: bool = True, # pylint: disable=W0622
            default: OptOp = None) -> None:
        # If no expression is provided, use the default operator, or if also not
        # provided the Zero(None) operator.
        if not self._expression:
            default = default or Zero().__call__
            setattr(type(self), '__call__', staticmethod(default))
            return

        # If the domain uses a frame, the given field IDs of the domain are not
        # required to be valid variable names to the parser, which requires to
        # pass the the frame to the parser.
        frame = self._domain.frame
        expr = parser.parse(self._expression, variables=frame)

        # The parser internally substitutes the field IDs by valid variable
        # names. The finally used variable names are provided by the attribute
        # 'variables' and the corresponding original field IDs by 'origin'.
        variables = self._variables = expr.variables
        fields = expr.origin

        # If the Domain frame is not given, create and bind a new domain with a
        # frame, that is given by the field names.
        dom = self._domain
        if not dom.frame:
            self._domain = stype.create_domain((dom.type, tuple(fields)))
            dom = self._domain

        # If the term is trusted create and compile lambda term. Note, that the
        # lambda term usually may be considered to be a trusted expression, as
        # it has been created by using the expression parser
        getter = Getter(*fields, domain=dom, target=(tuple, variables))
        func = expr.as_func(compile=compile)
        final = compose(func, getter, unpack=True)

        setattr(type(self), '__call__', staticmethod(final))

class Vector(collections.abc.Sequence, Operator):
    """Class for vectorial functions.

    Args:
        *args: Optional definitions of the function components. If provided, any
            component has to be given as a valid :term:`variable definition`.
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's domain. The accepted
            parameter values are documented in the class :class:`Getter`.
        target: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of the operator's target. The accepted
            parameter values are documented in the class :class:`Getter`.
        default: Default operator which is used to map fields to field
            variables. By default the identity is used.

    """
    __slots__ = ['_variables', '_built_components']

    _variables: Tuple[stype.Variable, ...]
    _built_components: Tuple[AnyOp, ...]

    def __new__(
            cls, *args: stype.VarLike, domain: stype.DomLike = None,
            target: stype.DomLike = None, default: OptOp = None) -> Operator:
        # If no variables are defined, the returned operator is the Zero
        # morphism onto the target's empty object.
        if not args:
            return Zero(target)

        # TODO: Check if the Vector can be implemented as a Getter

        return super().__new__(cls)

    def __init__(
            self, *args: stype.VarLike, domain: stype.DomLike = None,
            target: stype.DomLike = None, default: OptOp = None) -> None:
        # Initialize Operator Base Class
        Operator.__init__(self)

        self._update_variables(*args, default=default)
        self._update_domain(domain)
        self._update_target(target)
        self._build_components()
        self._build()

    def __getitem__(self, pos: Union[int, slice]) -> Any:
        if isinstance(pos, int):
            return self._built_components[pos]
        if isinstance(pos, slice):
            ops = self._built_components[pos]
            return lambda *args: tuple(op(*args) for op in ops)
        raise InvalidTypeError('pos', pos, (int, slice))

    def __len__(self) -> int:
        return len(self._target.frame)

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

    def _update_variables(
            self, *args: stype.VarLike, default: OptOp = None) -> None:
        var: AnyOp = lambda arg: stype.create_variable(arg, default=default)
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

    def _build_components(self) -> None:
        # Check if all field identifiers are found within the frame. Note that
        # this is also True if no frame is used, since set() <= set()
        if not set(self.fields) <= set(self._domain.frame):
            raise ValueError() # TODO

        # Create operators for the partial (per component) evaluation of the
        # mapper
        ops: List[AnyOp] = []
        for var in self._variables:
            getter = Getter(*var.frame, domain=self.domain)
            if isinstance(var.operator, Identity):
                ops.append(getter)
            elif not var.frame:
                ops.append(var.operator)
            elif len(var.frame) == 1:
                ops.append(compose(var.operator, getter))
            else:
                ops.append(compose(var.operator, getter, unpack=True))
        self._built_components = tuple(ops)

    def _build(self) -> None:
        func: AnyOp
        variables = self._variables
        domain = self._domain
        target = self._target
        components = self.components

        # Check if the vector operator can be implemented as a Getter. In
        # this case create and return the Getter
        equal: AnyOp = lambda var: (
            len(var.frame) == 1 and isinstance(var.operator, Identity))
        if all(map(equal, variables)):
            fields = tuple(var.frame[0] for var in variables)
            getter = Getter(*fields, domain=domain, target=target)
            func = getattr(getter, '__call__', getter)
            setattr(type(self), '__call__', staticmethod(func))
            return

        # If the mapper can not be implemented as a projection ...
        # TODO: Implement as follows:
        # 1. single getter
        # 2. apply all component operators ...
        # 3. single formatter
        mapper: AnyOp
        f = self._built_components
        if len(self) == 1:
            mapper = f[0]
        elif len(self) == 2:
            mapper = lambda *args: (f[0](*args), f[1](*args))
        elif len(self) == 3:
            mapper = lambda *args: (f[0](*args), f[1](*args), f[2](*args))
        else:
            mapper = lambda *args: tuple(comp(*args) for comp in f)

        # Create formatter
        formatter = Getter(
            *components, domain=(None, components), target=target)

        # If the formatter is an identity operator, return mapper. If the mapper
        # is an identity operator, precede a tuple 'packer' to the formatter
        if isinstance(formatter, Identity):
            func = mapper
        elif isinstance(mapper, Identity):
            func = formatter
        elif len(self) == 1:
            func = compose(formatter, mapper)
        else:
            func = compose(formatter, mapper, unpack=True)

        meth = staticmethod(func)
        setattr(type(self), '__call__', meth)

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
    # Check types of arguments
    if not all(map(lambda arg: arg is None or callable(arg), args)):
        raise InvalidTypeError('every argument', args, 'callable or None')

    # Filter None and identity operators. If no arguments pass the filter, the
    # the default operator given by the identity is used.
    use: AnyOp = lambda op: not(op is None or isinstance(args, Identity))
    ops = tuple(filter(use, args)) or (Identity(), )

    # Create pairwise composition operator and apply it to the remaining
    # arguments
    circ: AnyOp
    if unpack:
        circ = lambda f, g: lambda *cargs: f(*g(*cargs))
    else:
        circ = lambda f, g: lambda *cargs: f(g(*cargs))
    return functools.reduce(circ, ops) or Identity()

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
# Builders for sequence operators
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
            parameter values are documented in the class :class:`Getter`.
        reverse: Optional boolean parameter. If set to True, then the sequence
            elements are sorted as if each comparison were reversed.

    Returns:
        Callable function which sorts a sequence of objects of a given domain by
        given sorting keys.

    """
    # Create getter operator for given keys
    getter = Getter(*args, domain=domain) if args else None

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
            parameter values are documented in the class :class:`Getter`.
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
    getter = Getter(*args, domain=domain)

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
        *args: stype.VarLike, domain: stype.DomLike = None,
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

    # Create vectorial operator using the variable definitions
    f = Vector(*args, default=operator.itemgetter(0))

    # Create an operator, that converts data stored in rows to columns.
    # 1. At first fetch the rows from the input sequence
    # 2. Create a Matrix from the sequence (a list of rows)
    # 3. Transpose a Matrix (to a tuple of columns)
    # 4. Compose Matrix creation and transposition
    getter = Getter(*f.fields, domain=domain, target=tuple)
    matrix: SeqOp = lambda seq: list(map(getter, seq))
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
        *args: stype.VarLike, key: Key = None, domain: stype.DomLike = None,
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
