# -*- coding: utf-8 -*-
"""Collection of Vector Space Norms and Metrics."""

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
from nemoa.types import StrList, NpAxis, NpArray, NpArrayLike

VECNORM_PREFIX = 'vecnorm_'
VECDIST_PREFIX = 'vecdist_'

#
# Vector Space Norms and Vector Space Pseudo Norms
#

def vecnorms() -> StrList:
    """Get sorted list of vector space norms and vector space pseudo norms.

    Returns:
        Sorted list of all vector norms and pseudo vector norms, that are
        implemented within the module.

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

def vecnorm(x: NpArrayLike, norm: str, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate vector norm or pseudo vector norm along given axis.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of vector norm. Accepted values are:
            'lp': Class of lp-Norms (induces: lp-distances)
            'l1': l1-Norm (induces: Manhattan distance, SAD)
            'l2': l2-Norm (induces: Euclidean distance, RSSD)
            'max': Maximum-Norm (induces: Chebyshev distance)
            'mp': Class of Generalized Mean Norms (induce: mp-distances)
            'm1': Absolute Mean (induces: MAE)
            'm2': Quadratic Mean (induces: RMSD)
            'SS': Sum of Squares, pseudo norm (induces: SSD)
            'MS': Mean Square, pseudo norm (induces: MSD)
            'SD': Corrected Standard Deviation (induces: Bias)
        p: Positive integer, which parameterizes the respective p-norm. If the
            argument 'norm' is not a p-norm, then 'p' is not used.
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
    # Check Type of Argument 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be 'NumPy ArrayLike'") from err

    # Get Metric function
    fname = VECNORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid value '{str(norm)}'")

    # Declare return value and evaluate metric
    arr: NpArray
    if 'p' in nfunc.kwargs(func):
        arr = func(x, p=p, axis=axis)
    else:
        arr = func(x, axis=axis)

    return arr

def vecnorm_lp(x: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate lp-norm of an array along given axis.

    The class of lp-norms generalizes the Euclidean norm by replacing the
    square within its definition by arbitrary positive integers p [1].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive integer, which determines the lp-norm by the p-th root of
            the summed p-th powered absolute values.
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
        [1] https://en.wikipedia.org/wiki/Lp_norm

    """
    if p == 1:
        return vecnorm_l1(x, axis=axis) # faster then generic implementation
    if p == 2:
        return vecnorm_l2(x, axis=axis) # faster then generic implementation
    return np.power(np.sum(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def vecnorm_l1(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate l1-norm of an array along given axis.

    The l1-norm is the lp-norm for p=1 and calculated by the sum of absolute
    values [1]. The induced metric, is the 'Manhattan distance' [2].

    With respect to a given sample the induced metric, is a sample statistic and
    referred as the 'Sum of Absolute Differences' (SAD) [3]. Due to the absolute
    value function, the SAD statistic is not differentiable, but more robust to
    outliers than the 'Root-Sum-Square Difference' (RSSD), which is induced by
    the l2-norm.

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

def vecnorm_l2(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate L2-Norm of an array along given axis.

    The l2-norm is the lp-norm for p=2 and calculated by the root sum of squared
    values [1]. The induced metric, is the Euclidean distance [2], which is the
    natural distance in geometric interpretations.

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
        [1] https://en.wikipedia.org/wiki/L2-norm
        [2] https://en.wikipedia.org/wiki/Euclidean_distance
        [3] https://en.wikipedia.org/wiki/Least_squares

    """
    return np.sqrt(np.sum(np.square(x), axis=axis))

def vecnorm_max(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Maximum-norm of an array along given axis.

    The Maximum-norm is the limit of the lp-norms for p -> infinity and
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

def vecnorm_mp(x: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate generalized means of an array along given axis.

    Just as the lp-Norms generalize the Euclidean distance, so do the mp-Norms
    generalize the Pythagorean means, for which reason they are also referred
    as 'Generalized Means' [1]. The Generalized Means equal the lp-Norms except
    for an additional preliminary factor (1 / n) ** (1 / p), where n is the
    dimension of the vector space. Due to this linear dependency the Generalized
    Means are vector space Norms and thus induce a class of metrics within their
    domains. This class is referred as 'Generalized Mean Distances'.

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
        [1] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return np.power(np.mean(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def vecnorm_m1(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate absolute mean of an array along given axis.

    The 'Absolute Mean' is the generalized mean for p=1 (m1-Norm) and equals the
    l1-Norm except for the additional preliminary factor (1 / n), where n is the
    dimension of the vector space. Due to this linear dependency the Absolute
    Mean is a vector space norm and induces a metric within its domain.

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
        [1] https://en.wikipedia.org/wiki/Generalized_mean
        [2] https://en.wikipedia.org/wiki/Mean_absolute_error

    """
    return np.mean(np.abs(x), axis=axis)

def vecnorm_m2(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate quadratic mean of an array along given axis.

    The Quadratic Mean or 'Root-Mean-Square' (RMS) [1], is the generalized mean
    for p=2 (m2-Norm) and equals the l2-Norm except for the additional
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
        [1] https://en.wikipedia.org/wiki/Root_mean_square
        [2] https://en.wikipedia.org/wiki/Generalized_mean
        [3] https://en.wikipedia.org/wiki/Root-mean-square_deviation

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

def vecnorm_ss(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate the Sum of Squares of an Array along given axis.

    The 'Sum of Squares' (SS) equals the square of the l2-Norm [1]. Due to this
    nonlinear dependency the Sum of Squares does not satisfy the property of
    absolute homogeneity and is therefore not a vector norm. Since the Sum of
    Squares however is positive definite, subhomogeneous and subadditive, it is
    a vector space pseudo norm [2] and thus induces a metric within its domain.

    With respect to a given sample the induced metric is a sample statistic,
    which is referred as the Residual Sum of Squares (RSS) [3]. The RSS is used
    in regression analysis to quantify the unexplained variation of a model [4].

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
        [1] https://en.wikipedia.org/wiki/Sum_of_squares
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Residual_sum_of_squares
        [4] https://en.wikipedia.org/wiki/Explained_variation

    """
    return np.sum(np.square(x), axis=axis)

def vecnorm_ms(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Square of an array along given axis.

    The 'Mean Square' (MS) equals the square of the m2-Norm [1]. Due to this
    nonlinear dependency the Mean Square does not satisfy the property of
    absolute homogeneity and is therefore not a vector norm. Since the Mean
    Square however is positive definite, subhomogeneous and subadditive, it is
    a vector space pseudo norm [2] and thus induces a metric within its domain.

    With respect to a given sample the induced metric is a sample statistic,
    which is referred as the 'Mean Squared Difference' (MSD) [3], which is used
    as a risk function to measure of the quality estimators [4].

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
        [1] https://en.wikipedia.org/wiki/Mean_square
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Mean_squared_deviation
        [4] https://en.wikipedia.org/wiki/Risk_function

    """
    return np.mean(np.square(x), axis=axis)

def vecnorm_sd(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Corrected Standard Deviation of an array along given axis.

    The 'Corrected Standard Deviation' (SD) equals the l2-Norm except for the
    additional preliminary factor sqrt(1 / (n - 1)), where n is the dimension of
    the vector space [1]. Due to this linear dependency the Standard Deviation
    is a vector space norm and induces a metric within its domain.

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
        [1] https://en.wikipedia.org/wiki/Sample_standard_deviation

    """
    return np.std(x, axis=axis)

#
# Vector Metrics and Vector Premetrics
#

def vecdists() -> StrList:
    """Get sorted list of vector distance functions.

    Returns:
        Sorted list of all vector distance functions, that are implemented
        within the module.

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
        x: NpArrayLike, y: NpArrayLike, metric: str, p: int = 1,
        axis: NpAxis = 0) -> NpArray:
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
        metric: Name of used metric:
            'lp': Class of lp-Distances (induces by lp-Norms)
            'l1': Manhattan Distance (induced by l1-Norm)
            'l2': Euclidean Distance (induced by l2-Norm)
            'max': Chebyshev Distance (induced by Maximum-Norm)
            'mp': Class of Generalized Mean Distances (induces by mp-Norms)
            'MAD': Mean Absolute Difference (induced by m1-Norm)
            'RMSD': Root-Mean-Square Difference (induced by m2-Norm)
            'SSD': Sum of Squared Differences (induces by Sum of Squares)
            'MSD': Mean Square Difference (induced by Mean Square)
        p: Positive integer, which parameterizes the respective p-distance. If
            the argument 'metric' is not a p-distance, then 'p' is not used.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Metric_(mathematics)
        [2] https://en.wikipedia.org/wiki/Loss_function

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

    # Check dtypes and shapes of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Get Metric function
    fname = VECNORM_PREFIX + metric.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'metric' has an invalid value '{str(metric)}'")

    # Declare return value and evaluate metric
    arr: NpArray
    if 'p' in nfunc.kwargs(func):
        arr = func(x, y, p=p, axis=axis)
    else:
        arr = func(x, y, axis=axis)

    return arr

def vecdist_lp(x: NpArray, y: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate lp-distances of two arrays along given axis.

    The class of lp-distances generalizes the Euclidean distance by evaluation
    of the respective lp-norm of the differences instead of the Euclidean norm.
    Thereby the lp-norms replace the square within the definition of the
    Euclidean norm with an arbitrary positive integers p [1].

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive integer, which determines the lp-distance by the respective
            lp-norm
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Lp_norm

    """
    return vecnorm_lp(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_l1(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Manhatten distances of two arrays along given axis.

    The Manhatten distance is the lp-distance for p=1 and induced by the
    l1-norm [1]. With respect to a given sample the Manhatten distance, can be
    interpreted as a metric in the space of random variables, and is referred
    as the 'Sum of Absolute Differences' (SAD) [2]. Due to the absolute value
    function, Manhatten distance is not differentiable but more robust to
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
        [1] https://en.wikipedia.org/wiki/Manhattan_distance
        [2] https://en.wikipedia.org/wiki/Sum_of_absolute_differences

    """
    return vecnorm_l1(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_l2(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Euclidean distances of two arrays along given axis.

    The Euclidean distance is induced be the l2-norm [1] and the natural
    distance in geometric interpretations [2]. With respect to a given sample
    the Euclidean distance, can be interpred as a metric in the space of
    random variables, and is referred as the 'Root-Sum-Square Deviation' (RSSD).
    An important application is the method of least squares [3].

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
        [1] https://en.wikipedia.org/wiki/L2-norm
        [2] https://en.wikipedia.org/wiki/Euclidean_distance
        [3] https://en.wikipedia.org/wiki/Least_squares

    """
    return vecnorm_l2(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_max(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Chebyshev distances of two arrays along given axis.

    The Chebyshev distance is induced be the Maximum-norm [1].

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
        [1] https://en.wikipedia.org/wiki/Chebyshev_distance

    """
    return vecnorm_max(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_mp(x: NpArray, y: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate Generalized Mean distances of two arrays along given axis.

    Just as the lp-norms generalize the Euclidean distance, so do the mp-norms,
    generalize the Pythagorean means, for which they are also referred as
    generalized means [1]. With respect to given samples the distances,
    which are induced by generalized means are Risk-functions [2]. Examples
    are the 'Mean Absolute Error' (MAE) [3], which is induced by the absolute
    mean and the 'Root-Mean-Square Error' (RMSE) [4], which is induced by the
    quadratic mean.

    Args:
        x: NumPy ndarray with numeric values of arbitrary dimension.
        y: NumPy ndarray with same dimension, shape and datatypes as 'x'
        p: Positive integer, which determines the mp-distance by the p-th root
            of the averaged p-th powered absolute values.
        axis: Axis (or axes) along which the distance is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Generalized_mean
        [2] https://en.wikipedia.org/wiki/Risk_function
        [3] https://en.wikipedia.org/wiki/Mean_absolute_error
        [4] https://en.wikipedia.org/wiki/Root-mean-square_error

    """
    return vecnorm_mp(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_mad(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Absolute Difference of two arrays along given axis.

    The 'Mean Absolute Difference' (MAD) is the distance function, which is
    induced by the Absolute Mean [1] to a space of random variables. Thereby the
    Absolute Mean equals the l1-norm multiplied by the prefactor (1 / d), where
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
        [1] https://en.wikipedia.org/wiki/Mean_absolute_error
        [2] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return vecnorm_m1(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_rmsd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Root-Mean-Square Difference of two arrays along given axis.

    The 'Root-Mean-Square Difference' (RMSD) is the metric, which is induced by
    the Quadratic Mean to a space of random variables [1, 2]. Thereby the
    Quadritic Mean equals the l2-norm multiplied by the prefactor sqrt(1 / n),
    where d is the size of the underlying sample [3]. Consequently for an
    unbiased estimator, the RMSD is the square root of the variance and thus the
    uncorrected standard deviation.

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
        [1] https://en.wikipedia.org/wiki/Root_mean_square
        [2] https://en.wikipedia.org/wiki/Root-mean-square_error
        [3] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return vecnorm_m2(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_ssd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Sum of Squared Differences of two arrays along given axis.

    The 'Sum of Squared Differences' (SSD) is the metric, which is induced by
    the 'Sum of Squares' pseudo norm to a space of random variables [1, 2]. The
    SSD is used in regression analysis to quantify the unexplained variation of
    a model [3].

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
    return vecnorm_ss(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_msd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Square Difference of two arrays along given axis.

    The 'Mean Square Difference' (MSD) is the metric, which is induced by the
    Mean Square pseudo norm to a space of random variables [1, 2]. The Mean
    Square Difference is used in mathematical optimization and statistics as a
    risk function [3, 4]. ... (RSS)

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
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Mean_squared_error
        [4] https://en.wikipedia.org/wiki/Risk_function

    """
    return vecnorm_ms(np.add(x, np.multiply(y, -1)), axis=axis)

#vecdist_manhattan = vecdist_l1
#vecdist_sad = vecdist_l1
#vecdist_taxicab = vecdist_l1
#vecdist_block = vecdist_l1
#vecdist_euclid = vecdist_l2
#vecdist_rmse = vecdist_rmsd
