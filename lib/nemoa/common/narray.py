# -*- coding: utf-8 -*-
"""Collection of frequently used numpy ndarray functions."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common.ntype import StrPairDict, StrListPair, NpArray, OptFloat

#
#  Array Conversion Functions
#

def fromdict(d: StrPairDict, labels: StrListPair, na: float = 0.) -> NpArray:
    """Convert dictionary to array.

    Args:
        d: Dictionary of format {(<row>, <col>): value, ...}, where:
            <row> is an element of the <row list> of the argument labels and
            <col> is an element of the <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...].
        na: Value to mask NA (Not Available) entries. Missing entries in the
            dictionary are replenished by the NA value in the array.

    Returns:
        Numpy ndarray of shape (n, m), where n equals the length of the
        <row list> of the argument labels and m equals the length of the
        <col list> of the argument labels.

    """
    # Declare and initialize return value
    array: NpArray = np.empty(shape=(len(labels[0]), len(labels[1])))

    # Get numpy ndarray
    setitem = getattr(array, 'itemset')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            setitem((i, j), d.get((row, col), na))

    return array

def asdict(
        x: NpArray, labels: StrListPair, na: OptFloat = None) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        x: Numpy ndarray of shape (n, m), where n equals the length of the
            <row list> of the argument labels and m equals the length of the
            <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...]
        na: Optional value to mask NA (Not Available) entries. For cells in the
            array, which have this value, no entry in the returned dictionary
            is created.

    Returns:
        Dictionary of format {(<row>, <col>): value, ...}, where:
        <row> is an element of the <row list> of the argument labels and
        <col> is an element of the <col list> of the argument labels.

    """
    # Check argument 'x'
    if not hasattr(x, 'item'):
        raise TypeError(
            "argument 'x' is required to by of type 'ndarray'"
            f", not '{type(x)}'")

    # Declare and initialize return value
    d: StrPairDict = {}

    # Get dictionary with pairs as keys
    getitem = getattr(x, 'item')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            val = getitem(i, j)
            if na is None or val != na:
                d[(row, col)] = val

    return d
