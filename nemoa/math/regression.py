# -*- coding: utf-8 -*-
"""Regression Analysis Functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://pypi.org/project/numpy") from err

from nemoa.base import this
from nemoa.math import vector
from nemoa.types import Any, NpAxes, NpArray, NpArrayLike, StrList

_ERROR_PREFIX = 'error_'

#
# Error statistics for the evaluation of Regression Errors and Residuals
#

def errors() -> StrList:
    """Get sorted list of :term:`discrepancy measures<discrepancy measure>`.

    Returns:
        Sorted list of all discrepancy functions, that are implemented within
        the module.

    """
    return this.crop_functions(prefix=_ERROR_PREFIX)

def error(
        x: NpArrayLike, y: NpArrayLike, name: str, axes: NpAxes = 0,
        **kwds: Any) -> NpArray:
    """Calculate :term:`discrepancy<discrepancy measure>` of a prediction.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        name: Name of discrepancy function:
            'sad': :term:`Sum of Absolute Differences`
            'rss': :term:`Residual Sum of Squares`
            'mse': :term:`Mean Squared Error`
            'mae': :term:`Mean Absolute Error`
            'rmse': :term:`Root-Mean-Square Error`
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.
        **kwds: Additional parameters for the given discrepancy function. The
            function specific parameters are documented within the respective
            functions.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    # Check arguments 'x' and 'y' to be array like
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be 'Array like'") from err
    try:
        y = np.array(y)
    except TypeError as err:
        raise TypeError(
            "argument 'y' is required to be 'Array like'") from err

    # Check shapes and dtypes of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Evaluate function
    fname = _ERROR_PREFIX + name.lower()
    return this.call_attr(fname, x=x, y=y, axes=axes, **kwds)

def error_sad(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Sum of Absolute Differences` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_manhattan(x, y, axes=axes)

def error_rss(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Residual Sum of Squares` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return np.sum(np.square(np.add(x, np.multiply(y, -1))), axis=axes)

def error_mse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Mean Squared Error` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return np.mean(np.square(np.add(x, np.multiply(y, -1))), axis=axes)

def error_mae(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Mean Absolute Error` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_amean(x, y, axes=axes)

def error_rmse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Root-Mean-Square Error` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_qmean(x, y, axes=axes)

# TODO (patrick.michl@gmail.com): Goodness of fit Measures
# https://en.wikipedia.org/wiki/Goodness_of_fit
