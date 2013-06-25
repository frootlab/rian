# -*- coding: utf-8 -*-

# object functions

def isInstanceType(object, type):
    """
    Return true if the object is a instance of given class.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == type

def isDataset(object):
    """
    Return true if the object is a dataset instance.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'dataset'

def isNetwork(object):
    """
    Return true if the object is a network instance.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'network'

def isSystem(object):
    """
    Return true if the object is a system instance.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'system'

def isModel(object):
    """
    Return true if the object is a model instance.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'model'

def isPlot(object):
    """
    Return true if the object is a plot instance.
    """
    return hasattr(object, '__module__') \
        and object.__module__.split('.')[1] == 'plot'
