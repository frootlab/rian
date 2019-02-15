# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Regression Analysis Functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any
import numpy as np
from flab.base import call, catalog
from flab.base.types import StrList
from nemoa.base import array
from nemoa.math import vector
from nemoa.typing import NpAxes, NpArray, NpArrayLike

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
    return sorted(catalog.search(Error).get('name'))

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
    f = catalog.pick(Error, name=name)
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
    return vector.manhattan(x, y, axes=axes)

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
    return vector.amean_dist(x, y, axes=axes)

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
    return vector.qmean_dist(x, y, axes=axes)

# TODO (patrick.michl@gmail.com): Goodness of fit Measures
# https://en.wikipedia.org/wiki/Goodness_of_fit
