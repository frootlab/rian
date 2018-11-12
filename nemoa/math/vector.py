# -*- coding: utf-8 -*-
"""Vector Norms and Metrices."""

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
from nemoa.types import Any, NpAxis, NpArray, NpArrayLike, StrList

_NORM_PREFIX = 'norm_'
_DIST_PREFIX = 'dist_'

#
# Vector Norms
#

def norms() -> StrList:
    """Get sorted list of vector space norms.

    Returns:
        Sorted list of all vector norms, that are implemented within the module.

    """
    return this.crop_functions(prefix=_NORM_PREFIX)

def length(x: NpArrayLike, norm: str = 'euclid', **kwds: Any) -> NpArray:
    """Calculate length of a vector by given norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of Vector Norm:

            :p:
                The :term:`p-norm`_ requires an additional parameter *p* and
                induces the :term:`Minkowski metric`_.
            :1:
                The :term:`1-norm`_ induces the :term:`Manhatten metric`_.
            :euclid:
                The :term:`Euclidean norm`_ is the default norm and induces the
                :term:`Euclidean metric`_.
            :max:
                The :term:`Maximum norm`_ induces the :term:`Chebyshev metric`.
            :pmean:
                The :term:`Hölder mean`_ requires an additional parameter *p*
                and induces the :term:`Power-Mean difference`.
            :amean:
                The :term:`Mean-Absolute` induces the
                :term:`Mean-Absolute` difference
            :qmean:
                The :term:`Quadratic-Mean` induces the
                :term:`Quadratic-Mean difference`

        **kwds: Additional parameters of the given norm. These norm parameters
            are documented within the respective 'norm' functions.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    # Check type of 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "First argument 'x' is required to be array-like") from err

    # Get function
    func = this.get_attr(_NORM_PREFIX + norm.lower())
    if not callable(func):
        raise ValueError(f"name '{str(norm)}' is not supported")

    # Evaluate function
    supp_kwds = assess.get_function_kwds(func, default=kwds)
    return func(x, **supp_kwds) # pylint: disable=E1102

def norm_p(x: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
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
        axis: Index of axis (or axes) along which the function is performed.
            Within a 1d array the axis has index 0. In a 2d array the axis with
            index 0 is running across rows, and the axis with index 1 is running
            across columns. If axis is a tuple of ints, the function is
            performed over all axes in the tuple. If axis is None, the function
            is performed over all axes.
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    # For special cases prefer individual implementations, which are faster then
    # the generic implementation of the p-norm
    if p == 1.: # Use the 1-norm
        return norm_1(x, axis=axis)
    if p == 2.: # Use the Euclidean norm
        return norm_euclid(x, axis=axis)

    psum = np.sum(np.power(np.abs(x), p), axis=axis)
    return np.power(psum, 1. / p)

def norm_1(x: NpArray, axis: NpAxis = 0) -> NpArray:
    r"""Calculate the :term:`1-Norm` of an array along given axis.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes. The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sum(np.abs(x), axis=axis)

def norm_euclid(x: NpArray, axis: NpAxis = 0) -> NpArray:
    r"""Calculate the :term:`Euclidean norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default is 0.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sqrt(np.sum(np.square(x), axis=axis))

def norm_max(x: NpArray, axis: NpAxis = 0) -> NpArray:
    r"""Calculate the :term:`Maximum norm` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes. The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default is 0

    Returns:
        Numpy ndarray of dimension dim(*x*) - #*axes*.

    """
    return np.amax(np.abs(x), axis=axis)

def norm_pmean(x: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
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
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    if p == 1.:
        return norm_amean(x, axis=axis) # faster then generic implementation
    if p == 2.:
        return norm_qmean(x, axis=axis) # faster then generic implementation
    return np.power(np.mean(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def norm_amean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    r"""Calculate :term:`Mean-Absolute` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.mean(np.abs(x), axis=axis)

def norm_qmean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    r"""Calculate the :term:`Quadratic-Mean` of an array along given axes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

# def norm_sd(x: NpArray, axis: NpAxis = 0) -> NpArray:
#     """Calculate Corrected Standard Deviation of an array along given axis.
#
#     The 'Corrected Standard Deviation' (SD) equals the Euclidean norm except for
#     the additional preliminary factor sqrt(1 / (n - 1)), where n is the
#     dimension of the vector space [1]. Due to this linear dependency the
#     Standard Deviation is a valid vector norm and thus induces a metric within
#     its domain.
#
#     .. math::
#         SD(\vec{x})
#             := \left({\frac{1}{n}}\sum_{i=1}^{n}|x_{i}|^{2}\right)^{1/2}
#             = \left(\frac{1}{n}\right)^{1/2}\|\vec{x}\|_{2}
#
#     Args:
#         x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
#             dimension. This includes nested lists, tuples, scalars and existing
#             arrays.
#         axis: Axis (or axes) along which the norm is calculated. Within a
#             one-dimensional array the axis always has index 0. A two-dimensional
#             array has two corresponding axes: The first running vertically
#             downwards across rows (axis 0), and the second running horizontally
#             across columns (axis 1).
#             Default: 0
#
#     Returns:
#         NumPy ndarray of dimension <dim x> - <number of axes>.
#
#     References:
#         [1] https://en.wikipedia.org/wiki/sample_standard_deviation
#
#     """
#     return np.std(x, axis=axis)

#
# Vector Metrices
#

def metrices() -> StrList:
    """Get sorted list of vector space metrices.

    Returns:
        Sorted list of all vector space metrices and generalized vector space
        metrices, that are implemented within the module.

    """
    return this.crop_functions(prefix=_DIST_PREFIX)

def distance(
        x: NpArrayLike, y: NpArrayLike, metric: str = 'euclid',
        **kwds: Any) -> NpArray:
    """Calculate vector distances of two arrays along given axis.

    A vector distance function, also known as metric, is a function d(x, y),
    which quantifies the proximity of vectors in a vector space as non-negative
    real numbers. If the distance is zero, then the vectors are equivalent with
    respect to the distance function [1]. Distance functions are often used as
    error, loss or risk functions, to evaluate statistical estimations [2].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        metric: Name of metric. Accepted values are:
            'minkowski': Minkowski distances (induced by p-norms)
                Remark: requires additional parameter 'p'
            'manhatten': Manhatten distance (induced by 1-norm)
            'euclid': Euclidean distance (induced by Euclidean norm)
            'chebyshev': Chebyshev distance (induced by Maximum norm)
            'pmean': Class of Power mean differences (induced by Power Means)
                Remark: requires additional parameter 'p'
            'amean': Arithmetic mean difference (induced by Arithmetic Mean)
            'qmean': Quadratic mean difference (induced by Quadratic Mean)
            Default: 'euclid'
        **kwds: Parameters of the given metric or class of metrices.
            The Parameters are documented within the respective 'dist'
            functions.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/metric_(mathematics)
        [2] https://en.wikipedia.org/wiki/loss_function

    """
    # Check 'x' and 'y' to be array-like
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

    # Get function
    func = this.get_attr(_DIST_PREFIX + metric.lower())
    if not callable(func):
        raise ValueError(f"name '{str(metric)}' is not supported")

    # Evaluate function
    supp_kwds = assess.get_function_kwds(func, default=kwds)
    return func(x, y, **supp_kwds) # pylint: disable=E1102

def dist_minkowski(
        x: NpArray, y: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
    """Calculate distance along given axes for :term:`Minksowski metric`.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the Minkowsi distance by the
            respective p-norm. For p < 1, the function does not satisfy the
            triangle inequality and thus is not a valid metric, but a
            quasi-metric. For p >= 1 the Minkowski distance is a metric.
            Default: 2.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/p_norm
        [2] https://en.wikipedia.org/wiki/minkowski_distance

    """
    return norm_p(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def dist_manhatten(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate distance along given axes for :term:`Manhattan metric`.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return norm_1(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_euclid(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate distance along given axes for :term:`Euclidean metric`.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return norm_euclid(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_chebyshev(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate distance along given axes for :term:`Chebyshev metric`.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/maximum_norm
        [2] https://en.wikipedia.org/wiki/chebyshev_distance

    """
    return norm_max(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_pmean(
        x: NpArray, y: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
    """Calculate the :term:`Power-Mean difference` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the power mean difference by
            the respective power mean. For p < 1, the power mean does not
            satisfy the triangle inequality, such that the induced power mean
            difference is not a valid metric, but a quasi-metric. For p >= 1
            the power mean difference is a metric.
            Default: 2.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return norm_pmean(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def dist_amean(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate the :term:`Mean-Absolute difference` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return norm_amean(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_qmean(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate the :term:`Quadratic-Mean difference` along given axes.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    return norm_qmean(np.add(x, np.multiply(y, -1)), axis=axis)
