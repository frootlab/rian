# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def isdataset(object):
    """Return true if the object is a dataset instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'dataset'

def isnetwork(object):
    """Return true if the object is a network instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'network'

def issystem(object):
    """Return true if the object is a system instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'system'

def ismodel(object):
    """Return true if the object is a model instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'model'
