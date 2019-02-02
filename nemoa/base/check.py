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
"""Check type and value of objects."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from typing import Any, Callable, Collection
from nemoa import errors
from nemoa.types import Class, Sized, RealNumber
from nemoa.types import OptInt, TypeHint

#
# Type Checks
#

def has_type(name: str, obj: object, hint: TypeHint) -> None:
    """Check type of object."""
    # Check instance against classinfo
    if isinstance(hint, (type, tuple)):
        if isinstance(obj, hint):
            return
        raise errors.InvalidTypeError(name, obj, hint)
    # Check against assorted Structural Types
    if hint == Any:
        return
    if hint == TypeHint:
        try:
            is_typehint(name, obj)
        except errors.InvalidTypeError as err:
            raise errors.InvalidTypeError(name, obj, hint) from err
        return
    if hint == Callable:
        try:
            is_callable(name, obj)
        except errors.NotCallableError as err:
            raise errors.InvalidTypeError(name, obj, hint) from err
        return
    if hasattr(hint, '__origin__'):
        has_type(name, obj, getattr(hint, '__origin__'))

def has_opt_type(name: str, obj: object, hint: TypeHint) -> None:
    """Check type of optional object."""
    if obj is None:
        return
    has_type(name, obj, hint)

def is_callable(name: str, obj: object) -> None:
    """Check if object is callable."""
    if not callable(obj):
        raise errors.NotCallableError(name, obj)

def is_class(name: str, obj: object) -> None:
    """Check if object is a class."""
    if not inspect.isclass(obj):
        raise errors.NotClassError(name, obj)

def is_subclass(name: str, obj: object, ref: Class) -> None:
    """Check if object is a subclass of given class."""
    if not inspect.isclass(obj) or not issubclass(obj, ref): # type: ignore
        raise errors.InvalidClassError(name, obj, ref)

def is_typehint(name: str, obj: object) -> None:
    """Check if object is a supported typeinfo object."""
    if isinstance(obj, tuple):
        for i, token in enumerate(obj):
            is_typehint(f'{name}[{i}]', token)
            return
    # Allow any class with metaclass 'type'
    if isinstance(obj, type):
        return
    # Allow assorted structural types
    if obj in [TypeHint, Any, Callable]:
        return
    if hasattr(obj, '__origin__'):
        return
    raise errors.InvalidTypeError(name, obj, 'typeinfo')

#
# Value Checks
#

def is_identifier(name: str, string: str) -> None:
    """Check if a string is a valid identifier."""
    if not string.isidentifier():
        raise errors.InvalidFormatError(name, string, "'UAX-31'")

def is_subset(a: str, seta: set, b: str, setb: set) -> None:
    """Check if a set is a subset of another."""
    if not seta.issubset(setb):
        raise errors.NoSubsetError(a, seta, b, setb)

def no_dublicates(name: str, coll: Collection) -> None:
    """Check if all elements of a collection are unique."""

    if not len(set(coll)) == len(coll):
        items = list(coll)
        for item in set(coll):
            items.remove(item)
        raise errors.DublicateError(name, set(items))

def is_positive(name: str, obj: RealNumber) -> None:
    """Check if number is positive."""
    if obj <= 0:
        raise errors.NotPositiveError(name, obj)

def is_negative(name: str, obj: RealNumber) -> None:
    """Check if number is negative."""
    if obj >= 0:
        raise errors.NotNegativeError(name, obj)

def is_not_positive(name: str, obj: RealNumber) -> None:
    """Check if number is not positive."""
    if obj > 0:
        raise errors.IsPositiveError(name, obj)

def is_not_negative(name: str, obj: RealNumber) -> None:
    """Check if number is not negative."""
    if obj < 0:
        raise errors.IsNegativeError(name, obj)

def not_empty(name: str, obj: Sized) -> None:
    """Check if a sized object is not empty."""
    if len(obj) == 0:
        raise errors.MinSizeError(name, obj, 1)

def has_size(
        name: str, obj: Sized, size: OptInt = None,
        min_size: OptInt = None, max_size: OptInt = None, ) -> None:
    """Check the size of a sized object."""
    num = len(obj)
    if size and num != size:
        raise errors.SizeError(name, obj, size)
    if min_size and num < min_size:
        raise errors.MinSizeError(name, obj, min_size)
    if max_size is not None and num > max_size:
        raise errors.MaxSizeError(name, obj, max_size)

def has_attr(obj: object, attr: str) -> None:
    """Check if object has an attribute."""
    if not hasattr(obj, attr):
        raise errors.InvalidAttrError(obj, attr)
