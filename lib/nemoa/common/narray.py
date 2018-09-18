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

from nemoa.common.ntype import (
    StrPairDict, StrListPair, NpAxis, NpArray, NpArrayLike, OptStr, OptFloat)

def fromdict(
        edges: StrPairDict, labels: StrListPair, na: float = 0.) -> NpArray:
    """Convert dictionary to array.

    Args:
        edges: Dictionary of format {(<row>, <col>): value, ...}, where:
            <row> is an element of the <row list> of the argument labels and
            <col> is an element of the <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...].
        na: Value to mask NA (Not Available) entries. Missing entries in the
            dictionary are replenished by the NA value in the array.

    Returns:
        Numpy array of shape (n, m), where n equals the length of the
        <row list> of the argument labels and m equals the length of the
        <col list> of the argument labels.

    """
    arr = np.empty(shape=(len(labels[0]), len(labels[1])))
    for i, colx in enumerate(labels[0]):
        for j, coly in enumerate(labels[1]):
            arr[i, j] = edges.get((colx, coly), na)

    return arr

def asdict(
        arr: NpArray, labels: StrListPair, na: OptFloat = None) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        arr: Numpy array of shape (n, m), where n equals the length of the
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
    # Check argument 'arr'
    if not hasattr(arr, 'item'):
        raise TypeError(
            "argument 'arr' is required to by of type 'ndarray'"
            f", not '{type(arr)}'")

    # Declare and initialize return value
    dpair: StrPairDict = {}

    # Get dictionary with pairs as keys
    getval = getattr(arr, 'item')
    for i, x in enumerate(labels[0]):
        for j, y in enumerate(labels[1]):
            val = getval(i, j)
            if na is None or val != na:
                dpair[(x, y)] = val

    return dpair

def sumnorm(arr: NpArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> NpArray:
    """Sum of array.

    Calculate sum of data along given axes, using a given norm.

    Args:
        a: Numpy ndarray containing data
        norm: Data sum norm. Accepted values are:
            'S': Sum of Values
            'SE', 'l1': Sum of Errors / l1 Norm of Residuals
            'SSE', 'RSS': Sum of Squared Errors / Residual Sum of Squares
            'RSSE', 'l2': Root Sum of Squared Errors / l2 Norm of Residuals
        axis: Axis or axes along which a sum is performed.

    Returns:
        Sum of data as ndarray.

    """
    if norm is None:
        return np.sum(arr, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Sum of Values (S)
    if norm == 'S':
        return np.sum(arr, axis=axis)

    # Sum of Errors (SE) / l1-Norm (l1)
    if norm in ['SE', 'L1']:
        return np.sum(np.abs(arr), axis=axis)

    # Sum of Squared Errors (SSE) / Residual sum of squares (RSS)
    if norm in ['SSE', 'RSS']:
        return np.sum(np.square(arr), axis=axis)

    # Root Sum of Squared Errors (RSSE) / l2-Norm (l2)
    if norm in ['RSSE', 'L2']:
        return np.sqrt(np.sum(np.square(arr), axis=axis))

    raise ValueError(f"norm '{norm}' is not supported")

def meannorm(
        arr: NpArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> NpArray:
    """Mean of data.

    Calculate mean of data along given axes, using a given norm.

    Args:
        a: Numpy array containing data
        norm: Data mean norm. Accepted values are:
            'M': Arithmetic Mean of Values
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors / L2 Norm
        axis: Axis or axes along which a mean is performed.

    Returns:
        Mean of data as ndarray

    """
    if norm is None:
        return np.mean(arr, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Mean of Values (M)
    if norm == 'M':
        return np.mean(arr, axis=axis)

    # Mean of Errors (ME)
    if norm == 'ME':
        return np.mean(np.abs(arr), axis=axis)

    # Mean of Squared Errors (MSE)
    if norm == 'MSE':
        return np.mean(np.square(arr), axis=axis)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if norm == 'RMSE':
        return np.sqrt(np.mean(np.square(arr), axis=axis))

    raise ValueError(f"norm '{norm}' is not supported")

def devnorm(
        arr: NpArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> NpArray:
    """Deviation of data.

    Calculate deviation of data along given axes, using a given norm.

    Args:
        a: Numpy array containing data
        norm: Data deviation norm. Accepted values are:
            'SD': Standard Deviation of Values
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors
        axis: Axis or axes along which a deviation is performed.

    Returns:
        Deviation of data as ndarray

    """
    if norm is None:
        return np.std(arr, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Standard Deviation of Data (SD)
    if norm == 'SD':
        return np.std(arr, axis=axis)

    # Standard Deviation of Errors (SDE)
    if norm == 'SDE':
        return np.std(np.abs(arr), axis=axis)

    # Standard Deviation of Squared Errors (SDSE)
    if norm == 'SDSE':
        return np.std(np.square(arr), axis=axis)

    raise ValueError(f"norm '{norm}' is not supported")
