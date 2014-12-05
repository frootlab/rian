# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def attributes(**attr):
    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.iteritems():
            setattr(wrapped, key, val)
        return wrapped
    return wrapper
