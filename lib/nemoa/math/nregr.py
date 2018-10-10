# -*- coding: utf-8 -*-
"""Collection of Sample Statistics for Regression Analysis."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common import nfunc, nmodule
from nemoa.math import nvector
from nemoa.types import Any, NpAxis, NpArray, NpArrayLike, StrList

ERR_PREFIX = 'err_'
FIT_PREFIX = 'fit_'

#
# Discrepancy Functions for the evaluation of Regression Errors and Residuals
#

def errors() -> StrList:
    """Get sorted list of discrepancy functions.

    A 'discrepancy' is a sample statistic, that quantifies the difference of
    realized random variables [1]. In regression analysis discrepancy functions
    usually appear as deviations [2] and errors [3], which are to be minimized
    (locally or globally) by an underlying model. The traversal of the parameter
    space therefore requires, the class of discrepancy functions to be continous
    semi-metrices [4].

    Returns:
        Sorted list of all discrepany functions, that are implemented within
        the module.

    References:
        [1] https://en.wikipedia.org/wiki/discrepancy_function
        [2] https://en.wikipedia.org/wiki/deviation_(statistics)
        [3] https://en.wikipedia.org/wiki/errors_and_residuals
        [4] https://en.wikipedia.org/wiki/semimetrics

    """
    from nemoa.common import ndict

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = ERR_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of discrepancy functions
    i = len(ERR_PREFIX)
    return sorted([v['name'][i:] for v in d.values()])

def error(
        x: NpArrayLike, y: NpArrayLike, dfunc: str, **kwargs: Any) -> NpArray:
    """Calculate discrepancy of samples along given axis.

    A 'discrepancy' is a sample statistic, that quantifies the difference of
    realized random variables [1]. In regression analysis discrepancy functions
    usually appear as deviations [2] and errors [3], which are to be minimized
    (locally or globally) by an underlying model. The traversal of the parameter
    space therefore requires, the class of discrepancy functions to be continous
    semi-metrices.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        dfunc: Name of discrepancy function:
            'rss': Residual Sum of Squares
            'mse': Mean Squared Error
            'mae': Mean Absolute Error
            'rmse': Root-Mean-Squared Error
        **kwargs: Parameters of the given discrapancy function.
            The Parameters are documented within the respective 'err'
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

    # Get discrepancy function
    fname = ERR_PREFIX + dfunc.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'dfunc' has an invalid value '{str(dfunc)}'")

    # Evaluate distance function
    return func(x, y, **nfunc.kwargs(func, default=kwargs))

def err_rss(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Residual Sum of Squares of two samples along given axis.

    The Residual Sum of Squares (RSS), also known as the the Sum of squared
    errors (SSE), is a sample statistic on in the space of random variables [1],
    and induced by the Sum of Squares [2]. Since the Sum of Squares, which
    equals the square of the Euclidean norm, is non-convex, it does not satisfy
    the triangle inequality and therefore does not define a valid norm. Since
    the Sum of Squares however is positive definite and subhomogeneous, the
    induced RSS is a semi-metric within its domain, and therefore a valid
    measure of discrepancy [3]. The RSS is used in regression analysis to
    quantify the unexplained variation of a model [4].

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
        [1] https://en.wikipedia.org/wiki/residual_sum_of_squares
        [2] https://en.wikipedia.org/wiki/sum_of_squares
        [3] https://en.wikipedia.org/wiki/discrepancy_function
        [3] https://en.wikipedia.org/wiki/explained_variation

    """
    return np.sum(np.square(np.add(x, np.multiply(y, -1))), axis=axis)

def err_mse(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Squared Error of two samples along given axis.

    The Mean Squared Error (MSE) is a sample statistic on in the space of random
    variables [1] and induced by the Mean Square (MS) [2]. Since the MS, which
    equals the square of the Quadratic Mean, is non-convex, it does not satisfy
    the triangle inequality and therefore does not define a valid norm. Since
    the MS however is positive definite and subhomogeneous, the induced MSE is
    a semi metric within its domain, and therefore a valid measure of
    discrepancy [3]. The MSE is used in regression analysis as a risk function
    to quantify the quality of an estimator [4].

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
        [1] https://en.wikipedia.org/wiki/mean_squared_error
        [2] https://en.wikipedia.org/wiki/mean_square
        [3] https://en.wikipedia.org/wiki/discrepancy_function
        [4] https://en.wikipedia.org/wiki/risk_function

    """
    return np.mean(np.square(np.add(x, np.multiply(y, -1))), axis=axis)

def err_mae(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Absolute Error of two samples along given axis.

    The Mean Absolute Error (MAE) is a sample statistic on in the space of
    random variables [1], which is induced by the Arithmetic Mean of absolute
    values. This norm equals the 1-norm multiplied by the prefactor (1 / d),
    where d is the length of the sample [2]. Consequently the induced MAE
    is a valid metric within its domain, and therefore in particular a valid
    measure of discrepancy [3]. The MSE is used in regression analysis as a
    risk function to quantify the quality of an estimator [4].

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
        [3] https://en.wikipedia.org/wiki/discrepancy_function
        [4] https://en.wikipedia.org/wiki/risk_function

    """
    return nvector.dist_amean(x, y, axis=axis)

def err_rmse(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Root-Mean-Square Error of two samples along given axis.

    The Root-Mean-Square Error (RMSE) is a sample statistic on in the space of
    random variables [1], which is induced by the Quadratic Mean [2]. This norm
    equals the Euclidean norm multiplied by the prefactor sqrt(1 / d), where d
    is the length of the sample. Consequently the induced RMSE is a valid metric
    within its domain, and therefore in particular a valid measure of
    discrepancy [3]. The RMSE is used in regression analysis to quantify the
    quality of an estimator.

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
        [1] https://en.wikipedia.org/wiki/root-mean-square_error
        [2] https://en.wikipedia.org/wiki/power_mean
        [3] https://en.wikipedia.org/wiki/discrepancy_function

    """
    return nvector.dist_qmean(x, y, axis=axis)

# TODO: Add RSSE
# norm_euclid
# With respect to a given sample the induced metric, is a sample statistic and
# referred as the 'Root-Sum-Square Difference' (RSSD). An important
# application is the method of least squares [3].
# [3] https://en.wikipedia.org/wiki/least_squares


# TODO: Goodness of fit Measures
# https://en.wikipedia.org/wiki/Goodness_of_fit
