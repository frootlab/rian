# -*- coding: utf-8 -*-
"""Extended handling of collection type objects like dictionaries."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import fnmatch
from nemoa.base import check
from nemoa.types import RecDict, DictOfRecDicts, StrTupleDict, OptStr

def merge(*args: dict, mode: int = 1) -> dict:
    """Recursive right merge dictionaries.

    Args:
        *args: dictionaries with arbitrary hirarchy structures
        mode: creation mode for resulting dictionary:
            0: change rightmost dictionary
            1: create new dictionary by deepcopy
            2: create new dictionary by chain mapping

    Returns:
        Dictionary containing right merge of dictionaries.

    Examples:
        >>> merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3})
        {'a': 1, 'b': 2, 'c': 3}

    """
    # Check for trivial cases
    if not args:
        return {}
    if len(args) == 1:
        return args[0]

    # Check for chain mapping creation mode
    if mode == 2:
        import collections
        return dict(collections.ChainMap(*args))

    # Recursively right merge
    if len(args) == 2:
        d1, d2 = args[0], args[1]
    else:
        d1, d2 = args[0], merge(*args[1:], mode=mode)
        mode = 0

    # Check Type of first and second argument
    check.has_type("first argument", d1, dict)
    check.has_type("second argument", d2, dict)

    # Create new dictionary
    if mode == 1:
        import copy
        d2 = copy.deepcopy(d2)

    # Right merge couple of dictionaries
    for k1, v1 in d1.items():
        if k1 not in d2:
            d2[k1] = v1
        elif isinstance(v1, dict):
            merge(v1, d2[k1], mode=0)
        else: d2[k1] = v1

    return d2

def select(d: dict, pattern: str) -> dict:
    """Filter dictionary to keys, that match a given pattern.

    Args:
        d: Dictionary with string keys
        pattern: Wildcard pattern as described in the standard library module
            :py:mod:`fnmatch`.

    Returns:
        Subdictionary of the original dictionary, which only contains keys
        that match the given pattern

    Examples:
        >>> filter({'a1': 1, 'a2': 2, 'b1': 3}, 'a*')
        {'a1': 1, 'a2': 2}

    """
    # Check Type of 'd'
    if not isinstance(d, dict):
        raise TypeError(
            "first argument 'd' is required to be of type dict"
            f", not '{type(d).__name__}'")

    # Check Type of 'pattern'
    if not isinstance(pattern, str):
        raise TypeError(
            "second argument 'pattern' is required to be of type string"
            f", not '{type(pattern).__name__}'")

    valid = fnmatch.filter(list(d.keys()), pattern)

    return {k: d[k] for k in valid}

def crop(d: dict, prefix: str, trim: bool = True) -> dict:
    """Crop dictionary to keys, that start with an initial string.

    Args:
        d: Dictionary that encodes sections by the prefix of string keys
        prefix: Key prefix as string
        trim: Determines if the section prefix is removed from the keys of the
            returned dictionary. Default: True

    Returns:
        Subdictionary of the original dictionary, which only contains keys
        that start with the given section. Thereby the new keys are trimmed
        from the initial section string.

    Examples:
        >>> crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a')
        {'1': 1, '2': 2}

    """
    # Check Type of 'd'
    if not isinstance(d, dict):
        raise TypeError(
            "first argument 'd' is required to be of type dict"
            f", not '{type(d).__name__}'")

    # Check type of 'prefix'
    if not isinstance(prefix, str):
        raise TypeError(
            "second argument 'prefix' is required to be of type string"
            f", not '{type(prefix).__name__}'")

    # Create new dictionary with section
    i = len(prefix)
    if trim:
        section = {k[i:]: v for k, v in d.items() \
            if isinstance(k, str) and k[:i] == prefix}
    else:
        section = {k: v for k, v in d.items() \
            if isinstance(k, str) and k[:i] == prefix}

    return section

def flatten(d: DictOfRecDicts, group: OptStr = None) -> RecDict:
    """Flatten grouped record dictionary by given group name.

    Inverse dictionary operation to 'groupby'.

    Args:
        d: Nested dictionary, which entries are interpreted as attributes.
        group: Attribute names, which describes the groups.

    Returns:
        Dictinary which flattens the groups of the original dictinary to
        attributes.

    Examples:
        >>> flatten({1: {'a': {}}, 2: {'b': {}}})
        {'a': {}, 'b': {}}
        >>> flatten({1: {'a': {}}, 2: {'b': {}}}, group='id')
        {'a': {'id': 1}, 'b': {'id': 2}}

    """
    # Declare and initialize return value
    rd: RecDict = {}

    # Do not create group attribute, if not given
    if not group:
        rd = merge(*tuple(d.values()))
        return rd

    for gval, sub in d.items():
        for key, attr in sub.items():
            attr[group] = gval
            rd[key] = attr

    return rd

def groupby(d: RecDict, key: str, rmkey: bool = False) -> DictOfRecDicts:
    """Group record dictionary by the value of a given key.

    Args:
        d: Dictionary of dictionaries, which entries are interpreted as
            attributes.
        key: Name of attribute which is used to group the results by it's
            corresponding value.
        rmkey: Boolean which determines, if the group attribute is removed from
            the the sub dictionaries.

    Returns:
        Dictinary which groups the entries of the original dictinary in
        subdictionaries.

    """
    # Declare and initialize return value
    rd: DictOfRecDicts = {}

    for k, attr in d.items():
        if rmkey:
            gval = attr.pop(key, None)
        else:
            gval = attr.get(key, None)
        if not gval in rd:
            rd[gval] = {}
        rd[gval][k] = attr

    return rd

def strkeys(d: dict) -> StrTupleDict:
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
    # If argument is not a dictionary, return it for recursion
    if not isinstance(d, dict):
        return d

    # Declare and initialize return value
    dn: StrTupleDict = {}

    # Create new dictionary with string keys
    for k, v in d.items():
        if isinstance(k, tuple):
            dn[tuple([str(t) for t in k])] = strkeys(v)
        else:
            dn[str(k)] = strkeys(v)

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
    dn: dict = {}
    for d in args:
        if not isinstance(d, dict):
            continue
        for k, v in d.items():
            if k in dn:
                if not isinstance(dn[k], type(v)):
                    continue
                dn[k] += v
            else: dn[k] = v

    return dn
