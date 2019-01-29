# -*- coding: utf-8 -*-
"""Regression Analysis Functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any
import numpy as np
from nemoa.base import array, call, catalog
from nemoa.math import vector
from nemoa.types import NpAxes, NpArray, NpArrayLike, StrList

#
# Define Catalog Categories
#

@catalog.category
class Error:
    """Catalog category for regression errors.

    Regression errors are :term:`discrepancy functions<discrepancy measure>`,
    that provide information about the deviation of a single model prediction
    and given observed data.

    """
    name: str

#
# Error statistics for the evaluation of Regression Errors and Residuals
#

def errors() -> StrList:
    """Get sorted list of implemented regression errors."""
    path = __name__ + '.*'
    search = catalog.search(path, category=Error)
    return sorted(rec.meta['name'] for rec in search)

def error(
        x: NpArrayLike, y: NpArrayLike, name: str, axes: NpAxes = 0,
        **kwds: Any) -> NpArray:
    """Calculate the regression error of a prediction.

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
    # Try to cast 'x' and 'y' as arrays
    x = array.cast(x)
    y = array.cast(y)

    # Check shapes and dtypes of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Evaluate function
    f = catalog.pick(category=Error, name=name).reference
    return call.safe_call(f, x=x, y=y, axes=axes, **kwds)

@catalog.register(Error, name='sad')
def sad(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Sum of Absolute Differences` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
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

@catalog.register(Error, name='rss')
def rss(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Residual Sum of Squares` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
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

@catalog.register(Error, name='mse')
def mse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Mean Squared Error` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
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

@catalog.register(Error, name='mae')
def mae(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Mean Absolute Error` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
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

@catalog.register(Error, name='rmse')
def rmse(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Estimate :term:`Root-Mean-Square Error` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
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
