# -*- coding: utf-8 -*-
"""Vector Norms and Metrices."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import numpy as np
from nemoa.base import catalog, check, pkg
from nemoa.types import Any, NpAxes, NpArray, NpArrayLike, StrList

#
# Define Catalog Categories for global Registration of Algorithms
#

@catalog.category
class Norm:
    name: str

@catalog.category
class Distance:
    name: str

#
# Vector Norms
#

def norms() -> StrList:
    """Get sorted list of vector space norms.

    Returns:
        Sorted list of all vector norms, that are implemented within the module.

    """
    path = __name__ + '.*'
    search = catalog.search(path, category=Norm)
    return sorted(rec.meta['name'] for rec in search)

def length(
        x: NpArrayLike, norm: str = 'euclid', axes: NpAxes = 0,
        **kwds: Any) -> NpArray:
    r"""Calculate the length of a vector with respect to a given norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: String, which identifies the used vector norm:

            :p: The :term:`p-norm` requires an additional parameter *p* and
                induces the :term:`Minkowski distance`.
            :1: The :term:`1-norm` induces the :term:`Manhattan distance`.
            :euclid: The :term:`Euclidean norm` is the default norm and induces
                the :term:`Euclidean distance`.
            :max: The :term:`Maximum norm` induces the
                :term:`Chebyshev distance`.
            :pmean: The :term:`Hölder mean` requires an additional parameter
                *p* and induces the :term:`power mean difference`.
            :amean: The :term:`mean absolute` induces the
                :term:`mean absolute difference`
            :qmean: The :term:`quadratic mean` induces the
                :term:`quadratic mean difference`
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.
        **kwds: Additional parameters of the given norm. These norm parameters
            are documented within the respective 'norm' functions.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    # Try to create numpy array from argument 'x'
    with contextlib.suppress(TypeError):
        if not isinstance(x, np.ndarray):
            x = np.array(x)

    # Check types of 'x' and 'axes'
    check.has_type("'x'", x, np.ndarray)
    check.has_type("'axes'", axes, (int, tuple))

    # Get function name
    fname = catalog.pick(category=Norm, name=norm).name

    # Evaluate function
    return pkg.call_attr(fname, x, axes=axes, **kwds)

@catalog.register(Norm, name='p')
def norm_p(x: NpArray, p: float = 2., axes: NpAxes = 0) -> NpArray:
    r"""Calculate a :term:`p-Norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive real number, which determines the p-norm by the p-th root of
            the summed p-th powered absolute values. For p < 1, the function
            does not satisfy the triangle inequality and yields a quasi-norm.
            For p >= 1 the p-norm is a norm.
            Default: 2.
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
    # For special cases prefer individual implementations, which are faster then
    # the generic implementation of the p-norm
    if p == 1.: # Use the 1-norm
        return norm_1(x, axes=axes)
    if p == 2.: # Use the Euclidean norm
        return norm_euclid(x, axes=axes)

    return np.power(np.sum(np.power(np.abs(x), p), axis=axes), 1. / p)

@catalog.register(Norm, name='1-norm')
def norm_1(x: NpArray, axes: NpAxes = 0) -> NpArray:
    r"""Calculate the :term:`1-Norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
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
    return np.sum(np.abs(x), axis=axes)

@catalog.register(Norm, name='euclid')
def norm_euclid(x: NpArray, axes: NpAxes = 0) -> NpArray:
    r"""Calculate the :term:`Euclidean norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
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
    return np.sqrt(np.sum(np.square(x), axis=axes))

@catalog.register(Norm, name='maximum')
def norm_max(x: NpArray, axes: NpAxes = 0) -> NpArray:
    r"""Calculate the :term:`Maximum norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
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
    return np.amax(np.abs(x), axis=axes)

@catalog.register(Norm, name='p-mean')
def norm_pmean(x: NpArray, p: float = 2., axes: NpAxes = 0) -> NpArray:
    r"""Calculate a :term:`Hölder mean` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive real number, which determines the power mean by the p-th
            root of the averaged p-th powered absolute values. For p < 1, the
            function does not satisfy the triangle inequality and yields a
            quasi-norm. For p >= 1 the power mean is a norm.
            Default: 2
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
    if p == 1.:
        return norm_amean(x, axes=axes) # faster then generic implementation
    if p == 2.:
        return norm_qmean(x, axes=axes) # faster then generic implementation
    return np.power(np.mean(np.power(np.abs(x), p), axis=axes), 1. / float(p))

@catalog.register(Norm, name='abs-mean')
def norm_amean(x: NpArray, axes: NpAxes = 0) -> NpArray:
    r"""Calculate :term:`mean absolute` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
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
    return np.mean(np.abs(x), axis=axes)

@catalog.register(Norm, name='quadratic-mean')
def norm_qmean(x: NpArray, axes: NpAxes = 0) -> NpArray:
    r"""Calculate the :term:`quadratic mean` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
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
    return np.sqrt(np.mean(np.square(x), axis=axes))

#
# Distances
#

def distances() -> StrList:
    """Get sorted list of vector space distances.

    Returns:
        Sorted list of all vector space distances and generalized vector space
        distances, that are implemented within the module.

    """
    path = __name__ + '.*'
    search = catalog.search(path, category=Distance)
    return sorted(rec.meta['name'] for rec in search)

def distance(
        x: NpArrayLike, y: NpArrayLike, name: str = 'euclid',
        axes: NpAxes = 0, **kwds: Any) -> NpArray:
    """Calculate distance of two arrays along given axes.

    A vector distance function, also known as metric, is a function d(x, y),
    which quantifies the proximity of vectors in a vector space as non-negative
    real numbers. If the distance is zero, then the vectors are equivalent with
    respect to the distance function. Distance functions are often used as
    error, loss or risk functions, to evaluate statistical estimations.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        name: Name of distance. Accepted values are:
            'minkowski': :term:`Minkowski distance`
                Remark: requires additional parameter 'p'
            'manhattan': :term:`Manhattan distance`
            'euclid': :term:`Euclidean distance` (default)
            'chebyshev': :term:`Chebyshev distance`
            'pmean': :term:`Power mean difference`
                Remark: requires additional parameter 'p'
            'amean': :term:`Mean absolute difference`
            'qmean': :term:`Quadratic mean difference`
        axes: Integer or tuple of integers, that identify the array axes, along
            which the function is evaluated. In a one-dimensional array the
            single axis has ID 0. In a two-dimensional array the axis with ID 0
            is running across the rows and the axis with ID 1 is running across
            the columns. For the value None, the function is evaluated with
            respect to all axes of the array. The default value is 0, which
            is an evaluation with respect to the first axis in the array.
        **kwds: Parameters of the given distance or class of distances.
            The Parameters are documented within the respective 'dist'
            functions.

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    # Try to create numpy arrays from 'x' and 'y'
    with contextlib.suppress(TypeError):
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

    # Check types of 'x', 'y' and 'axes'
    check.has_type("'x'", x, np.ndarray)
    check.has_type("'y'", y, np.ndarray)
    check.has_type("'axes'", axes, (int, tuple))

    # Check dimensions of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Get function name
    fname = catalog.pick(category=Distance, name=name).name

    # Evaluate function
    return pkg.call_attr(fname, x, y, axes=axes, **kwds)

@catalog.register(Distance, name='minkowski')
def dist_minkowski(
        x: NpArray, y: NpArray, p: float = 2., axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Minkowski distance` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the Minkowsi distance by the
            respective p-norm. For p < 1, the function does not satisfy the
            triangle inequality and thus is not a valid metric, but a
            quasi-metric. For p >= 1 the Minkowski distance is a metric.
            Default: 2.
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
    return norm_p(np.add(x, np.multiply(y, -1)), p=p, axes=axes)

@catalog.register(Distance, name='manhattan')
def dist_manhattan(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Manhattan distance` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
        axes: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        :class:`numpy.ndarray` of dimension dim(*x*) - len(*axes*).

    """
    return norm_1(np.add(x, np.multiply(y, -1)), axes=axes)

@catalog.register(Distance, name='euclid')
def dist_euclid(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Euclidean distance` along given axes for.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same shape and datatypes as 'x'
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
    return norm_euclid(np.add(x, np.multiply(y, -1)), axes=axes)

@catalog.register(Distance, name='chebyshev')
def dist_chebyshev(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`Chebyshev distance` along given axes.

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
    return norm_max(np.add(x, np.multiply(y, -1)), axes=axes)

@catalog.register(Distance, name='p-mean')
def dist_pmean(
        x: NpArray, y: NpArray, p: float = 2., axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`power mean difference` along given axes.

    Args:
        x: Numpy ndarray with numeric values of arbitrary dimension.
        y: Numpy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the power mean difference by
            the respective power mean. For p < 1, the power mean does not
            satisfy the triangle inequality, such that the induced power mean
            difference is not a valid metric, but a quasi-metric. For p >= 1
            the power mean difference is a metric.
            Default: 2.
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
    return norm_pmean(np.add(x, np.multiply(y, -1)), p=p, axes=axes)

@catalog.register(Distance, name='abs-mean')
def dist_amean(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`mean absolute difference` along given axes.

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
    return norm_amean(np.add(x, np.multiply(y, -1)), axes=axes)

@catalog.register(Distance, name='quadratic-mean')
def dist_qmean(x: NpArray, y: NpArray, axes: NpAxes = 0) -> NpArray:
    """Calculate :term:`quadratic mean difference` along given axes.

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
    return norm_qmean(np.add(x, np.multiply(y, -1)), axes=axes)
