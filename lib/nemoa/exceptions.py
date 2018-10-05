# -*- coding: utf-8 -*-
"""Application specific Exceptions.

Base exceptions and errors for nemoa.
"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

class DirNotEmptyError(OSError):
    """Exception for remove() requested on a non empty directory."""

class NemoaException(Exception):
    """Base class for exceptions in nemoa."""

class NemoaError(NemoaException):
    """Exception for a serious error in nemoa."""

class NemoaWarning(NemoaException):
    """Exception for warnings in nemoa."""

class BadWorkspaceFile(NemoaError):
    """Exception for invalid nemoa workspace files."""
