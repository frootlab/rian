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
"""Structural / Symbolic Types."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
from typing import Any, Callable, NamedTuple, Hashable, Tuple, Union, Type
from typing import Optional, Mapping, Dict
from nemoa.base import check
from nemoa.math import operator
from nemoa.types import AnyOp, OptOp, OptType, NoneType

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
VarLike = Union[
    str,                        # Variable(<name>, Identity, (<name>, ))
    Tuple[str],                 # Variable(<name>, Identity, (<name>, ))
    Tuple[str, FieldID],        # Variable(<name>, Identity, (<id>, ))
    Tuple[str, Frame],          # Variable(<name>, Identity, <frame>)
    Tuple[str, AnyOp],          # Variable(<name>, <operator>, (<name>, ))
    Tuple[str, AnyOp, FieldID], # Variable(<name>, <operator>, (<id>, ))
    Tuple[str, AnyOp, Frame],   # Variable(<name>, <operator>, <frame>)
    Tuple[str, str, FieldID],   # Variable(<name>, <lambda>, (<id>, ))
    Tuple[str, str, Frame]]     # Variable(<name>, <lambda>, <frame>)

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

def create_variable(var: VarLike, default: OptOp = None) -> Variable:
    """Create variable from variable definition.

    Args:
        var: Variable defintion
        default:

    Returns:

    """
    # Check Arguments
    check.has_type('var', var, (str, tuple))
    check.not_empty('var', var)

    # Get Defaults
    default = default or operator.Identity()

    # Get Variable Arguments
    args: VarLike
    if isinstance(var, str):
        if var.isidentifier():
            args = (var, default, (var, ))
        else:
            op = operator.Lambda(expression=var)
            args = (var, op, op.variables)
    elif len(var) == 1:
        args = (var[0], default, (var[0], ))
    elif len(var) == 2:
        if callable(var[1]):
            args = (var[0], var[1], (var[0], ))
        elif isinstance(var[1], tuple):
            args = (var[0], default, var[1])
        else:
            args = (var[0], default, (var[1], ))
    elif callable(var[1]):
        if isinstance(var[2], tuple):
            args = (var[0], var[1], var[2])
        else:
            args = (var[0], var[1], (var[2], ))
    elif isinstance(var[2], tuple):
        op = operator.Lambda(expression=var[1], domain=(None, var[2]))
        args = (var[0], op, var[2])
    else:
        op = operator.Lambda(expression=var[1], domain=(None, (var[2], )))
        args = (var[0], op, (var[2], ))

    # Check Variable Arguments
    check.has_type('variable name', args[0], str)
    check.has_type('variable operator', args[1], Callable)
    check.has_type('variable frame', args[2], tuple)

    # Create and return Variable
    return Variable(*args)

#
# Fields
#

class Field(NamedTuple):
    """Class for Field Parameters."""
    id: FieldID
    type: Type = NoneType

    def __repr__(self) -> str:
        name = type(self).__name__
        dtype = 'None' if self.type == NoneType else self.type.__name__
        return f"{name}({repr(self.id)}, {dtype})"

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

#
# Domains
#

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
