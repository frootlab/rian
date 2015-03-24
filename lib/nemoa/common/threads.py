# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def thread(function, *args, **kwargs):
    """ """

    import threading

    return threading.Thread(
        target = (lambda f, args, kwargs: f(*args, **kwargs)),
        args = (function, args, kwargs))
