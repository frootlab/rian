# -*- coding: utf-8 -*-
"""Collection of Vector Space Norms and Metrices."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common import nfunc, nmodule
from nemoa.types import Any, NpAxis, NpArray, NpArrayLike, StrList

NORM_PREFIX = 'norm_'
DIST_PREFIX = 'dist_'

#
# Vector Space Norms
#

def norms() -> StrList:
    """Get sorted list of vector space norms.

    Returns:
        Sorted list of all vector norms, that are implemented within the module.

    """
    from nemoa.common import ndict

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = NORM_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(NORM_PREFIX)
    return sorted([v['name'][i:] for v in d.values()])

def length(x: NpArrayLike, norm: str = 'euclid', **kwargs: Any) -> NpArray:
    """Calculate generalized length of vector by given norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of vector norm. Accepted values are:
            'p': Class of p-Norms (induces: Minkowski distances)
                Remark: requires additional parameter 'p'
            '1': 1-Norm (induces: Manhatten distance, SAD)
            'euclid': Euclidean norm (induces: Euclidean distance, RSSD)
            'max': Maximum-Norm (induces: Chebyshev distance)
            'pmean': Class of Power Means (induce: power mean differences)
                Remark: requires additional parameter 'p'
            'amean': Arithmetic Mean (induces: Arithmetic mean difference)
            'qmean': Quadratic Mean (induces: Quadratic mean difference)
            'sd': Corrected Standard Deviation
            Default: 'euclid'
        **kwargs: Parameters of the given norm / class of norms.
            The norm Parameters are documented within the respective 'norm'
            functions.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    # Check Type of Argument 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be of type 'NumPy ArrayLike'") from err

    # Get norm function
    fname = NORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid value '{str(norm)}'")

    # Evaluate norm function
    return func(x, **nfunc.kwargs(func, default=kwargs))

def norm_p(x: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
    """Calculate p-norm of an array along given axis.

    The class of p-norms generalizes the Euclidean norm and the by replacing the
    square within its definition by arbitrary positive integers p [1].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive real number, which determines the p-norm by the p-th root of
            the summed p-th powered absolute values. For p < 1, the 'p-norm'
            does not satisfy the triangle inequality. In this case the 'p-norm'
            is a quasi-norm. For p >= 1 the p-norm is a norm.
            Default: 2
        axis: Index of axis (or axes) along which the function is performed.
            Within a 1d array the axis has index 0. In a 2d array the axis with
            index 0 is running across rows, and the axis with index 1 is running
            across columns. If axis is a tuple of ints, the function is
            performed over all axes in the tuple. If axis is None, the function
            is performed over all axes.
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/P_norm
        [2] https://en.wikipedia.org/wiki/Quasinorm

    """
    if p == 1.:
        return norm_1(x, axis=axis) # faster then generic implementation
    if p == 2.:
        return norm_euclid(x, axis=axis) # faster then generic implementation
    return np.power(np.sum(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def norm_1(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate 1-norm of an array along given axis.

    The 1-norm is the p-norm for p=1 and calculated by the sum of absolute
    values [1]. The induced metric, is the 'Manhatten distance' [2].

    With respect to a given sample the induced metric, is a sample statistic and
    referred as the 'Sum of Absolute Differences' (SAD) [3]. Due to the absolute
    value function, the SAD statistic is not differentiable, but more robust to
    outliers than the 'Root-Sum-Square Difference' (RSSD), which is induced by
    the Euclidean norm.

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

    References:
        [1] https://en.wikipedia.org/wiki/L1-norm
        [2] https://en.wikipedia.org/wiki/Manhattan_distance
        [3] https://en.wikipedia.org/wiki/Sum_of_absolute_differences

    """
    return np.sum(np.abs(x), axis=axis)

def norm_euclid(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Euclidean norm of an array along given axis.

    The Euclidean norm is the p-norm for p=2 and calculated by the root sum of
    squared values [1]. The induced metric, is the Euclidean distance [2], which
    is the natural distance in geometric interpretations.

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

    References:
        [1] https://en.wikipedia.org/wiki/euclidean_norm
        [2] https://en.wikipedia.org/wiki/euclidean_distance

    """
    return np.sqrt(np.sum(np.square(x), axis=axis))

def norm_max(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Maximum-norm of an array along given axis.

    The Maximum-norm is the limit of the p-norms for p -> infinity and
    calulated by the maximum of the absolute values [1]. The induced distance
    measure, which is derived from the Maximum-norm is the Chebyshev
    distance [2].

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

    References:
        [1] https://en.wikipedia.org/wiki/maximum_norm
        [2] https://en.wikipedia.org/wiki/chebyshev_distance

    """
    return np.amax(np.abs(x), axis=axis)

def norm_pmean(x: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
    """Calculate power means of an array along given axis.

    Just as the p-norms generalize the Euclidean norm, so do the power means
    generalize the Pythagorean means, for which reason they are also referred
    as 'generalized means' [1]. The power means equal the p-norms except
    for an additional normalization factor (1 / n) ** (1 / p), where n is the
    dimension of the vector space. Due to this linear dependency the power
    means are vector space norms and thus induce a class of metrices within
    their domains, referred as 'power mean differences'.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive real number, which determines the power mean by the p-th
            root of the averaged p-th powered absolute values. For p < 1, the
            power mean does not satisfy the triangle inequality. In this case
            power mean is a quasi-norm. For p >= 1 the power mean is a norm.
            Default: 2
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/power_mean

    """
    if p == 1.:
        return norm_amean(x, axis=axis) # faster then generic implementation
    if p == 2.:
        return norm_qmean(x, axis=axis) # faster then generic implementation
    return np.power(np.mean(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def norm_amean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Arithmetic Mean of the absolute values of an array.

    The 'Arithmetic Mean' is the power mean for p = 1 and equals the 1-norm
    except for the additional normalization factor (1 / n), where n is the
    dimension of the vector space [1]. Due to this linear dependency the
    Arithmetic Mean is a valid vector norm and thus induces a metric within its
    domain, which is referred as 'arithmetic mean difference'.

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

    References:
        [1] https://en.wikipedia.org/wiki/power_mean

    """
    return np.mean(np.abs(x), axis=axis)

def norm_qmean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate quadratic mean of an array along given axis.

    The Quadratic Mean or 'Root-Mean-Square' (RMS) [1], is the power mean
    for p = 2 and equals the Euclidean norm except for an additional
    normalization factor sqrt(1 / n), where n is the dimension of the vector
    space [2]. Due to this linear dependency the Quadratic Mean is a valid
    vector norm and thus induces a metric within its domain, which is referred
    as 'quadratic mean difference'.

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

    References:
        [1] https://en.wikipedia.org/wiki/root_mean_square
        [2] https://en.wikipedia.org/wiki/power_mean
        [3] https://en.wikipedia.org/wiki/root-mean-square_deviation

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

def norm_sd(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Corrected Standard Deviation of an array along given axis.

    The 'Corrected Standard Deviation' (SD) equals the Euclidean norm except for
    the additional preliminary factor sqrt(1 / (n - 1)), where n is the
    dimension of the vector space [1]. Due to this linear dependency the
    Standard Deviation is a valid vector norm and thus induces a metric within
    its domain.

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

    References:
        [1] https://en.wikipedia.org/wiki/sample_standard_deviation

    """
    return np.std(x, axis=axis)

#
# Vector Space Metrices and Generalized Vector Space Metrices
#

def metrices() -> StrList:
    """Get sorted list of vector space metrices.

    Returns:
        Sorted list of all vector space metrices and generalized vector space
        metrices, that are implemented within the module.

    """
    from nemoa.common import ndict

    # Declare and initialize return value
    dists: StrList = []

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = DIST_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(DIST_PREFIX)
    dists = sorted([v['name'][i:] for v in d.values()])

    return dists

def distance(
        x: NpArrayLike, y: NpArrayLike, metric: str = 'euclid',
        **kwargs: Any) -> NpArray:
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
        **kwargs: Parameters of the given metric or class of metrices.
            The Parameters are documented within the respective 'dist'
            functions.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/metric_(mathematics)
        [2] https://en.wikipedia.org/wiki/loss_function

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

    # Get distance function
    fname = DIST_PREFIX + metric.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'metric' has an invalid value '{str(metric)}'")

    # Evaluate distance function
    return func(x, y, **nfunc.kwargs(func, default=kwargs))

def dist_minkowski(
        x: NpArray, y: NpArray, p: float = 2., axis: NpAxis = 0) -> NpArray:
    """Calculate Minksowski distances of two arrays along given axis.

    The class of Minkowski distances is induced ba the p-norms [1] and
    generalizes the Euclidean and the Manhatten distance [2]. Thereby the
    p-norms replace the square within the definition of the Euclidean norm with
    an arbitrary power, given by a real number p >= 1 [1].

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the Minkowsi distance by the
            respective p-norm. For p < 1, the 'p-norm' does not satisfy the
            triangle inequality. In this case the induced 'Minkowski distance'
            is not a distance, but a quasi-metric. For p >= 1 the Minkowski
            distance is a metric.
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
    """Calculate Manhatten distances of two arrays along given axis.

    The Manhatten distance is the Minkowski distance for p = 1 and induced by
    the 1-norm [1].

    With respect to a given sample the Manhatten distance, can be interpreted as
    a metric in the space of random variables, and is referred as the
    'Sum of Absolute Differences' (SAD) [2]. Due to the absolute value
    function, the Manhatten distance is not differentiable but more robust to
    outliers than the Euclidean distance.

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
        [1] https://en.wikipedia.org/wiki/manhattan_distance
        [2] https://en.wikipedia.org/wiki/sum_of_absolute_differences

    """
    return norm_1(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_euclid(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Euclidean distances of two arrays along given axis.

    The Euclidean distance is induced by the Euclidean norm [1] and the natural
    distance in geometric interpretations [2].

    With respect to a given sample the Euclidean distance, can be interpred as a
    metric in the space of random variables, and is referred as the
    'Root-Sum-Square Deviation' (RSSD). An important application is the method
    of least squares [3].

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

    References:
        [1] https://en.wikipedia.org/wiki/euclidean_norm
        [2] https://en.wikipedia.org/wiki/euclidean_distance
        [3] https://en.wikipedia.org/wiki/least_squares

    """
    return norm_euclid(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_chebyshev(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Chebyshev distances of two arrays along given axis.

    The Chebyshev distance is induced be the maximum norm [1] and also known as
    chessboard distance, since in the game of chess it equals the minimum number
    of moves needed by a king to go from one square to another [2].

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
    """Calculate power mean difference of two arrays along given axis.

    Just as the p-norms generalize the Euclidean norm, so do the power means,
    generalize the Pythagorean means, for which they are also referred as
    generalized means [1].

    With respect to given samples the distances, which are induced by
    power means are Risk-functions [2]. Examples are the 'Mean Absolute
    Difference' (MAD) [3], which is induced by the arithmetic mean and the
    'Root-Mean-Square Error' (RMSE) [4], which is induced by the quadratic mean.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive real number, which determines the power mean difference by
            the respective power mean. For p < 1, the power mean does not
            satisfy the triangle inequality. In this case the induced power mean
            difference is not a valid metric, but a quasi-metric. For p >= 1 the
            power mean difference is a metric.
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
        [1] https://en.wikipedia.org/wiki/power_mean
        [2] https://en.wikipedia.org/wiki/risk_function
        [3] https://en.wikipedia.org/wiki/mean_absolute_error
        [4] https://en.wikipedia.org/wiki/root-mean-square_error

    """
    return norm_pmean(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def dist_amean(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Arithmetic mean difference of two arrays along given axis.

    The Arithmetic mean difference is the metric, which is induced by the
    arithmetic mean of the absolute values [1], which equals the 1-norm
    multiplied by the prefactor (1 / n), where n is the dimension of the
    underlying vector space [2].

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
        [1] https://en.wikipedia.org/wiki/mean_absolute_error
        [2] https://en.wikipedia.org/wiki/generalized_mean

    """
    return norm_amean(np.add(x, np.multiply(y, -1)), axis=axis)

def dist_qmean(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Quadratic mean difference of two arrays along given axis.

    The Quadratic mean difference is the metric, which is induced by
    the Quadratic Mean, which equals the Euclidean norm multiplied by the
    prefactor sqrt(1 / n), where n is the dimension of the vector space [1].

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
        [1] https://en.wikipedia.org/wiki/power_mean

    """
    return norm_qmean(np.add(x, np.multiply(y, -1)), axis=axis)
