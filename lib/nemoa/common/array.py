# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as E: raise ImportError(
    "nemoa.common.array requires numpy: https://scipy.org") from E

from typing import Optional, Tuple, Union

ndarray = numpy.ndarray
Axis = Optional[Union[int, Tuple[int]]]

def sumnorm(a: ndarray, norm: Optional[str] = None, axis: Axis = 0) -> ndarray:
    """Sum of array.

    Calculate sum of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str or None, optional): Data mean norm
            'S': Sum of Values
            'SE', 'l1': Sum of Errors / l1 Norm of Residuals
            'SSE', 'RSS': Sum of Squared Errors / Residual Sum of Squares
            'RSSE', 'l2': Root Sum of Squared Errors / l2 Norm of Residuals
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a sum is performed.

    Returns:
        Sum of data as ndarray.

    """

    if not norm: return numpy.sum(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Sum of Values (S)
    if n == 'S': return numpy.sum(a, axis = axis)

    # Sum of Errors (SE) / l1-Norm (l1)
    if n in ['SE', 'L1']: return numpy.sum(numpy.abs(a), axis = axis)

    # Sum of Squared Errors (SSE) / Residual sum of squares (RSS)
    if n in ['SSE', 'RSS']: return numpy.sum(a ** 2, axis = axis)

    # Root Sum of Squared Errors (RSSE) / l2-Norm (l2)
    if n in ['RSSE', 'L2']: return numpy.sqrt(numpy.sum(a ** 2, axis = axis))

    raise ValueError(f"norm '{norm}' is not supported")

def meannorm(a: ndarray, norm: Optional[str] = None, axis: Axis = 0) -> ndarray:
    """Mean of data.

    Calculate mean of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str or None, optional): Data mean norm
            'M': Arithmetic Mean of Values
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors / L2 Norm
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a mean is performed.

    Returns:
        Mean of data as ndarray

    """

    if not norm: return numpy.mean(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Mean of Values (M)
    if n == 'M': return numpy.mean(a, axis = axis)

    # Mean of Errors (ME)
    if n == 'ME': return numpy.mean(numpy.abs(a), axis = axis)

    # Mean of Squared Errors (MSE)
    if n == 'MSE': return numpy.mean(a ** 2, axis = axis)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if n == 'RMSE': return numpy.sqrt(numpy.mean(a ** 2, axis = axis))

    raise ValueError(f"norm '{norm}' is not supported")

def devnorm(a: ndarray, norm: Optional[str] = None, axis: Axis = 0) -> ndarray:
    """Deviation of data.

    Calculate deviation of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str or None, optional): Data deviation norm
            'SD': Standard Deviation of Values
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a deviation is performed.

    Returns:
        Deviation of data as ndarray

    """

    if not norm: return numpy.std(a, axis = axis)
    if not isinstance(norm, str):
        raise TypeError(f"norm requires type 'str', not '{type(norm)}'")

    n = norm.upper()

    # Standard Deviation of Data (SD)
    if n == 'SD': return numpy.std(a, axis = axis)

    # Standard Deviation of Errors (SDE)
    if n == 'SDE': return numpy.std(numpy.abs(a), axis = axis)

    # Standard Deviation of Squared Errors (SDSE)
    if n == 'SDSE': return numpy.std(a ** 2, axis = axis)

    raise ValueError(f"norm '{norm}' is not supported")
