# -*- coding: utf-8 -*-
"""Assert functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from nemoa.errors import (
    IsPositiveError, IsNegativeError,
    InvalidTypeError, InvalidClassError, NotClassError, NotCallableError,
    NotHasAttrError, NotIsSubsetError, NotIsPositiveError, NotIsNegativeError,
    MinSizeError, MaxSizeError)
from nemoa.types import Class, ClassInfo, Sized, RealNumber, OptInt

#
# Check Type of Objects
#

def has_type(name: str, obj: object, classinfo: ClassInfo) -> None:
    """Check type of object."""
    if not isinstance(obj, classinfo):
        raise InvalidTypeError(name, obj, classinfo)

def has_opt_type(name: str, obj: object, classinfo: ClassInfo) -> None:
    """Check type of optional object."""
    if obj is not None and not isinstance(obj, classinfo):
        raise InvalidTypeError(name, obj, classinfo)

def is_callable(name: str, obj: object) -> None:
    """Check if object is callable."""
    if not callable(obj):
        raise NotCallableError(name, obj)

def is_class(name: str, obj: object) -> None:
    """Check if object is a class."""
    if not inspect.isclass(obj):
        raise NotClassError(name, obj)

def is_subclass(name: str, obj: object, ref: Class) -> None:
    """Check if object is a subclass of given class."""
    if not inspect.isclass(obj) or not issubclass(obj, ref): # type: ignore
        raise InvalidClassError(name, obj, ref)

#
# Check Value of Objects
#

def is_subset(a: str, seta: set, b: str, setb: set) -> None:
    """Check if set is a subset of another set."""
    if not seta.issubset(setb):
        raise NotIsSubsetError(a, seta, b, setb)

def is_positive(name: str, obj: RealNumber) -> None:
    """Check if number is positive."""
    if obj <= 0:
        raise NotIsPositiveError(name, obj)

def is_negative(name: str, obj: RealNumber) -> None:
    """Check if number is negative."""
    if obj >= 0:
        raise NotIsNegativeError(name, obj)

def is_not_positive(name: str, obj: RealNumber) -> None:
    """Check if number is not positive."""
    if obj > 0:
        raise IsPositiveError(name, obj)

def is_not_negative(name: str, obj: RealNumber) -> None:
    """Check if number is not negative."""
    if obj < 0:
        raise IsNegativeError(name, obj)

def has_size(
        name: str, obj: Sized, min_size: OptInt = None,
        max_size: OptInt = None) -> None:
    """Check if sized object has a size between given bounds."""
    num = len(obj)
    if min_size and num < min_size:
        raise MinSizeError(name, obj, min_size)
    if max_size and num > max_size:
        raise MaxSizeError(name, obj, max_size)

#
# Check Properties of an Object
#

def has_attr(obj: object, attr: str) -> None:
    """Check if object has an attribute."""
    if not hasattr(obj, attr):
        raise NotHasAttrError(obj, attr)
