# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError: raise ImportError(
    "nemoa.common.dict requires numpy: "
    "https://scipy.org")

from typing import Optional

def dict_to_array(d: dict, axes: tuple, na: float = 0.) -> numpy.ndarray:
    """Convert dictionary to 2d numpy ndarray."""

    a = numpy.empty(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in enumerate(axes[1]):
            a[i, j] = d[(x, y)] if (x, y) in d else na

    return a

def array_to_dict(a: numpy.ndarray, axes: tuple,
    na: Optional[float] = None) -> dict:
    """Convert 2d numpy ndarray to dictionary."""

    d = {}
    for i, x in enumerate(axes[0]):
        for j, y in enumerate(axes[1]):
            if not na == None and a[i, j] == na: continue
            d[(x, y)] = a[i, j]

    return d

def merge(*args, new: bool = True) -> dict:
    """Recursively right merge dictionaries.

    Args:
        d1 (dict): dictionary
        d2 (dict): target dictionary
        ...

    Kwargs:
        new (bool, optional): a new dictionary is created if new is True

    Returns:
        Dictionary containing right merge of dictionaries.

    """

    # recursively right merge
    if len(args) < 2: raise TypeError(
        'at least two arguments are required.')
    elif len(args) > 2:
        d1, d2 = args[0], merge(*args[1:], new = new)
        new = False
    else:
        d1, d2 = args[0], args[1]

    # check types of arguments
    if not type(d1) is dict: raise TypeError(
        'first argument is required to be of type dict.')
    if not type(d2) is dict: raise TypeError(
        'second argument is required to be of type dict.')

    # create new dictionary
    if new:
        import copy
        d2 = copy.deepcopy(d2)

    for k1, v1 in d1.items():
        if not k1 in d2: d2[k1] = v1
        elif isinstance(v1, dict):
            merge(v1, d2[k1], new = False)
        else: d2[k1] = v1

    return d2

def section(d: dict, s: str) -> dict:
    """Crop dictionary to keys, that start with an initial string."""

    # check types of arguments
    if not type(d) is dict: raise TypeError(
        'first argument is required to be of type dict.')
    if not type(s) is str: raise TypeError(
        'second argument is required to be of type string.')

    i = len(s)

    return {k[i:]: v for k, v in list(d.items()) \
        if isinstance(k, str) and k[:i] == s}

def strkeys(d: dict) -> dict:
    """Recursively convert dictionary keys to string."""

    if not type(d) is dict: return d

    dnew = {}
    for key, val in list(d.items()):
        if not isinstance(key, tuple): keynew = str(key)
        else: keynew = tuple([str(token) for token in key])
        dnew[keynew] = strkeys(val)

    return dnew

def sumjoin(*args) -> dict:
    """Sum values of common keys in differnet dictionaries."""

    dsum = {}
    for d in args:
        if not type(d) is dict: continue
        for key, val in d.items():
            if key in dsum:
                if not type(dsum[key]) == type(val): continue
                dsum[key] += val
            else: dsum[key] = val

    return dsum
