# -*- coding: utf-8 -*-
"""Assert functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
import typing
from nemoa.errors import IsPositiveError, IsNegativeError, SizeError
from nemoa.errors import InvalidTypeError, InvalidClassError, NotClassError
from nemoa.errors import NotCallableError, InvalidAttrError, NoSubsetError
from nemoa.errors import NotPositiveError, NotNegativeError, MinSizeError
from nemoa.errors import MaxSizeError, InvalidFormatError
from nemoa.types import Class, ClassInfo, Sized, RealNumber, OptInt
from nemoa.types import ClassInfoClasses

#
# Check Type of Objects
#

def has_type(name: str, obj: object, classinfo: ClassInfo) -> None:
    """Check type of object."""

    # Check against ClassInfo
    if isinstance(classinfo, ClassInfoClasses):
        if isinstance(obj, classinfo):
            return
        raise InvalidTypeError(name, obj, classinfo)

    # Check against assorted Structural Types
    if classinfo == typing.Any:
        return
    if classinfo == typing.Callable:
        try:
            is_callable(name, obj)
        except NotCallableError as err:
            raise InvalidTypeError(name, obj, classinfo) from err
        return
    if hasattr(classinfo, '__origin__'):
        has_type(name, obj, getattr(classinfo, '__origin__'))

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

def is_identifier(name: str, string: str) -> None:
    """Check if a string is a valid identifier."""
    if not string.isidentifier():
        raise InvalidFormatError(name, string, "'UAX-31'")

def is_subset(a: str, seta: set, b: str, setb: set) -> None:
    """Check if a set is a subset of another."""
    if not seta.issubset(setb):
        raise NoSubsetError(a, seta, b, setb)

def is_positive(name: str, obj: RealNumber) -> None:
    """Check if number is positive."""
    if obj <= 0:
        raise NotPositiveError(name, obj)

def is_negative(name: str, obj: RealNumber) -> None:
    """Check if number is negative."""
    if obj >= 0:
        raise NotNegativeError(name, obj)

def is_not_positive(name: str, obj: RealNumber) -> None:
    """Check if number is not positive."""
    if obj > 0:
        raise IsPositiveError(name, obj)

def is_not_negative(name: str, obj: RealNumber) -> None:
    """Check if number is not negative."""
    if obj < 0:
        raise IsNegativeError(name, obj)

def has_size(
        name: str, obj: Sized, size: OptInt = None,
        min_size: OptInt = None, max_size: OptInt = None, ) -> None:
    """Check the size of a sized object."""
    num = len(obj)
    if size and num != size:
        raise SizeError(name, obj, size)
    if min_size and num < min_size:
        raise MinSizeError(name, obj, min_size)
    if max_size is not None and num > max_size:
        raise MaxSizeError(name, obj, max_size)

#
# Check Properties of an Object
#

def has_attr(obj: object, attr: str) -> None:
    """Check if object has an attribute."""
    if not hasattr(obj, attr):
        raise InvalidAttrError(obj, attr)
