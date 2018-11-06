# -*- coding: utf-8 -*-
"""Exceptions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import assess
from nemoa.types import Class, Iterable, Number, Sized

#
# Object Representation
#

def _repr_classinfo(obj: object) -> str:
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, Iterable):
        return ' or '.join([_repr_classinfo(each) for each in obj])
    if isinstance(obj, type):
        return repr(obj.__name__)
    if hasattr(obj, '__repr__'):
        return repr(obj)
    return '?'

def _repr_set(obj: set) -> str:
    num = len(obj)
    if num == 0:
        return "no elements"
    if num > 3:
        return "some elements"
    if num > 1:
        names = [str(o) for o in obj]
        return "elements " + "' and '".join(names).join(["'", "'"])
    # Get single element without pop()
    return f"element '{obj.__iter__().__next__()}'"

def _repr_type(obj: object) -> str:
    return f"'{type(obj).__name__}'"

def _repr_obj(obj: object) -> str:
    return f"'{assess.get_name(obj)}'"

################################################################################
# Generic Exceptions
################################################################################

class NemoaException(Exception):
    """Base class for exceptions in nemoa."""

    def __init__(self, msg: str):
        super().__init__(msg.strip(' .'))

class NemoaError(NemoaException):
    """Exception for standard errors in nemoa."""

class NemoaWarning(NemoaException, Warning):
    """Exception for warnings in nemoa."""

################################################################################
# Assertion Errors
################################################################################

class NemoaAssert(NemoaError, AssertionError):
    """Exception for assertions in nemoa."""

class InvalidTypeError(NemoaAssert, TypeError):
    """Raise when an object is required to be of a given type."""

    def __init__(self, name: str, obj: object, classinfo: object) -> None:
        this = _repr_classinfo(classinfo)
        that = _repr_type(obj)
        msg = f"{name} requires to be of type {this} not {that}"
        super().__init__(msg)

class InvalidClassError(NemoaAssert, TypeError):
    """Raise when an object is required to be of a given subclass."""

    def __init__(self, name: str, obj: object, ref: Class) -> None:
        this = _repr_obj(ref)
        that = _repr_obj(obj)
        msg = f"{name} requires to be a subclass of {this} not {that}"
        super().__init__(msg)

class NotClassError(NemoaAssert, TypeError):
    """Raise when an object is required to be a class."""

    def __init__(self, name: str, obj: object) -> None:
        that = _repr_type(obj)
        msg = f"{name} requires to be a class not {that}"
        super().__init__(msg)

class NotCallableError(NemoaAssert, TypeError):
    """Raise when an object is required to be callable."""

    def __init__(self, name: str, obj: object) -> None:
        that = _repr_type(obj)
        msg = f"{name} requires to be callable not {that}"
        super().__init__(msg)

class IsNegativeError(NemoaAssert, ValueError):
    """Raise when a number may not be negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a positive number not {val}"
        super().__init__(msg)

class NotIsPositiveError(NemoaAssert, ValueError):
    """Raise when a number must be strictly positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly positive number not {val}"
        super().__init__(msg)

class IsPositiveError(NemoaAssert, ValueError):
    """Raise when a number may not be positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required not to be a negative number not {val}"
        super().__init__(msg)

class NotIsNegativeError(NemoaAssert, ValueError):
    """Raise when a number must be strictly negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly negative number not {val}"
        super().__init__(msg)

class NotIsSubsetError(NemoaAssert, ValueError):
    """Raise when a set not is a subset of another."""

    def __init__(self, a: str, seta: set, b: str, setb: set) -> None:
        diff = seta - setb
        elements = _repr_set(diff)
        are = 'are' if len(diff) > 1 else 'is'
        msg = f"{elements} of {a} {are} not contained in {b}"
        super().__init__(msg)

class MinSizeError(NemoaAssert, ValueError):
    """Raise when a sized object has too few elements."""

    def __init__(self, name: str, obj: Sized, min_len: int) -> None:
        msg = (
            f"{name} contains only {len(obj)} elements"
            f", but at least {min_len} are required")
        super().__init__(msg)

class MaxSizeError(NemoaAssert, ValueError):
    """Raise when a container has too many elements."""

    def __init__(self, name: str, obj: Sized, max_len: int) -> None:
        msg = (
            f"{name} contains {len(obj)} elements"
            f", but at most {max_len} are allowed")
        super().__init__(msg)

################################################################################
# Attribute Errors
################################################################################

class ReadOnlyError(AttributeError, NemoaError):
    """Raise when a read-only attributes setter method is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = _repr_type(obj)
        msg = f"'{attr}' is a read-only property of {that}"
        super().__init__(msg)

class NotHasAttrError(AttributeError, NemoaError):
    """Raise when a not existing attribute is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = _repr_type(obj)
        msg = f"{that} has no attribute '{attr}'"
        super().__init__(msg)

################################################################################
# File Errors
################################################################################

class DirNotEmptyError(OSError, NemoaError):
    """Raise on remove() requests on a non-empty directory."""

class FileNotGivenError(OSError, NemoaError):
    """Raise when a file or directory is required but not given."""

################################################################################
# Database interface (DBI) Exceptions
################################################################################

class DBIError(NemoaError):
    """Raise as standard error in database interfaces."""

class DBIWarning(NemoaWarning):
    """Raise as standard warning in database interfaces."""

################################################################################
# Singleton Errors
################################################################################

class SingletonExistsError(LookupError, NemoaError):
    """Raise when a singleton which allready exists shall be initialized."""

class NotStartedError(LookupError, NemoaError):
    """Raise when a singleton is closed but not has been initialized."""
