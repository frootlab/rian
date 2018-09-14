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
    DyaDict, DyaTuple, Optional, NpAxis, OptStr, Union)

Array = np.ndarray
ArrayLike = Union[Array, np.matrix, float, int]

def fromdict(d: DyaDict, labels: DyaTuple, na: float = 0.) -> Array:
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
        Numpy array of shape (n, m), where n equals the length of the
        <row list> of the argument labels and m equals the length of the
        <col list> of the argument labels.

    """

    a = np.empty(shape=(len(labels[0]), len(labels[1])))
    for i, x in enumerate(labels[0]):
        for j, y in enumerate(labels[1]):
            a[i, j] = d[(x, y)] if (x, y) in d else na

    return a

def asdict(a: Array, labels: DyaTuple, na: Optional[float] = None) -> DyaDict:
    """Convert array to dictionary.

    Args:
        a: Numpy array of shape (n, m), where n equals the length of the
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

    d = {}
    for i, x in enumerate(labels[0]):
        for j, y in enumerate(labels[1]):
            if not na is None and a[i, j] == na:
                continue
            d[(x, y)] = a[i, j]

    return d

def sumnorm(a: ArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> ArrayLike:
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
        return np.sum(a, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Sum of Values (S)
    if norm == 'S':
        return np.sum(a, axis=axis)

    # Sum of Errors (SE) / l1-Norm (l1)
    if norm in ['SE', 'L1']:
        return np.sum(np.abs(a), axis=axis)

    # Sum of Squared Errors (SSE) / Residual sum of squares (RSS)
    if norm in ['SSE', 'RSS']:
        return np.sum(a ** 2, axis=axis)

    # Root Sum of Squared Errors (RSSE) / l2-Norm (l2)
    if norm in ['RSSE', 'L2']:
        return np.sqrt(np.sum(a ** 2, axis=axis))

    raise ValueError(f"norm '{norm}' is not supported")

def meannorm(a: ArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> ArrayLike:
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
        return np.mean(a, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Mean of Values (M)
    if norm == 'M':
        return np.mean(a, axis=axis)

    # Mean of Errors (ME)
    if norm == 'ME':
        return np.mean(np.abs(a), axis=axis)

    # Mean of Squared Errors (MSE)
    if norm == 'MSE':
        return np.mean(a ** 2, axis=axis)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if norm == 'RMSE':
        return np.sqrt(np.mean(a ** 2, axis=axis))

    raise ValueError(f"norm '{norm}' is not supported")

def devnorm(a: ArrayLike, norm: OptStr = None, axis: NpAxis = 0) -> ArrayLike:
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
        return np.std(a, axis=axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    norm = norm.upper()

    # Standard Deviation of Data (SD)
    if norm == 'SD':
        return np.std(a, axis=axis)

    # Standard Deviation of Errors (SDE)
    if norm == 'SDE':
        return np.std(np.abs(a), axis=axis)

    # Standard Deviation of Squared Errors (SDSE)
    if norm == 'SDSE':
        return np.std(a ** 2, axis=axis)

    raise ValueError(f"norm '{norm}' is not supported")
