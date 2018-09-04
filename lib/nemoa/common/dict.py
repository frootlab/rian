# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Optional

def merge(*args: dict, new: bool = True) -> dict:
    """Recursively right merge dictionaries.

    Args:
        *args (dict): dictionaries, that are recursively right merged
        new (bool, optional): a new dictionary is created if new is True

    Returns:
        Dictionary containing right merge of dictionaries.

    """

    # recursive right merge
    if len(args) < 2: raise TypeError('at least two arguments are required')
    elif len(args) == 2: d1, d2 = args[0], args[1]
    else: d1, d2, new = args[0], merge(*args[1:], new = new), False

    # check types of arguments
    if not isinstance(d1, dict): raise TypeError(
        f"first argument is required to be of type 'dict', not '{type(d1)}'")
    if not isinstance(d2, dict): raise TypeError(
        f"second argument is required to be of type 'dict', not '{type(d2)}'")

    # create new dictionary
    if new:
        import copy
        d2 = copy.deepcopy(d2)

    for k1, v1 in d1.items():
        if k1 not in d2: d2[k1] = v1
        elif isinstance(v1, dict): merge(v1, d2[k1], new = False)
        else: d2[k1] = v1

    return d2

def section(d: dict, s: str) -> dict:
    """Crop dictionary to keys, that start with an initial string."""

    # check argument types
    if not isinstance(d, dict): raise TypeError(
        'first argument is required to be of type dict.')
    if not isinstance(s, str): raise TypeError(
        'second argument is required to be of type string.')

    i = len(s)

    return {k[i:]: v for k, v in list(d.items()) \
        if isinstance(k, str) and k[:i] == s}

def strkeys(d: dict) -> dict:
    """Recursively convert dictionary keys to string."""

    # return non dictionary argument for recursion
    if not isinstance(d, dict): return d

    dnew = {}
    for key, val in list(d.items()):
        if not isinstance(key, tuple): keynew = str(key)
        else: keynew = tuple([str(token) for token in key])
        dnew[keynew] = strkeys(val)

    return dnew

def sumjoin(*args: dict) -> dict:
    """Sum values of common keys in differnet dictionaries."""

    dsum = {}
    for d in args:
        if not isinstance(d, dict): continue
        for key, val in d.items():
            if key in dsum:
                if not isinstance(dsum[key], type(val)): continue
                dsum[key] += val
            else: dsum[key] = val

    return dsum
