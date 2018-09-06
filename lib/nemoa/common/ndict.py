# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Dict, Hashable

def merge(*args: dict, new: bool = True) -> dict:
    """Recursive right merge dictionaries.

    Args:
        *args: dictionaries with arbitrary hirarchy structures
        new: a new dictionary is created if new is True

    Returns:
        Dictionary containing right merge of dictionaries.

    Examples:
        >>> merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3})
        {'a': 1, 'b': 2, 'c': 3}

    """

    # recursively right merge
    if len(args) < 2:
        raise TypeError("at least two arguments are required")
    elif len(args) == 2:
        d1, d2 = args[0], args[1]
    else:
        d1, d2, new = args[0], merge(*args[1:], new = new), False

    # check types of arguments
    if not isinstance(d1, dict):
        raise TypeError("first argument requires type "
            f"'dict', not '{type(d1)}'")
    if not isinstance(d2, dict):
        raise TypeError("second argument requires type "
            f"'dict', not '{type(d2)}'")

    # create new dictionary
    if new:
        import copy
        d2 = copy.deepcopy(d2)

    # right merge couple of dictionaries
    for k1, v1 in d1.items():
        if k1 not in d2: d2[k1] = v1
        elif isinstance(v1, dict): merge(v1, d2[k1], new = False)
        else: d2[k1] = v1

    return d2

def reduce(d: dict, s: str, trim: bool = True) -> dict:
    """Crop dictionary to keys, that start with an initial string.

    Args:
        d: Dictionary that encodes sections by the prefix of string keys
        s: Section prefix as string
        trim: Determines if the section prefix is removed from the keys of the
            returned dictionary. Default: True

    Returns:
        Subdictionary of the original dictionary, which only contains keys
        that start with the given section. Thereby the new keys are trimmed
        from the initial section string.

    Examples:
        >>> reduce({'a1': 1, 'a2': 2, 'b1': 3}, 'a')
        {'1': 1, '2': 2}

    """

    # check argument types
    if not isinstance(d, dict):
        raise TypeError("first argument is required to be "
            f"of type dict, not '{type(d)}'")
    if not isinstance(s, str):
        raise TypeError("second argument is required to be "
            "of type string, not '{type(s)}'")

    # create new dictionary
    i = len(s)
    if trim:
        sec = {k[i:]: v for k, v in d.items() \
            if isinstance(k, str) and k[:i] == s}
    else:
        sec = {k: v for k, v in d.items() \
            if isinstance(k, str) and k[:i] == s}

    return sec

def groupby(d: Dict[Hashable, dict], key: Hashable) -> Dict[Hashable, dict]:
    """Group dictionary by the value of a given key of subdictionaries.

    Args:
        d: Dictionary of dictionaries, which entries are interpreted as
            elements and attributes.
        key: Name of attribute which is used to group the results by it's
            corresponding value.

    Returns:
        Dictinary which groups the entries of the original dictinary in
        subdictionaries.

    """

    gd = dict()
    for k, v in d.items():
        g = v.get(key, None)
        if not g in gd: gd[g] = dict()
        gd[g][k] = v

    return gd


def strkeys(d: dict) -> dict:
    """Recursively convert dictionary keys to string keys.

    Args:
        d: Hierarchivally structured dictionary with keys of arbitrary types.

    Returns:
        New dictionary with string converted keys. Thereby keys of type tuple
        are are not converted as a whole but with respect to the tokens in
        the tuple.

    Examples:
        >>> strkeys({(1, 2): 3, None: {True: False}})
        {('1', '2'): 3, 'None': {'True': False}}

    """

    # if argument is not a dictionary, return it for recursion
    if not isinstance(d, dict): return d

    # create new dictionary with string keys
    dn = {}
    for k, v in list(d.items()):
        if not isinstance(k, tuple): kn = str(k)
        else: kn = tuple([str(t) for t in k])
        dn[kn] = strkeys(v)

    return dn

def sumjoin(*args: dict) -> dict:
    """Sum values of common keys in differnet dictionaries.

    Args:
        *args: dictionaries, that are recursively right merged

    Returns:
        New dictionary, where items with keys, that only occur in a single
        dictionary are adopted and items with keys, that occur in multiple
        dictionaries are united by a sum.

    Examples:
        >>> sumjoin({'a': 1}, {'a': 2, 'b': 3})
        {'a': 3, 'b': 3}
        >>> sumjoin({1: 'a', 2: True}, {1: 'b', 2: True})
        {1: 'ab', 2: 2}

    """

    dn = {}
    for d in args:
        if not isinstance(d, dict): continue
        for k, v in d.items():
            if k in dn:
                if not isinstance(dn[k], type(v)): continue
                dn[k] += v
            else: dn[k] = v

    return dn
