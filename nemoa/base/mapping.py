# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Helper functions for mappings."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import copy
import fnmatch
from nemoa.base import check
from nemoa.types import RecDict, DictOfRecDicts, StrTupleDict, OptStr, Mapping

def merge(*args: Mapping, mode: int = 1) -> Mapping:
    """Recursively right merge mappings.

    Args:
        *args: Mappings with arbitrary structure
        mode: Creation mode for merged mapping:
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
        d2 = copy.deepcopy(d2)

    # Right merge couple of dictionaries
    for k1, v1 in d1.items():
        if k1 not in d2:
            d2[k1] = v1 # type: ignore
        elif isinstance(v1, dict):
            merge(v1, d2[k1], mode=0)
        else:
            d2[k1] = v1 # type: ignore

    return d2

def select(d: Mapping, pattern: str) -> dict:
    """Filter mappings to keys, that match a given pattern.

    Args:
        d: Mapping, which keys aregiven by strings
        pattern: Wildcard pattern as described in the standard library module
            :mod:`fnmatch`.

    Returns:
        Subset of the original mapping, which only contains keys, that match
        the given pattern.

    Examples:
        >>> select({'a1': 1, 'a2': 2, 'b1': 3}, 'a*')
        {'a1': 1, 'a2': 2}

    """
    # Check types
    check.has_type('d', d, Mapping)
    check.has_type('pattern', pattern, str)

    valid = fnmatch.filter(d.keys(), pattern)
    return {k: d[k] for k in valid}

def crop(d: Mapping, prefix: str, trim: bool = True) -> dict:
    """Crop mapping to keys, that start with an initial string.

    Args:
        d: Mapping that encodes sections by the prefix of string keys
        prefix: Key prefix as string
        trim: Determines if the section prefix is removed from the keys of the
            returned mapping. Default: True

    Returns:
        Subset of the original mapping, which only contains keys that start
        with the given section. Thereby the new keys are trimmed
        from the initial section string.

    Examples:
        >>> crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a')
        {'1': 1, '2': 2}

    """
    # Check types
    check.has_type('d', d, Mapping)
    check.has_type('prefix', prefix, str)

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

# def calc_hash(d: Mapping) -> int:
#     val = 0
#     for item in d.items():
#         val ^= hash(val)
#     return val
