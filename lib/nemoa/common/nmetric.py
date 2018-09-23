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

VECNORM_PREFIX = 'vecnorm_'
VECDIST_PREFIX = 'vecdist_'

#
# Vector Space Norms and Generalized Vector Space Norms
#

def vecnorms() -> StrList:
    """Get sorted list of vector space norms.

    Returns:
        Sorted list of all vector norms, that are implemented within the module.

    """
    from nemoa.common import ndict

    # Declare and initialize return value
    norms: StrList = []

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = VECNORM_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(VECNORM_PREFIX)
    norms = sorted([v['name'][i:] for v in d.values()])

    return norms

def vecnorm(x: NpArrayLike, norm: str, **kwargs: Any) -> NpArray:
    """Calculate vector norm or (pseudo / semi) vector norm along given axis.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of vector norm. Accepted values are:
            'p': Class of p-Norms (induces: Minkowski distances)
            '1': 1-Norm (induces: Manhatten distance, SAD)
            'euclid': Euclidean norm (induces: Euclidean distance, RSSD)
            'max': Maximum-Norm (induces: Chebyshev distance)
            'pmean': Class of Power Means (induce: pmean distances)
            'amean': Absolute Mean (induces: MAE)
            'qmean': Quadratic Mean (induces: RMSD)
            'sd': Corrected Standard Deviation
        **kwargs: Parameters of the given norm / class of norms.
            The norm Parameters are documented within the respective 'vecnorm'
            functions.

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    """
    # Check Type of Argument 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be 'NumPy ArrayLike'") from err

    # Get norm function
    fname = VECNORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid value '{str(norm)}'")

    # Evaluate norm function
    return func(x, **nfunc.kwargs(func, default=kwargs))

def vecnorm_p(x: NpArray, p: float = 1., axis: NpAxis = 0) -> NpArray:
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
            is a quasinorm.
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
        return vecnorm_1(x, axis=axis) # faster then generic implementation
    if p == 2.:
        return vecnorm_euclid(x, axis=axis) # faster then generic implementation
    return np.power(np.sum(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def vecnorm_1(x: NpArray, axis: NpAxis = 0) -> NpArray:
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
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/L1-norm
        [2] https://en.wikipedia.org/wiki/Manhattan_distance
        [3] https://en.wikipedia.org/wiki/Sum_of_absolute_differences

    """
    return np.sum(np.abs(x), axis=axis)

def vecnorm_euclid(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Euclidean norm of an array along given axis.

    The Euclidean norm is the p-norm for p=2 and calculated by the root sum of
    squared values [1]. The induced metric, is the Euclidean distance [2], which
    is the natural distance in geometric interpretations.

    With respect to a given sample the induced metric, is a sample statistic and
    referred as the 'Root-Sum-Square Difference' (RSSD). An important
    application is the method of least squares [3].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Euclidean_norm
        [2] https://en.wikipedia.org/wiki/Euclidean_distance
        [3] https://en.wikipedia.org/wiki/Least_squares

    """
    return np.sqrt(np.sum(np.square(x), axis=axis))

def vecnorm_max(x: NpArray, axis: NpAxis = 0) -> NpArray:
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
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Maximum_norm
        [2] https://en.wikipedia.org/wiki/Chebyshev_distance

    """
    return np.amax(np.abs(x), axis=axis)

def vecnorm_pmean(x: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate power means of an array along given axis.

    Just as the p-norms generalize the Euclidean norm, so do the power means
    generalize the Pythagorean means, for which reason they are also referred
    as 'generalized means' [1]. The power means equal the p-norms except
    for an additional preliminary factor (1 / n) ** (1 / p), where n is the
    dimension of the vector space. Due to this linear dependency the power
    means are vector space norms and thus induce a class of metrices within
    their domains. This class is referred as 'power mean distances'.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive integer, which determines the mp-norm by the p-th root of
            the averaged p-th powered absolute values.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/power_mean

    """
    return np.power(np.mean(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def vecnorm_amean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate absolute mean of an array along given axis.

    The 'Absolute Mean' is the power mean for p = 1 and equals the 1-norm except
    for the additional preliminary factor (1 / n), where n is the dimension of
    the vector space. Due to this linear dependency the Absolute Mean is a
    vector space norm and induces a metric within its domain.

    With respect to a given sample the induced metric, is a sample statistic and
    referred as the 'Mean Absolute Error' (MAE) [2].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/power_mean
        [2] https://en.wikipedia.org/wiki/mean_absolute_error

    """
    return np.mean(np.abs(x), axis=axis)

def vecnorm_qmean(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate quadratic mean of an array along given axis.

    The Quadratic Mean or 'Root-Mean-Square' (RMS) [1], is the power mean
    for p = 2 and equals the Euclidean norm except for the additional
    preliminary factor sqrt(1 / n), where n is the dimension of the vector
    space [2]. Due to this linear dependency the Quadratic Mean is a vector
    space norm and induces a metric within its domain.

    With respect to a given sample the induced metric, is a sample statistic and
    referred as the 'Root-mean-squared deviation' (RMSD) [3].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/root_mean_square
        [2] https://en.wikipedia.org/wiki/power_mean
        [3] https://en.wikipedia.org/wiki/root-mean-square_deviation

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

def vecnorm_sd(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Corrected Standard Deviation of an array along given axis.

    The 'Corrected Standard Deviation' (SD) equals the Euclidean norm except for
    the additional preliminary factor sqrt(1 / (n - 1)), where n is the
    dimension of the vector space [1]. Due to this linear dependency the
    Standard Deviation is a vector space norm and induces a metric within its
    domain.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/sample_standard_deviation

    """
    return np.std(x, axis=axis)

#
# Vector Space Metrices and Generalized Vector Space Metrices
#

def vecmetrices() -> StrList:
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
    pattern = VECDIST_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(VECDIST_PREFIX)
    dists = sorted([v['name'][i:] for v in d.values()])

    return dists

def vecdist(
        x: NpArrayLike, y: NpArrayLike, metric: str, **kwargs: Any) -> NpArray:
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
        metric: Name of metric (or generalized metric):
            'minkowski': Minkowski distances (induces by p-Norms)
            'manhatten': Manhatten distance (induced by 1-Norm)
            'euclid': Euclidean distance (induced by Euclidean norm)
            'chebyshev': Chebyshev distance (induced by Maximum-Norm)
            'pmean': Class of Power Mean distances (induced by power means)
            'mad': Mean Absolute Difference (induced by absolute mean)
            'rmsd': Root-Mean-Square Difference (induced by quadratic mean)
            'ssd': Sum of Square Difference (induces by Sum of Squares)
            'msd': Mean Square Difference (induced by Mean Square)
        **kwargs: Parameters of the given metric or class of metrices.
            The Parameters are documented within the respective 'vecdist'
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
    fname = VECDIST_PREFIX + metric.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'metric' has an invalid value '{str(metric)}'")

    # Evaluate distance function
    return func(x, y, **nfunc.kwargs(func, default=kwargs))

def vecdist_minkowski(
        x: NpArray, y: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
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
            is not a distance, but a quasi-metric.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/p_norm
        [2] https://en.wikipedia.org/wiki/minkowski_distance

    """
    return vecnorm_p(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_manhatten(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
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
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/manhattan_distance
        [2] https://en.wikipedia.org/wiki/sum_of_absolute_differences

    """
    return vecnorm_1(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_euclid(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
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
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/euclidean_norm
        [2] https://en.wikipedia.org/wiki/euclidean_distance
        [3] https://en.wikipedia.org/wiki/least_squares

    """
    return vecnorm_euclid(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_chebyshev(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
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
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/maximum_norm
        [2] https://en.wikipedia.org/wiki/chebyshev_distance

    """
    return vecnorm_max(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_pmean(
        x: NpArray, y: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate power mean difference of two arrays along given axis.

    Just as the p-norms generalize the Euclidean norm, so do the power means,
    generalize the Pythagorean means, for which they are also referred as
    generalized means [1].

    With respect to given samples the distances, which are induced by
    power means are Risk-functions [2]. Examples are the 'Mean Absolute
    Difference' (MAD) [3], which is induced by the absolute mean and the
    'Root-Mean-Square Error' (RMSE) [4], which is induced by the quadratic mean.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive integer, which determines the power mean distance by the
            p-th root of the averaged p-th powered absolute values.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/power_mean
        [2] https://en.wikipedia.org/wiki/risk_function
        [3] https://en.wikipedia.org/wiki/mean_absolute_error
        [4] https://en.wikipedia.org/wiki/root-mean-square_error

    """
    return vecnorm_pmean(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_mad(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Absolute Difference of two arrays along given axis.

    The 'Mean Absolute Difference' (MAD) is the distance function, which is
    induced by the absolute mean [1] to a space of random variables. Thereby the
    Absolute Mean equals the 1-norm multiplied by the prefactor (1 / d), where
    d is the size of the underlying sample [2].

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/mean_absolute_error
        [2] https://en.wikipedia.org/wiki/generalized_mean

    """
    return vecnorm_amean(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_rmsd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Root-Mean-Square Difference of two arrays along given axis.

    The 'Root-Mean-Square Difference' (RMSD) is the metric, which is induced by
    the Quadratic Mean to a space of random variables [1, 2]. Thereby the
    Quadritic Mean equals the Euclidean norm multiplied by the prefactor
    sqrt(1 / n), where d is the size of the underlying sample [3]. Consequently
    for an unbiased estimator, the RMSD is the square root of the variance and
    thus the uncorrected standard deviation.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/root_mean_square
        [2] https://en.wikipedia.org/wiki/root-mean-square_error
        [3] https://en.wikipedia.org/wiki/power_mean

    """
    return vecnorm_qmean(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_ssd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Sum of Squares Differences of two arrays along given axis.

    The 'Sum of Squares Difference' (SSD) is a semi metric, which is induced by
    the Sum of Squares. The Sum of Squares is given by the square of the
    Euclidean norm [1] and therefore non-convex. Consequently the Sum of Squares
    does not satisfy the property of absolute homogeneity nor the triangle
    inequality and is therefore not a vector norm. Since the Sum of Squares
    however is positive definite and subhomogeneous, it induces a semi metric
    within its domain.

    With respect to a given sample the induced semi metric is a sample
    statistic, which is referred as the Sum of Squares Difference or the
    'Residual Sum of Squares' (RSS) [3]. The RSS is used in regression analysis
    to quantify the unexplained variation of a model [4].

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Sum_of_squares
        [2] https://en.wikipedia.org/wiki/Residual_sum_of_squares
        [3] https://en.wikipedia.org/wiki/Explained_variation

    """
    return np.sum(np.square(np.add(x, np.multiply(y, -1))), axis=axis)

def vecdist_msd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Square Differences of two arrays along given axis.

    The 'Mean Squared Difference' (MSD) is a semi metric, which is induced by
    the 'Mean Square' (MS) [1]. The Mean Square in turn equals the square of the
    m2-Norm. Due to this nonlinear dependency the Mean Square does not satisfy
    the property of absolute homogeneity nor the triangle inequality and is
    therefore not a vector norm. Since the Mean Square however is positive
    definite and subhomogeneous, it induces a semi metric within its
    domain.

    With respect to a given sample the induced semi metric is a sample
    statistic, which is referred as the 'Mean Squared Difference'. Applied to
    an estimator, the MSD is also referred as the Mean Squared Deviation or
    the 'Mean Squared Error' (MSE) [2]. In this context the MSE is a measure of
    the quality in terms of the expected loss of an estimator [3].

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Mean_square
        [2] https://en.wikipedia.org/wiki/Mean_squared_error
        [3] https://en.wikipedia.org/wiki/Risk_function

    """
    return np.mean(np.square(np.add(x, np.multiply(y, -1))), axis=axis)
