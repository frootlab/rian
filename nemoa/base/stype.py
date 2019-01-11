# -*- coding: utf-8 -*-
"""Structured type declaration."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
from typing import Any, NamedTuple, Hashable, Tuple, Union, Type, Optional
from typing import Mapping
#from nemoa.errors import InvalidTypeError
from nemoa.types import OptType, NoneType

Keywords = Optional[Mapping[str, Any]]
FieldID = Hashable
FieldLike = Union[
    FieldID,                # Field(<id>, NoneType)
    Tuple[FieldID],         # Field(<id>, NoneType)
    Tuple[FieldID, type],   # Field(<id>, <type>)
    'Field']          # Field(<id>, <type>)
Frame = Tuple[FieldID, ...]
Fields = Tuple['Field', ...]
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
    fields: Fields
    frame: Frame

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
        raise ValueError() # TODO

    # Create and return Field object
    return Field(field_id, field_type)

def create_domain(domain: DomLike = None, defaults: Keywords = None) -> Domain:
    """Create a Domain object.

    Args:
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of a domain.
        defaults: Optional :term:`mapping` with default values, used to complete
            the domain definiation. The key `'type'` specifies the default
            domain type and is required to be given as a :class:`type`. The key
            `'fields'` specifies the default domain frame and is required to be
            given as a single or a tuple of :term:`field definitions<field
            definition>`.

    Returns:
        Instance of the class :class:`Domain`

    """
    # Get defaults
    defaults = defaults or {}
    default_type = defaults.get('type', NoneType)
    default_fdef = defaults.get('fields', tuple())

    # Get domain parameters
    if domain is None:
        dom_type = default_type
        dom_fdef = default_fdef
    elif isinstance(domain, Domain):
        dom_type = domain.type
        dom_fdef = domain.frame
    elif isinstance(domain, tuple):
        dom_type = domain[0] or default_type
        dom_fdef = domain[1] or default_fdef
    else:
        dom_type = domain
        dom_fdef = default_fdef
    if isinstance(dom_fdef, tuple):
        dom_fields = tuple(create_field(field) for field in dom_fdef)
    elif dom_fdef is None:
        dom_fields = tuple()
    else:
        dom_fields = (create_field(dom_fdef), )
    dom_frame = tuple(field.id for field in dom_fields)

    # Validate parameters
    # else:
    #     allowed = (NoneType, type, tuple, Domain)
    #     raise InvalidTypeError('domain', domain, allowed)

    if len(set(dom_frame)) < len(dom_frame):
        raise ValueError() # TODO

    return Domain(dom_type, dom_fields, dom_frame)
