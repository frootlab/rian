# -*- coding: utf-8 -*-
"""Regression Analysis Functions.

.. _`numpy.ndarray`:
    https://www.numpy.org/devdocs/reference/arrays.ndarray
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
        "https://pypi.org/project/numpy") from err

from nemoa.base import assess, this
from nemoa.math import vector
from nemoa.types import Any, NpAxes, NpArray, NpArrayLike, StrList

_ERROR_PREFIX = 'error_'

#
# Error statistics for the evaluation of Regression Errors and Residuals
#

def errors() -> StrList:
    """Get sorted list of :term:`discrepancy` measures.

    Returns:
        Sorted list of all discrepancy functions, that are implemented within
        the module.

    """
    return this.crop_functions(prefix=_ERROR_PREFIX)

def error(
        x: NpArrayLike, y: NpArrayLike, name: str, axes: NpAxes = 0,
        **kwds: Any) -> NpArray:
    """Calculate :term:`discrepancy` of a prediction along given axes.

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

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

    # Get discrepancy function
    fname = _ERROR_PREFIX + name.lower()
    module = assess.get_module(this.get_module_name())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(f"name '{name}' is not valid")

    # Evaluate distance function
    return func(x, y, axes=axes, **assess.get_parameters(func, default=kwds))

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_manhatten(x, y, axes=axes)

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

    """
    return np.sum(np.square(np.add(x, np.multiply(y, -1))), axis=axes)

def error_mse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Mean Squared Error` along given axes.

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

    """
    return np.mean(np.square(np.add(x, np.multiply(y, -1))), axis=axes)

def error_mae(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Mean Absolute Error` along given axes.

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_amean(x, y, axes=axes)

def error_rmse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Root-Mean-Square Error` along given axes.

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
        `Numpy.ndarray`_ of dimension dim(*x*) - len(*axes*).

    """
    return vector.dist_qmean(x, y, axes=axes)

# TODO (patrick.michl@gmail.com): Add RSSE
# norm_euclid
# With respect to a given sample the induced metric, is a sample statistic and
# referred as the 'Root-Sum-Square Difference' (RSSD). An important
# application is the method of least squares [3].
# [3] https://en.wikipedia.org/wiki/least_squares

# TODO (patrick.michl@gmail.com): Goodness of fit Measures
# https://en.wikipedia.org/wiki/Goodness_of_fit
