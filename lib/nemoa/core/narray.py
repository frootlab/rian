# -*- coding: utf-8 -*-
"""Supplementary NumPy ndarray functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.types import StrPairDict, StrListPair, NpArray, NaN, Num, OptNum

def fromdict(d: StrPairDict, labels: StrListPair, nan: Num = NaN) -> NpArray:
    """Convert dictionary to array.

    Args:
        d: Dictionary of format {(<row>, <col>): value, ...}, where:
            <row> is an element of the <row list> of the argument labels and
            <col> is an element of the <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...].
        nan: Value to mask Not Not a Number (NaN) entries. Missing entries in
            the dictionary are replenished by the NaN value in the array.
            Default: IEEE 754 floating point representation of NaN [1]

    Returns:
        Numpy ndarray of shape (n, m), where n equals the length of the
        <row list> of the argument labels and m equals the length of the
        <col list> of the argument labels.

    References:
        [1] https://ieeexplore.ieee.org/document/4610935/

    """
    # Check Type of Argument 'd'
    if not isinstance(d, dict):
        raise TypeError(
            "argument 'd' is required to by of type 'dict'"
            f", not '{type(d)}'")

    # Declare and initialize return value
    x: NpArray = np.empty(shape=(len(labels[0]), len(labels[1])))

    # Get NumPy ndarray
    setit = getattr(x, 'itemset')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            setit((i, j), d.get((row, col), nan))

    return x

def asdict(
        x: NpArray, labels: StrListPair, nan: OptNum = NaN) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        x: NumPy ndarray of shape (n, m), where n equals the length of the
            <row list> of the argument labels and m equals the length of the
            <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...]
        na: Optional value to mask Not a Number (NaN) entries. For cells in the
            array, which have this value, no entry in the returned dictionary
            is created. If nan is None, then for all numbers entries are
            created. Default: IEEE 754 floating point representation of NaN [1]

    Returns:
        Dictionary of format {(<row>, <col>): value, ...}, where:
        <row> is an element of the <row list> of the argument labels and
        <col> is an element of the <col list> of the argument labels.

    References:
        [1] https://ieeexplore.ieee.org/document/4610935/

    """
    # Check Type of Argument 'x'
    if not hasattr(x, 'ndim'):
        raise TypeError(
            "argument 'x' is required to by of type 'ndarray'"
            f", not '{type(x)}'")
    if getattr(x, 'ndim') != 2:
        raise TypeError(
            "ndarray 'x' is required to have dimension 2"
            f", not '{getattr(x, 'ndim')}'")

    # Declare and initialize return value
    d: StrPairDict = {}

    # Get dictionary with pairs as keys
    getit = getattr(x, 'item')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            val = getit(i, j)
            if nan is None or not np.isnan(val):
                d[(row, col)] = val

    return d
