# -*- coding: utf-8 -*-
"""Exceptions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import entity
from nemoa.types import Any, Class, Number, Sized

################################################################################
# Generic Application Exceptions
################################################################################

class NemoaException(Exception):
    """Base class for exceptions in nemoa."""

    def __init__(self, msg: str):
        super().__init__(msg.strip(' .'))

class NemoaError(NemoaException):
    """Exception for standard errors in nemoa."""

class NemoaWarning(NemoaException, Warning):
    """Exception for warnings in nemoa."""

class NemoaAssert(NemoaError, AssertionError):
    """Exception for assertions in nemoa."""

################################################################################
# Application specific Type Errors
################################################################################

class MissingKwError(NemoaAssert, TypeError):
    """Raise when a required keyword argument is not given."""

    def __init__(self, name: str, obj: object) -> None:
        this = entity.get_name(obj)
        msg = f"{this} missing required keyword argument '{name}'"
        super().__init__(msg)

class InvalidTypeError(NemoaAssert, TypeError):
    """Raise when an object is required to be of a given type."""

    def __init__(self, name: str, obj: object, classinfo: object) -> None:
        this = entity.get_lang_repr(classinfo, separator='or')
        that = entity.get_name(type(obj))
        msg = f"{name} requires to be of type {this} not {that}"
        super().__init__(msg)

class InvalidClassError(NemoaAssert, TypeError):
    """Raise when an object is required to be of a given subclass."""

    def __init__(self, name: str, obj: object, ref: Class) -> None:
        this = entity.get_name(ref)
        that = entity.get_name(obj)
        msg = f"{name} requires to be a subclass of {this} not {that}"
        super().__init__(msg)

class NotClassError(NemoaAssert, TypeError):
    """Raise when an object is required to be a class."""

    def __init__(self, name: str, obj: object) -> None:
        that = entity.get_name(type(obj))
        msg = f"{name} requires to be a class not {that}"
        super().__init__(msg)

class NotCallableError(NemoaAssert, TypeError):
    """Raise when an object is required to be callable."""

    def __init__(self, name: str, obj: object) -> None:
        that = entity.get_name(type(obj))
        msg = f"{name} requires to be callable not {that}"
        super().__init__(msg)

################################################################################
# Application specific Value Errors
################################################################################

class InvalidFormatError(NemoaAssert, ValueError):
    """Rasise when a string has an invalid format."""

    def __init__(self, name: str, val: str, fmt: str) -> None:
        msg = f"{name} '{val}' does not have the required format {fmt}"
        super().__init__(msg)

class IsNegativeError(NemoaAssert, ValueError):
    """Raise when a number may not be negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a positive number not {val}"
        super().__init__(msg)

class NotPositiveError(NemoaAssert, ValueError):
    """Raise when a number has strictly to be positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly positive number not {val}"
        super().__init__(msg)

class IsPositiveError(NemoaAssert, ValueError):
    """Raise when a number may not be positive."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required not to be a negative number not {val}"
        super().__init__(msg)

class NotNegativeError(NemoaAssert, ValueError):
    """Raise when a number has strictly to be negative."""

    def __init__(self, name: str, val: Number) -> None:
        msg = f"{name} is required to be a strictly negative number not {val}"
        super().__init__(msg)

class NotInSequenceError(NemoaAssert, ValueError):
    """Raise when an element is not contained within a sequence."""

    def __init__(self, name: str, val: Any, seqname: str) -> None:
        msg = f"value {val} of {name} is not contained in {seqname}"
        super().__init__(msg)

class NoSubsetError(NemoaAssert, ValueError):
    """Raise when sequence elements are not contained within another."""

    def __init__(self, a: str, seta: set, b: str, setb: set) -> None:
        diff = set(seta) - set(setb)
        elements = entity.get_lang_repr(diff)
        are = 'are' if len(diff) > 1 else 'is'
        msg = f"{elements} of {a} {are} not contained in {b}"
        super().__init__(msg)

class SizeError(NemoaAssert, ValueError):
    """Raise when a sized object has an invalid size."""

    def __init__(self, name: str, obj: Sized, size: int) -> None:
        msg = (
            f"{name} contains {len(obj)} elements"
            f", but exactly {size} are required")
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
# Application specific Attribute Errors
################################################################################

class InvalidAttrError(NemoaAssert, AttributeError):
    """Raise when a not existing attribute is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = entity.get_name(obj)
        msg = f"{that} has no attribute '{attr}'"
        super().__init__(msg)

class ReadOnlyAttrError(NemoaAssert, AttributeError):
    """Raise when a read-only attribute's setter method is called."""

    def __init__(self, obj: object, attr: str) -> None:
        that = entity.get_name(obj)
        msg = f"'{attr}' is a read-only attribute of {that}"
        super().__init__(msg)

################################################################################
# Application specific OS Errors
################################################################################

class DirNotEmptyError(NemoaAssert, OSError):
    """Raise on remove() requests on a non-empty directory."""

class FileNotGivenError(NemoaAssert, OSError):
    """Raise when a file or directory is required but not given."""

################################################################################
# Application specific Lookup Errors
################################################################################

class ExistsError(NemoaAssert, LookupError):
    """Raise when an existing singleton shall be created."""

class NotExistsError(NemoaAssert, LookupError):
    """Raise when a non existing singleton shall be destructed."""
