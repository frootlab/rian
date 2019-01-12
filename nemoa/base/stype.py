# -*- coding: utf-8 -*-
"""Structured type declaration."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
from typing import Any, NamedTuple, Hashable, Tuple, Union, Type, Optional
from typing import Mapping
from nemoa.base import check
from nemoa.types import OptType, NoneType

Keywords = Optional[Mapping[str, Any]]
FieldID = Hashable
FieldLike = Union[
    FieldID,                # Field(<id>, NoneType)
    Tuple[FieldID],         # Field(<id>, NoneType)
    Tuple[FieldID, type],   # Field(<id>, <type>)
    'Field']                # Field(<id>, <type>)
Fields = Tuple['Field', ...]
Frame = Tuple[FieldID, ...]
Basis = Tuple[Frame, Fields]
DomLike = Union[OptType, Tuple[OptType, Frame], 'Domain']

#
# Parameter Classes
#

class Field(NamedTuple):
    """Class for Field Parameters."""
    id: FieldID
    type: Type

class Domain(NamedTuple):
    """Class for Domain Parameters."""
    type: Type
    frame: Frame
    fields: Fields

    def __repr__(self) -> str:
        name = type(self).__name__
        if self.type == NoneType:
            type_name = 'None'
        else:
            type_name = self.type.__name__
        if not self.fields:
            return f"{name}({type_name})"
        if len(self.fields) == 1:
            fields_repr = repr(self.fields[0])
            return f"{name}({type_name}, {fields_repr})"
        fields_repr = ', '.join(map(repr, self.fields))
        return f"{name}({type_name}, ({fields_repr}))"

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
    # Get field parameters
    field_id: Any
    field_type: Any
    if isinstance(field, Field):
        field_id = field.id
        field_type = field.type
    elif isinstance(field, tuple):
        if len(field) == 1:
            field_id = field[0]
            field_type = NoneType
        elif len(field) == 2:
            field_id = field[0]
            field_type = field[1]
    else:
        field_id = field
        field_type = NoneType

    # Validate Paramateres
    if not isinstance(field_id, Hashable):
        raise ValueError(f"unhashable field identifier '{field_id}'")
    if not isinstance(field_type, type):
        raise ValueError(f"invalid daomin type '{field_type}'")

    # Create and return Field object
    return Field(field_id, field_type)

def create_basis(arg: Any) -> Basis:
    """Create a domain basis from given field definitions.

    Args:

    Returns:

    """

    # Create Basis from Field Definitions
    basis: Tuple[Field, ...]
    if not arg:
        basis = tuple()
    elif isinstance(arg, tuple):
        basis = tuple(create_field(field) for field in arg)
    elif isinstance(arg, Hashable):
        basis = (create_field(arg), )
    else:
        raise ValueError(f"field definition '{arg}' is not valid")

    # Get frame and fields from basis
    frame = tuple(b.id for b in basis)
    fields = basis
    return frame, fields

def create_domain(domain: DomLike = None, defaults: Keywords = None) -> Domain:
    """Create Domain object from domain definition.

    Args:
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of a domain.
        defaults: Optional :term:`mapping` which is used to complete the given
            domain definition. The key `'type'` specifies the default domain
            type and is required to be given as a :class:`type`. The key
            `'fields'` specifies the default domain frame and is required to be
            given as a single or a tuple of :term:`field definitions<field
            definition>`.

    Returns:
        Instance of the class :class:`Domain`

    """
    # Check Types of Arguments
    check.has_opt_type('domain', domain, (Hashable, Field, tuple))
    check.has_opt_type('defaults', defaults, Mapping)

    # Get Defaults
    defaults = defaults or {}
    deftype = defaults.get('type', NoneType)
    defbasis = defaults.get('fields', tuple())

    # Get Domain Constructor Arguments
    if not domain:
        args = (deftype, *create_basis(defbasis))
    elif isinstance(domain, Domain):
        args = (domain.type, domain.frame, domain.fields)
    elif isinstance(domain, tuple):
        args = (domain[0] or deftype, *create_basis(domain[1] or defbasis))
    else:
        args = (domain, *create_basis(defbasis))

    # Validate Arguments
    check.has_type('domain type', args[0], type)
    check.has_type('domain frame', args[1], tuple)
    # TODO: check.is_unique('domain frame', args[1])
    if len(set(args[1])) < len(args[1]):
        print(domain, defaults)
        raise ValueError(f"invalid frame {args[1]}")
    check.has_type('domain fields', args[2], tuple)

    # Create and return Domain Object
    return Domain(*args)
