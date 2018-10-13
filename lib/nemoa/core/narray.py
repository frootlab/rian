# -*- coding: utf-8 -*-
"""Supplementary NumPy ndarray functions.

.. References:
.. _IEEE 754: https://ieeexplore.ieee.org/document/4610935/

"""

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

def from_dict(d: StrPairDict, labels: StrListPair, nan: Num = NaN) -> NpArray:
    """Convert dictionary to array.

    Args:
        d: Dictionary with keys (<*row*>, <*col*>), where the elemns <*row*> are
            row labels from the list <*rows*> and <*col*> column labels from the
            list *columns*.
        labels: Tuple of format (<*rows*>, <*columns*>), where <*rows*> is a
            list of row labels, e.g. ['row1', 'row2', ...] and <*columns*> a
            list of column labels, e.g. ['col1', 'col2', ...].
        nan: Value to mask Not Not a Number (NaN) entries. Missing entries in
            the dictionary are replenished by the NaN value in the array.
            Default: `IEEE 754`_ floating point representation of NaN.

    Returns:
        NumPy ndarray of shape (*n*, *m*), where *n* equals the number of
        <*rows*> and *m* the number of <*columns*>.

    """
    # Check Type of Argument 'd'
    if not isinstance(d, dict):
        raise TypeError(
            "'d' is required to by of type 'dict'"
            f", not '{type(d).__name__}'")

    # Declare and initialize return value
    x: NpArray = np.empty(shape=(len(labels[0]), len(labels[1])))

    # Get NumPy ndarray
    setit = getattr(x, 'itemset')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            setit((i, j), d.get((row, col), nan))

    return x

def as_dict(
        x: NpArray, labels: StrListPair, nan: OptNum = NaN) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        x: NumPy ndarray of shape (*n*, *m*), where *n* equals the number of
            <*rows*> and *m* the number of <*columns*>.
        labels: Tuple of format (<*rows*>, <*columns*>), where <*rows*> is a
            list of row labels, e.g. ['row1', 'row2', ...] and <*columns*> a
            list of column labels, e.g. ['col1', 'col2', ...].
        na: Optional value to mask Not a Number (NaN) entries. For cells in the
            array, which have this value, no entry in the returned dictionary
            is created. If nan is None, then for all numbers entries are
            created. Default: `IEEE 754`_ floating point representation of NaN.

    Returns:
         Dictionary with keys (<*row*>, <*col*>), where the elemns <*row*> are
         row labels from the list <*rows*> and <*col*> column labels from the
         list *columns*.

    """
    # Check Type of Argument 'x'
    if not isinstance(x, np.ndarray):
        raise TypeError(
            "'x' is required to by of type 'numpy ndarray'"
            f", not '{type(x).__name__}'")
    # Check dimension of Array 'x'
    if x.ndim != 2:
        raise TypeError(
            "Numpy ndarray 'x' is required to have dimension 2"
            f", not '{x.ndim}'")

    # Get dictionary with pairs as keys
    d: StrPairDict = {}
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            val = x.item(i, j)
            if nan is None or not np.isnan(val):
                d[(row, col)] = val

    return d
