# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def isInstanceType(object, type):
    """Return true if the object is a instance of given class."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == type

def is_dataset(object):
    """Return true if the object is a dataset instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'dataset'

def is_network(object):
    """Return true if the object is a network instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'network'

def is_system(object):
    """Return true if the object is a system instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'system'

def is_model(object):
    """Return true if the object is a model instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'model'

def isPlot(object):
    """Return true if the object is a plot instance."""
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'plot'
