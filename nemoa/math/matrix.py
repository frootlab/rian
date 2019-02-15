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
"""Matrix Norms and Metrices."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any
import numpy as np
from flab.base import call, catalog, check
from flab.base.types import IntPair, StrList
from nemoa.base import array
from nemoa.typing import NpArray, NpArrayLike
from nemoa.math import vector

#
# Define Catalog Categories
#

@catalog.category
class Norm:
    name: str

@catalog.category
class Distance:
    name: str

#
# Matrix Norms
#

def norms() -> StrList:
    """Get sorted list of matrix norms."""
    return sorted(catalog.search(Norm).get('name'))

def norm(
        x: NpArrayLike, name: str = 'frobenius', axes: IntPair = (0, 1),
        **kwds: Any) -> NpArray:
    """Calculate magnitude of matrix with respect to given norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        name: Name of matrix norm. Accepted values are:

            :pq: :term:`pq-Norm`. Remark: requires additional parameters *p* and
                *q*
            :frobenius: The default norm is the :term:`Frobenius Norm`

        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.
        **kwds: Parameters of the given norm / class of norms.
            The norm Parameters are documented within the respective 'norm'
            functions.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    # Try to cast 'x' as array
    x = array.cast(x)

    # Check type of 'axes'
    check.has_type("'axes'", axes, tuple)

    # Check dimension of 'x'
    if x.ndim < 2:
        raise ValueError("'x' is required to have dimension > 1")

    # Check value of 'axes'
    check.has_size("argument 'axes'", axes, size=2)
    if axes[0] == axes[1]:
        raise np.AxisError(
            "first and second axis have to be different")

    # Get function from catalog
    f = catalog.pick(Norm, name=name)

    # Evaluate function
    return call.safe_call(f, x=x, axes=axes, **kwds)

@catalog.register(Norm, name='pq-norm')
def pq_norm(x: NpArray,
        p: float = 2., q: float = 2., axes: IntPair = (0, 1)) -> NpArray:
    """Calculate :term:`pq-norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        p: Positive real number, which determines the parameter *p* of the
            :term:`p-norm`, which is performed along the first given axes. The
            default value is 2.
        q: Positive real number, which determines the parameter *p* of the
            :term:`p-norm`, which is performed along the second given axes. The
            default value is 2.
        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    # For special cases prefer specific implementations for faster calculation
    if p == q == 2.: # Use the Frobenius norm
        return frob_norm(x, axes=axes)
    if p == q: # Use an elementwise p-norm
        return vector.p_norm(x, p=p, axes=axes)

    # If the first axis id is smaller then the second, the latter
    # has to be corrected by the collapsed dimension of the first sum
    if axes[0] < axes[1]:
        axisp, axisq = axes[0], axes[1] - 1
    else:
        axisp, axisq = axes[0], axes[1]

    psum = np.sum(np.power(np.abs(x), p), axis=axisp)
    qsum = np.sum(np.power(psum, q / p), axis=axisq)

    return np.power(qsum, 1. / q)

@catalog.register(Norm, name='frobenius')
def frob_norm(x: NpArray, axes: IntPair = (0, 1)) -> NpArray:
    """Calculate :term:`Frobenius norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    return vector.euclid_norm(x, axes=axes)

#
# Matrix Metrices
#

def distances() -> StrList:
    """Get sorted list of matrix distances."""
    return sorted(catalog.search(Distance).get('name'))

def distance(
        x: NpArrayLike, y: NpArrayLike, name: str = 'frobenius',
        axes: IntPair = (0, 1), **kwds: Any) -> NpArray:
    """Calculate matrix distances of two arrays along given axes.

    A matrix distance function, is a function d(x, y), which quantifies the
    proximity of matrices in a vector space as non-negative
    real numbers. If the distance is zero, then the matrices are equivalent with
    respect to the distance function. Distance functions are often used as
    error, loss or risk functions, to evaluate statistical estimations.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        name: Name of used matrix distance. Accepted values are:
            'frobenius': :term:`Frobenius distance` (default)
        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.
        **kwds: Parameters of the given distance or class of distances.
            The Parameters are documented within the respective 'dist'
            functions.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    # Try to cast 'x' and 'y' as arrays
    x = array.cast(x)
    y = array.cast(y)

    # Check type of 'axes'
    check.has_type("'axes'", axes, tuple)

    # Check dimensions of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Check value of 'axes'
    check.has_size("argument 'axes'", axes, size=2)
    if axes[0] == axes[1]:
        raise np.AxisError(
            "first and second axis have to be different")

    # Get function from catalog
    f = catalog.pick(Distance, name=name)

    # Evaluate function
    return call.safe_call(f, x=x, y=y, axes=axes, **kwds)

@catalog.register(Distance, name='frobenius')
def frob_dist(x: NpArray, y: NpArray, axes: IntPair = (0, 1)) -> NpArray:
    """Calculate :term:`Frobenius distance` of two arrays along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    return frob_norm(np.add(x, np.multiply(y, -1)), axes=axes)

@catalog.register(Distance, name='pq-distance')
def pq_dist(
        x: NpArray, y: NpArray, p: float = 2., q: float = 2.,
        axes: IntPair = (0, 1)) -> NpArray:
    """Calculate :term:`pq-distance` of two arrays along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with equal
            dimension, shape and datatypes as 'x'.
        p: Positive real number, which determines the parameter *p* of the
            :term:`p-norm`, which is performed along the first given axes. The
            default value is 2.
        q: Positive real number, which determines the parameter *p* of the
            :term:`p-norm`, which is performed along the second given axes. The
            default value is 2.
        axes: Pair (2-tuple) of integers, that identify the array axes, along
            which the function is evaluated. In a two-dimensional array the axis
            with ID 0 is running across the rows and the axis with ID 1 is
            running across the columns. The default value is (0, 1), which is an
            evaluation with respect to the first two axis in the array.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - 2.

    """
    return pq_norm(x - y, p=p, q=q, axes=axes)
