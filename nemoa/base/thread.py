# -*- coding: utf-8 -*-
"""Multithreading functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import threading
from nemoa.types import Any, AnyFunc

def create(func: AnyFunc, *args: Any, **kwds: Any) -> object:
    """Create and start thread for given callable and arguments."""
    thr = threading.Thread(
        target=(lambda func, args, kwds: func(*args, **kwds)),
        args=(func, args, kwds))

    thr.daemon = True
    thr.start()

    return thr
