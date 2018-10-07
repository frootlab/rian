# -*- coding: utf-8 -*-
"""Exceptions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

################################################################################
# OSError Exceptions
################################################################################

class DirNotEmptyError(OSError):
    """Raised on remove() requests on a non-empty directory."""

class FileNotGivenError(OSError):
    """Raised when a file or directory is required but not given."""

################################################################################
# Application specific Exceptions
################################################################################

class NemoaException(Exception):
    """Base class for exceptions in nemoa."""

class NemoaError(NemoaException):
    """Exception for a serious error in nemoa."""

class NemoaWarning(NemoaException):
    """Exception for warnings in nemoa."""

class BadWsFile(NemoaError):
    """Exception for invalid nemoa workspace files."""
