# -*- coding: utf-8 -*-
"""Matrix Norms and Metrices."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import numpy as np
from nemoa.base import check, this
from nemoa.math import vector
from nemoa.types import Any, IntPair, NpArray, NpArrayLike, StrList
from nemoa.types import StrPairDict, StrListPair, NaN, Number, OptNumber

_NORM_PREFIX = 'norm_'
_DIST_PREFIX = 'dist_'

#
# Matrix Norms
#

def norms() -> StrList:
    """Get sorted list of matrix norms.

    Returns:
        Sorted list of all matrix norms, that are implemented within the module.

    """
    return this.crop_functions(prefix=_NORM_PREFIX)

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
    # Convert numpy array like 'x' to numpy array
    with contextlib.suppress(TypeError):
        if not isinstance(x, np.ndarray):
            x = np.array(x)

    # Check types of 'x' and 'axes'
    check.has_type("argument 'x'", x, np.ndarray)
    check.has_type("argument 'axes'", axes, tuple)

    # Check dimension of 'x'
    if x.ndim < 2:
        raise ValueError("'x' is required to have dimension > 1")

    # Check value of 'axes'
    check.has_size("argument 'axes'", axes, size=2)
    if axes[0] == axes[1]:
        raise np.AxisError(
            "first and second axis have to be different")

    # Evaluate function
    fname = _NORM_PREFIX + name.lower()
    return this.call_attr(fname, x=x, axes=axes, **kwds)

def norm_pq(x: NpArray,
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
        return norm_frobenius(x, axes=axes)
    if p == q: # Use an elementwise p-norm
        return vector.norm_p(x, p=p, axes=axes)

    # If the first axis id is smaller then the second, the latter
    # has to be corrected by the collapsed dimension of the first sum
    if axes[0] < axes[1]:
        axisp, axisq = axes[0], axes[1] - 1
    else:
        axisp, axisq = axes[0], axes[1]

    psum = np.sum(np.power(np.abs(x), p), axis=axisp)
    qsum = np.sum(np.power(psum, q / p), axis=axisq)
    return np.power(qsum, 1. / q)

def norm_frobenius(x: NpArray, axes: IntPair = (0, 1)) -> NpArray:
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
    return vector.norm_euclid(x, axes=axes)

#
# Matrix Metrices
#

def distances() -> StrList:
    """Get sorted list of matrix distances.

    Returns:
        Sorted list of all matrix distances, that are implemented within the
        module.

    """
    return this.crop_functions(prefix=_DIST_PREFIX)

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
    # Try to create numpy arrays from 'x' and 'y'
    with contextlib.suppress(TypeError):
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

    # Check types of 'x', 'y' and 'axes'
    check.has_type("argument 'x'", x, np.ndarray)
    check.has_type("argument 'y'", y, np.ndarray)
    check.has_type("argument 'axes'", axes, tuple)

    # Check dimensions of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Check value of 'axes'
    check.has_size("argument 'axes'", axes, size=2)
    if axes[0] == axes[1]:
        raise np.AxisError(
            "first and second axis have to be different")

    # Evaluate function
    fname = _DIST_PREFIX + name.lower()
    return this.call_attr(fname, x=x, y=y, axes=axes, **kwds)

def dist_frobenius(x: NpArray, y: NpArray, axes: IntPair = (0, 1)) -> NpArray:
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
    return norm_frobenius(np.add(x, np.multiply(y, -1)), axes=axes)

def dist_pq(
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
    return norm_pq(x - y, p=p, q=q, axes=axes)

#
# Matrix type transformation
#

def from_dict(
        d: StrPairDict, labels: StrListPair, nan: Number = NaN) -> NpArray:
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
            Default: [IEEE754]_ floating point representation of NaN.

    Returns:
        :class:`numpy.ndarray` of shape (*n*, *m*), where *n* equals the number
        of <*rows*> and *m* the number of <*columns*>.

    """
    # Check type of 'd'
    check.has_type("argument 'd'", d, dict)

    # Declare and initialize return value
    x: NpArray = np.empty(shape=(len(labels[0]), len(labels[1])))

    # Get numpy ndarray
    setit = getattr(x, 'itemset')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            setit((i, j), d.get((row, col), nan))

    return x

def as_dict(
        x: NpArray, labels: StrListPair, nan: OptNumber = NaN) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        x: Numpy ndarray of shape (*n*, *m*), where *n* equals the number of
            <*rows*> and *m* the number of <*columns*>.
        labels: Tuple of format (<*rows*>, <*columns*>), where <*rows*> is a
            list of row labels, e.g. ['row1', 'row2', ...] and <*columns*> a
            list of column labels, e.g. ['col1', 'col2', ...].
        na: Optional value to mask Not a Number (NaN) entries. For cells in the
            array, which have this value, no entry in the returned dictionary
            is created. If nan is None, then for all numbers entries are
            created. Default: [IEEE754]_ floating point representation of NaN.

    Returns:
         Dictionary with keys (<*row*>, <*col*>), where the elemns <*row*> are
         row labels from the list <*rows*> and <*col*> column labels from the
         list *columns*.

    """
    # Check type of 'x'
    check.has_type("argument 'x'", x, np.ndarray)

    # Check dimension of 'x'
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
