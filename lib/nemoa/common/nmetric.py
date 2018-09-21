# -*- coding: utf-8 -*-
"""Collection of vector norms and distance functions."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common import nmodule
from nemoa.types import StrList, NpAxis, NpArray, NpArrayLike

VECNORM_PREFIX = 'vecnorm_'
VECDIST_PREFIX = 'vecdist_'

#
# Vector norms and pseudo norms
#

def vecnorms() -> StrList:
    """Get sorted list of (generalized) vector norms.

    Returns:
        Sorted list of all (generalized) vector norms, that are implemented
        within the module.

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
    """Calculate (generalized) vector norm along given axis.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of vector norm. Accepted values are:
            'lp': Class of lp-Norms (induces: lp-distances)
            'l1': l1-Norm (induces: Manhattan distance, SAD)
            'l2': l2-Norm (induces: Euclidean distance, RSSE)
            'max': Maximum-Norm (induces: Chebyshev distance)
            'mp': Class of generalized means (induces: mp-distances)
            'm1': Absolute Mean (induces: MAE)
            'm2': Quadratic Mean (induces: RMSE)
            'SD': Standard Deviation (induces: Bias)
            'dot': Dot product, pseudo norm (induces: RSS)
            'ME': Mean Square product, pseudo norm (induces: MSE)
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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    # Check argument 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be 'ArrayLike'") from err

    # Declare return value
    array: NpArray

    fname = VECNORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        array = getattr(module, fname)(x, axis=axis)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid value '{str(norm)}'")

    return array

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

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
    values [1]. The induced metric, is the 'Manhattan distance' [2]. With
    respect to a given sample the induced distance, can be interpreted as a
    metric in the space of random valiables, and is referred as the 'Sum of
    Absolute Differences' (SAD) [3]. Due to the absolute value function, the
    l1-norm is not differentiable but more robust to outliers than the l2-norm.

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

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
    natural distance in geometric interpretations. With respect to a given
    sample the induced distance, can be interpred as a metric in the space of
    random variables, and is referred as the 'Root-Sum-Square Error' (RSSE). An
    important application is the method of least squares [3].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Maximum_norm
        [2] https://en.wikipedia.org/wiki/Chebyshev_distance

    """
    return np.amax(np.abs(x), axis=axis)

def vecnorm_mp(x: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate generalized means of an array along given axis.

    Just as the lp-norms generalize the Euclidean distance, so do the mp-norms
    generalize the Pythagorean means, for which reason they are also referred
    as generalized means [1].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return np.power(np.mean(np.power(np.abs(x), p), axis=axis), 1. / float(p))

def vecnorm_m1(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate absolute mean of an array along given axis.

    The absolute mean (aka 'm1-norm') is the generalized mean for p=1 and
    equals the l1-norm multiplied by the prefactor (1 / n), where n is the
    dimension of the vector space [1]. With respect to a given sample the
    m1-norm induces a metric to the space of random valiables, which is known as
    the 'Mean Absolute Error' (MAE) [2].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Generalized_mean
        [2] https://en.wikipedia.org/wiki/Mean_absolute_error

    """
    return np.mean(np.abs(x), axis=axis)

def vecnorm_m2(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate quadratic mean of an array along given axis.

    The quadratic mean, aka 'm2-norm' or 'Root-Mean-Square' (RMS) [1], is the
    generalized mean for p=1 and equals the l2-norm multiplied by the prefactor
    sqrt(1 / n), where n is the dimension of the vector space. With respect to a
    given sample the m2-norm induces a metric to the space of random valiables,
    which is known as the 'Root-Mean-Square Error' (RMSE) [3].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Root_mean_square
        [2] https://en.wikipedia.org/wiki/Generalized_mean
        [3] https://en.wikipedia.org/wiki/Root-mean-square_error

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

def vecnorm_dot(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate the dot product of an array along given axis.

    The dot product satisfies all properties of a norm, except the absolute
    homogeneity [1]. Since the dot product however is abolute homogeneous of
    positive degree 2 and therefore in particular subhomogeneous, it is a
    pseudo norm [2]. Consequently the dot product also induces a metric to the
    vector space. This is the 'Residual Sum of Squares' (RSS) [3], which is used
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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Dot_product
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Residual_sum_of_squares
        [4] https://en.wikipedia.org/wiki/Explained_variation

    """
    return np.sum(np.square(x), axis=axis)

def vecnorm_ms(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Square of an array along given axis.

    The Mean Square satisfies all properties of a norm, except the absolute
    homogeneity. Since the Mean Square however is abolute homogeneous of
    positive degree 2 and therefore in particular subhomogeneous, it is a
    pseudo norm [2]. Consequently the Mean Square also induces a metric to the
    vector space. With respect to a given sample, this is the 'Mean Squared
    Error' (MSE) [3], which is used in mathematical optimization and statistics
    as a risk function [4].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Mean_square
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Mean_squared_error
        [4] https://en.wikipedia.org/wiki/Risk_function

    """
    return np.mean(np.square(x), axis=axis)

def vecnorm_sd(x: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate standard deviation of an array along given axis.

    The 'Standard Deviation' (SD) defines a valid norm on the vector space of
    mean zero random variables [1]. For a given sample the standard deviation
    has an unbiased estimator by the 'Corrected Sample Standard Deviation' [2],
    which equals the l2-norm multiplied by the factor sqrt(1 / (d - 1)), where
    d is the size of the sample. The induced metric is the 'Bias' between random
    variables, which is used to evaluate the consistency of estimators [3].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://stats.stackexchange.com/questions/269405
        [2] https://en.wikipedia.org/wiki/Sample_standard_deviation
        [3] https://en.wikipedia.org/wiki/Bias_of_an_estimator

    """
    return np.std(x, axis=axis)

#
# Vector distance functions
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
        x: NpArrayLike, y: NpArrayLike, norm: str, axis: NpAxis = 0) -> NpArray:
    """Calculate vector distances of two arrays along given axis.

    A vector distance function, also known as metric, is a function d(x, y),
    which quantifies the proximity of vectors in a vector space as non-negative
    real numbers. If the distance is zero, then the vectors are equivalent with
    respect to the distance function [1]. Distance functions are often used as
    error, loss or risk functions, for statistical estimations [2].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            shape as ´x´.
        norm: Name of vector norm, which induces the distance:
            'lp': Class of lp-Norms (induces: lp-distances)
            'l1': l1-Norm (induces: Manhattan distance, SAD)
            'l2': l2-Norm (induces: Euclidean distance, RSSE)
            'max': Maximum-Norm (induces: Chebyshev distance)
            'mp': Class of generalized means (induces: mp-distances)
            'm1': Absolute Mean (induces: MAE)
            'm2': Quadratic Mean (induces: RMSE)
            'SD': Standard Deviation (induces: Bias)
            'dot': Dot product, pseudo norm (induces: RSS)
            'ME': Mean Square product, pseudo norm (induces: MSE)
        p: Positive integer, which parameterizes the respective p-distance. If
            the argument 'norm' is not a p-norm, then 'p' is not used.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

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

    # Calculate difference from 'x' and 'y'
    try:
        d = np.add(x, np.multiply(y, -1))
    except ValueError as err:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together") from err

    return vecnorm(d, norm=norm, axis=axis)

def vecdist_lp(x: NpArray, y: NpArray, p: int = 1, axis: NpAxis = 0) -> NpArray:
    """Calculate lp-distances of two arrays along given axis.

    The class of lp-distances generalizes the Euclidean distance by evaluation
    of the respective lp-norm of the differences instead of the Euclidean norm.
    Thereby the lp-norms replace the square within the definition of the
    Euclidean norm with an arbitrary positive integers p [1].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        p: Positive integer, which determines the lp-distance by the respective
            lp-norm
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Lp_norm

    """
    return vecnorm_lp(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_manhatten(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Manhatten distances of two arrays along given axis.

    The Manhatten distance is the lp-distance for p=1 and induced by the
    l1-norm [1]. With respect to a given sample the Manhatten distance, can be
    interpreted as a metric in the space of random valiables, and is referred
    as the 'Sum of Absolute Differences' (SAD) [2]. Due to the absolute value
    function, Manhatten distance is not differentiable but more robust to
    outliers than the Euclidean distance.

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Manhattan_distance
        [2] https://en.wikipedia.org/wiki/Sum_of_absolute_differences

    """
    return vecnorm_l1(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_euclid(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Euclidean distances of two arrays along given axis.

    The Euclidean distance is induced be the l2-norm [1] and the natural
    distance in geometric interpretations [2]. With respect to a given sample
    the Euclidean distance, can be interpred as a metric in the space of
    random variables, and is referred as the 'Root-Sum-Square Error' (RSSE). An
    important application is the method of least squares [3].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/L2-norm
        [2] https://en.wikipedia.org/wiki/Euclidean_distance
        [3] https://en.wikipedia.org/wiki/Least_squares

    """
    return vecnorm_l2(np.add(x, np.multiply(y, -1)), axis=axis)

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Generalized_mean
        [2] https://en.wikipedia.org/wiki/Risk_function
        [3] https://en.wikipedia.org/wiki/Mean_absolute_error
        [4] https://en.wikipedia.org/wiki/Root-mean-square_error

    """
    return vecnorm_mp(np.add(x, np.multiply(y, -1)), p=p, axis=axis)

def vecdist_mae(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Absolute Error of two arrays along given axis.

    The Mean Absolute Error is the metric, which is induced by the absolute
    mean [1] to a space of random variables. Thereby the absolute mean equals
    the l1-norm multiplied by the prefactor (1 / d), where d is the size of
    the underlying sample [2].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Mean_absolute_error
        [2] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return vecnorm_m1(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_rmse(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Root-Mean-Square Error of two arrays along given axis.

    The Root-Mean-Square Error (RMSE) is the metric, which is induced by the
    quadratic mean to a space of random variables [1, 2]. Thereby the quadritic
    mean equals the l2-norm multiplied by the prefactor sqrt(1 / n), where d is
    the size of the underlying sample [3]. Consequently for an unbiased
    estimator, the RMSE is the square root of the variance and thus the
    standard deviation.

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Root_mean_square
        [2] https://en.wikipedia.org/wiki/Root-mean-square_error
        [3] https://en.wikipedia.org/wiki/Generalized_mean

    """
    return vecnorm_m2(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_rss(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Residual Sum of Squares of two arrays along given axis.

    The Residual Sum of Squares (RSS) is the metric, which is induced by the
    dot product pseudo norm to a space of random variables [1, 2]. The RSS is
    used in regression analysis to quantify the unexplained variation of a
    model [3].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Dot_product
        [2] https://en.wikipedia.org/wiki/Residual_sum_of_squares
        [3] https://en.wikipedia.org/wiki/Explained_variation

    """
    return vecnorm_dot(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_mse(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Squared Error of two arrays along given axis.

    The Mean Squared Error (RSS) is the metric, which is induced by the Mean
    Square pseudo norm to a space of random variables [1, 2]. The Mean Squared
    Error is used in mathematical optimization and statistics as a risk
    function [3, 4].

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/Mean_square
        [2] https://en.wikipedia.org/wiki/Pseudonorm
        [3] https://en.wikipedia.org/wiki/Mean_squared_error
        [4] https://en.wikipedia.org/wiki/Risk_function

    """
    return vecnorm_ms(np.add(x, np.multiply(y, -1)), axis=axis)

def vecdist_bias(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate bias of two arrays along given axis.

    The Bias is the metric, which is induced by the Standard Deviation to a
    space of random variables [1, 2]. The Bias 'between' an observable and an
    estimator is used to evaluate the consistency of the estimator [3].
    Consequently unbiased estimators are termed consistent.

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
        Numpy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://stats.stackexchange.com/questions/269405
        [2] https://en.wikipedia.org/wiki/Sample_standard_deviation
        [3] https://en.wikipedia.org/wiki/Bias_of_an_estimator

    """
    return np.std(x, axis=axis)

#vecdist_manhattan = vecdist_l1
#vecdist_sad = vecdist_l1
#vecdist_taxicab = vecdist_l1
#vecdist_block = vecdist_l1
#vecdist_euclid = vecdist_l2
#vecdist_rmsd = vecdist_rmse # root-mean-square deviation (RMSD)
