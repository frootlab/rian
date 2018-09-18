# -*- coding: utf-8 -*-
"""Collection of frequently functions for multitreading."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import threading

from nemoa.common.ntype import Any, AnyFunc, Obj

def thread(func: AnyFunc, *args: Any, **kwargs: Any) -> Obj:
    """Create and start thread for given callable and arguments."""
    thr = threading.Thread(
        target=(lambda func, args, kwargs: func(*args, **kwargs)),
        args=(func, args, kwargs))

    thr.daemon = True
    thr.start()

    return thr
