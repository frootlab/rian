# -*- coding: utf-8 -*-
"""Assert functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect

from nemoa.errors import (
    IsPositiveError, IsNegativeError,
    NotIsInstanceError, NotIsSubclassError, NotIsClassError, NotIsCallableError,
    NotHasAttrError, NotIsSubsetError, NotIsPositiveError, NotIsNegativeError)
from nemoa.types import Class, ClassInfo, RealNumber

#
# Check Type of Objects
#

def has_type(name: str, obj: object, classinfo: ClassInfo) -> None:
    """Check type of object."""
    if not isinstance(obj, classinfo):
        raise NotIsInstanceError(name, obj, classinfo)

def has_opt_type(name: str, obj: object, classinfo: ClassInfo) -> None:
    """Check type of optional object."""
    if obj is not None and not isinstance(obj, classinfo):
        raise NotIsInstanceError(name, obj, classinfo)

def is_callable(name: str, obj: object) -> None:
    """Check if object is callable."""
    if not callable(obj):
        raise NotIsCallableError(name, obj)

def is_class(name: str, obj: object) -> None:
    """Check if object is a class."""
    if not inspect.isclass(obj):
        raise NotIsClassError(name, obj)

def is_subclass(name: str, obj: object, ref: Class) -> None:
    """Check if object is a subclass of given class."""
    if not inspect.isclass(obj) or not issubclass(obj, ref): # type: ignore
        raise NotIsSubclassError(name, obj, ref)

#
# Check Value of Objects
#

def is_subset(a: str, seta: set, b: str, setb: set) -> None:
    """Check if set is a subset of another set."""
    if not seta.issubset(setb):
        raise NotIsSubsetError(a, seta, b, setb)

def is_positive(name: str, val: RealNumber) -> None:
    """Check if number is positive."""
    if val <= 0:
        raise NotIsPositiveError(name, val)

def is_negative(name: str, val: RealNumber) -> None:
    """Check if number is negative."""
    if val >= 0:
        raise NotIsNegativeError(name, val)

def is_not_positive(name: str, val: RealNumber) -> None:
    """Check if number is not positive."""
    if val > 0:
        raise IsPositiveError(name, val)

def is_not_negative(name: str, val: RealNumber) -> None:
    """Check if number is not negative."""
    if val < 0:
        raise IsNegativeError(name, val)

#
# Check Properties of an Object
#

def has_attr(obj: object, attr: str) -> None:
    """Check if object has an attribute."""
    if not hasattr(obj, attr):
        raise NotHasAttrError(obj, attr)
