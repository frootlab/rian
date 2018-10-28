# -*- coding: utf-8 -*-
"""Exceptions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import assess
from nemoa.types import Class, ClassInfo, Number

#
# Informative Object Representation
#

def _repr_classinfo(obj: ClassInfo) -> str:
    if isinstance(obj, type):
        return obj.__name__.join(["'", "'"])
    if isinstance(obj, tuple):
        names = [getattr(each, '__name__', '?') for each in obj]
        return "' or '".join(names).join(["'", "'"])
    return '?'

def _repr_set(obj: set) -> str:
    if len(obj) > 3:
        return "some elements"
    if len(obj) > 1:
        names = [str(o) for o in obj]
        return "elements " + "' and '".join(names).join(["'", "'"])
    e = ''
    for e in obj:
        break
    return f"element '{e}'"

def _repr_type(obj: object) -> str:
    return f"'{type(obj).__name__}'"

def _repr_obj(obj: object) -> str:
    return f"'{assess.get_name(obj)}'"

def _format_msg(msg: str) -> str:
    return msg.strip('.').capitalize()

################################################################################
# Generic Exceptions
################################################################################

class NmException(Exception):
    """Base class for exceptions in nemoa."""

class NmError(NmException):
    """Exception for errors in nemoa."""

class NmWarning(Warning, NmException):
    """Exception for warnings in nemoa."""

class NmAssert(AssertionError, NmException):
    """Exception for assertions in nemoa."""

################################################################################
# Assertion Errors
################################################################################

class WrongTypeError(TypeError, NmAssert):
    """Raise when an object is required to be of a given type."""

    def __init__(self, name: str, obj: object, classinfo: ClassInfo) -> None:
        this = _repr_classinfo(classinfo)
        that = _repr_type(obj)
        msg = f"{name} requires to be of type {this} not {that}"
        super().__init__(_format_msg(msg))

class NotIsSubclassError(TypeError, NmAssert):
    """Raise when an object is required to be of a given subclass."""

    def __init__(self, name: str, obj: object, ref: Class) -> None:
        this = _repr_obj(ref)
        that = _repr_obj(obj)
        msg = f"{name} requires to be a subclass of {this} not {that}"
        super().__init__(_format_msg(msg))

class NotIsClassError(TypeError, NmAssert):
    """Raise when an object is required to be of a class."""

    def __init__(self, name: str, obj: object) -> None:
        that = _repr_type(obj)
        msg = f"{name} requires to be a class not {that}"
        super().__init__(_format_msg(msg))

class NotIsCallableError(TypeError, NmAssert):
    """Raise when an object is required to be callable."""

    def __init__(self, name: str, obj: object) -> None:
        that = _repr_type(obj)
        msg = f"{name} requires to be callable not {that}"
        super().__init__(_format_msg(msg))

class NotIsSubsetError(ValueError, NmAssert):
    """Raise when a set not is a subset of another."""

    def __init__(self, a: str, seta: set, b: str, setb: set) -> None:
        diff = seta - setb
        elements = _repr_set(diff)
        are = 'are' if len(diff) > 1 else 'is'
        msg = f"{elements} of {a} {are} not contained in {b}"
        super().__init__(_format_msg(msg))

class IsNegativeError(ValueError, NmAssert):
    """Raise when a number may not be negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a positive number not {val}"
        super().__init__(_format_msg(msg))

class NotIsPositiveError(ValueError, NmAssert):
    """Raise when a number must be strictly positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly positive number not {val}"
        super().__init__(_format_msg(msg))

class IsPositiveError(ValueError, NmAssert):
    """Raise when a number may not be positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required not to be a negative number not {val}"
        super().__init__(_format_msg(msg))

class NotIsNegativeError(ValueError, NmAssert):
    """Raise when a number must be strictly negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly negative number not {val}"
        super().__init__(_format_msg(msg))

################################################################################
# Attribute Errors
################################################################################

class ReadOnlyError(AttributeError, NmError):
    """Raise when a read-only attributes setter method is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = _repr_type(obj)
        msg = f"'{attr}' is a read-only property of {that}"
        super().__init__(_format_msg(msg))

class NotHasAttrError(AttributeError, NmError):
    """Raise when a not existing attribute is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = _repr_type(obj)
        msg = f"{that} has no attribute '{attr}'"
        super().__init__(_format_msg(msg))

################################################################################
# File Errors
################################################################################

class DirNotEmptyError(OSError, NmError):
    """Raise on remove() requests on a non-empty directory."""

class FileNotGivenError(OSError, NmError):
    """Raise when a file or directory is required but not given."""

################################################################################
# Singleton Design Errors
################################################################################

class AlreadyStartedError(LookupError, NmError):
    """Raise when a singleton process shall be started twice."""

class NotStartedError(LookupError, NmError):
    """Raise when a singleton process is called but not has been started."""
