# -*- coding: utf-8 -*-
"""Classes and functions for structured types."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
from typing import Any, NamedTuple, Hashable, Tuple, Union, Type, Optional
from typing import Mapping, Dict
from nemoa.base import check
from nemoa.types import OptType, NoneType

Keywords = Optional[Mapping[str, Any]]
FieldID = Hashable
FieldLike = Union[
    FieldID,                # Field(<id>, NoneType)
    Tuple[FieldID],         # Field(<id>, NoneType)
    Tuple[FieldID, type],   # Field(<id>, <type>)
    'Field']                # Field(<id>, <type>)
Fields = Dict[FieldID, 'Field']
Frame = Tuple[FieldID, ...]
Basis = Tuple[Frame, Fields]
DomLike = Union[OptType, Tuple[OptType, Frame], 'Domain']

#
# Parameter Classes
#

class Field(NamedTuple):
    """Class for Field Parameters."""
    id: FieldID
    type: Type = NoneType

    def __repr__(self) -> str:
        name = type(self).__name__
        dtype = 'None' if self.type == NoneType else self.type.__name__
        return f"{name}({repr(self.id)}, {dtype})"

class Domain(NamedTuple):
    """Class for Domain Parameters."""
    type: Type = NoneType
    frame: Frame = tuple()
    basis: Fields = dict()

    def __repr__(self) -> str:
        name = type(self).__name__
        dtype = 'None' if self.type == NoneType else self.type.__name__
        if not self.basis:
            return f"{name}({dtype})"
        if len(self.basis) == 1:
            field = repr(tuple(self.basis.values())[0])
            return f"{name}({dtype}, {field})"
        fields = ', '.join(map(repr, map(self.basis.get, self.frame)))
        return f"{name}({dtype}, ({fields}))"

    def __hash__(self) -> int:
        value = hash(self.type) ^ hash(self.frame)
        for field in self.basis.items():
            value ^= hash(field)
        return value

    def __bool__(self) -> bool:
        return self.type != NoneType or bool(self.frame) or bool(self.basis)

#
# Constructors
#

@functools.lru_cache(maxsize=256)
def create_field(field: FieldLike) -> Field:
    """Create a Field object.

    Args:
        field: :term:`Field definition`

    Return:
        Instance of class :class:`Field`

    """
    # Get Field Arguments
    if isinstance(field, Field):
        args = (field.id, field.type)
    elif isinstance(field, tuple):
        if len(field) == 1:
            args = (field[0], NoneType)
        elif len(field) == 2:
            args = (field[0], field[1])
    else:
        args = (field, NoneType)

    # Check Field Arguments
    check.has_type('field identifier', args[0], Hashable)
    check.has_type('field type', args[1], type)

    # Create and return Field
    return Field(*args)

def create_basis(arg: Any) -> Basis:
    """Create domain frame and basis from given field definitions.

    Args:

    Returns:

    """

    # Create Basis from Field Definitions
    fields: Tuple[Field, ...]
    if not arg:
        fields = tuple()
    elif isinstance(arg, tuple):
        fields = tuple(create_field(field) for field in arg)
    elif isinstance(arg, Hashable):
        fields = (create_field(arg), )
    else:
        raise ValueError(f"field definition '{arg}' is not valid")

    # Get Frame and Basis from Fields
    frame = tuple(b.id for b in fields)
    basis = dict(zip(frame, fields))

    return frame, basis

def create_domain(domain: DomLike = None, defaults: Keywords = None) -> Domain:
    """Create Domain object from domain definition.

    Args:
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of a domain.
        defaults: Optional :term:`mapping` which is used to complete the given
            domain definition. The key `'type'` specifies the default domain
            type and is required to be given as a :class:`type`. The key
            `'fields'` specifies a default ordered basis for the domain and is
            required to be given as a single or a tuple of :term:`field
            definitions<field definition>`.

    Returns:
        Instance of the class :class:`Domain`

    """
    # Check Arguments
    check.has_opt_type('domain', domain, (Hashable, Field, tuple))
    check.has_opt_type('defaults', defaults, Mapping)

    # Get Defaults
    defaults = defaults or {}
    dtype = defaults.get('type', NoneType)
    dfields = defaults.get('fields', tuple())

    # Get Domain Arguments
    if not domain:
        args = (dtype, *create_basis(dfields))
    elif isinstance(domain, Domain):
        args = (domain.type, domain.frame, domain.basis)
    elif isinstance(domain, tuple):
        args = (domain[0] or dtype, *create_basis(domain[1] or dfields))
    else:
        args = (domain, *create_basis(dfields))

    # Check Domain Arguments
    check.has_type('domain type', args[0], type)
    check.has_type('domain frame', args[1], tuple)
    check.no_dublicates('domain frame', args[1])
    check.has_type('domain basis', args[2], dict)

    # Create and return Domain
    return Domain(*args)
