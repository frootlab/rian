# -*- coding: utf-8 -*-
"""Application specific Exceptions.

Base exceptions and errors for nemoa.
"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'


class NemoaException(Exception):
    """Base class for exceptions in nemoa."""

class NemoaError(NemoaException):
    """Exception for a serious error in nemoa."""

class NemoaWarning(NemoaException):
    """Exception for warnings in nemoa."""
