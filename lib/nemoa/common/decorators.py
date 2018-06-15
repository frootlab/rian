# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

def attributes(**attr):
    """Generic attribute decorator for arbitrary class methods."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.items():
            setattr(wrapped, key, val)

        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper

def algorithm(**attr):
    """Attribute decorator for algorithm methods."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.items():
            setattr(wrapped, key, val)

        setattr(wrapped, 'func', method)
        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper
