# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import os
import sys
import functools

from nemoa.core import log
from nemoa.types import Any, OptStr, Traceback

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def excepthook(etype: type, value: Any, tb: Traceback) -> None:
    """ """
    exc_info = (etype, value, tb)
    log.exception(str(value), exc_info=exc_info)

def bypass_exceptions(func, interrupt: bool = False):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        etype = sys.exc_info()[0]
        if not issubclass(etype, Exception):
            return func(*args, **kwds)
        if interrupt:
            return excepthook(*sys.exc_info())
        excepthook(*sys.exc_info())
        return func(*args, **kwds)
    return wrapper

def bypass_python_exepthook() -> None:
    """Bypass exceptions from sys.excepthook."""
    sys.excepthook = bypass_exceptions(sys.excepthook)
