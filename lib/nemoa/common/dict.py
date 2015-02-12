# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def asarray(d, axes):
    """Return 2-dimensional numpy array from dictionary."""

    array = numpy.zeros(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in enumerate(axes[1]):
            array[i, j] = d[(x, y)] if (x, y) in dict else 0.

    return array

def fromarray(array, axes):
    """Return dictionary from 2-dimensional numpy array."""

    d = {}
    for i, x in enumerate(axes[0]):
        for j, y in enumerate(axes[1]):
            d[(x, y)] = array[i, j]

    return d

def merge(d1, d2, new = True):
    """Recursively merge dictionaries (merge d1 over d2).

    Args:
        new (bool): a new dictionary is created if new is True

    Returns:
        Dictionary containing right merge from d1 and d2.

    """

    if new:
        import copy
        d2 = copy.deepcopy(d2)

    for k1, v1 in d1.iteritems():
        if not k1 in d2: d2[k1] = v1
        elif isinstance(v1, dict): merge(v1, d2[k1], new = False)
        else: d2[k1] = v1

    return d2

def strkeys(d):
    """Recursively convert dictionary keys to string."""

    if not isinstance(d, dict): return d
    dnew = {}
    for key, val in d.items():
        if not isinstance(key, tuple): keynew = str(key)
        else: keynew = tuple([str(token) for token in key])
        dnew[keynew] = strkeys(val)

    return dnew

def sumjoin(*args):
    """Sum values of common keys in differnet dictionaries."""

    dsum = {}
    for d in args:
        if not isinstance(d, dict): continue
        for key, val in d.iteritems():
            if key in dsum:
                if not type(dsum[key]) == type(val): continue
                dsum[key] += val
            else: dsum[key] = val

    return dsum
