# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
import os
import sys

from nemoa.core import log
from nemoa.types import Any, AnyFunc, ExcType, ExcValue, ExcTraceback

def clear() -> None:
    """Clear screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def excepthook(etype: ExcType, value: ExcValue, tb: ExcTraceback) -> None:
    """Alternative exception hook."""
    exc_info = (etype, value, tb)
    log.exception(str(value), exc_info=exc_info)

def bypass_exceptions(func: AnyFunc, interrupt: bool = False) -> AnyFunc:
    """Bypass exceptions from given function."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwds: Any) -> Any:
        etype = sys.exc_info()[0]
        if etype and not issubclass(etype, Exception):
            return func(*args, **kwds)
        if interrupt:
            return excepthook(*sys.exc_info())
        excepthook(*sys.exc_info())
        return func(*args, **kwds)
    return wrapper

def bypass_python_exepthook() -> None:
    """Bypass exceptions from sys.excepthook."""
    sys.excepthook = bypass_exceptions(sys.excepthook)
