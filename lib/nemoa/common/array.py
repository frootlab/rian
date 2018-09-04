# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as E:
    raise ImportError("requires package numpy: "
        "https://scipy.org") from E

from typing import Optional, Tuple, Union

ArrayLike = Union[np.ndarray, np.matrix, float, int]
Axis = Optional[Union[int, Tuple[int]]]

def sumnorm(a: ArrayLike, norm: Optional[str] = None,
    axis: Axis = 0) -> ArrayLike:
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

    if not norm: return np.sum(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Sum of Values (S)
    if n == 'S': return np.sum(a, axis = axis)

    # Sum of Errors (SE) / l1-Norm (l1)
    if n in ['SE', 'L1']: return np.sum(np.abs(a), axis = axis)

    # Sum of Squared Errors (SSE) / Residual sum of squares (RSS)
    if n in ['SSE', 'RSS']: return np.sum(a ** 2, axis = axis)

    # Root Sum of Squared Errors (RSSE) / l2-Norm (l2)
    if n in ['RSSE', 'L2']: return np.sqrt(np.sum(a ** 2, axis = axis))

    raise ValueError(f"norm '{norm}' is not supported")

def meannorm(a: ArrayLike, norm: Optional[str] = None,
    axis: Axis = 0) -> ArrayLike:
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

    if not norm: return np.mean(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Mean of Values (M)
    if n == 'M': return np.mean(a, axis = axis)

    # Mean of Errors (ME)
    if n == 'ME': return np.mean(np.abs(a), axis = axis)

    # Mean of Squared Errors (MSE)
    if n == 'MSE': return np.mean(a ** 2, axis = axis)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if n == 'RMSE': return np.sqrt(np.mean(a ** 2, axis = axis))

    raise ValueError(f"norm '{norm}' is not supported")

def devnorm(a: ArrayLike, norm: Optional[str] = None,
    axis: Axis = 0) -> ArrayLike:
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

    if not norm: return np.std(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Standard Deviation of Data (SD)
    if n == 'SD': return np.std(a, axis = axis)

    # Standard Deviation of Errors (SDE)
    if n == 'SDE': return np.std(np.abs(a), axis = axis)

    # Standard Deviation of Squared Errors (SDSE)
    if n == 'SDSE': return np.std(a ** 2, axis = axis)

    raise ValueError(f"norm '{norm}' is not supported")
