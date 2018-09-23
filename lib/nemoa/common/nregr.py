# -*- coding: utf-8 -*-
"""Collection of Sample Statistics for Regression Analysis."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common import nfunc, nmodule, nvector
from nemoa.types import Any, NpAxis, NpArray, NpArrayLike, StrList

DIFF_PREFIX = 'diff_'

#
# Discrepancy Functions
#

def dfuncs() -> StrList:
    """Get sorted list of discrepancy functions.

    A 'discrepancy' is a sample statistic, that quantifies the difference of
    realized random variables [1]. In regression analysis discrepancy functions
    usually appear as deviations [2] and errors [3], which are to be minimized
    (locally or globally) by an underlying model. The traversal of the parameter
    space therefore requires, the class of discrepancy functions to be continous
    semi-metrices.

    Returns:
        Sorted list of all discrepany functions, that are implemented within
        the module.

    References:
        [1] https://en.wikipedia.org/wiki/discrepancy_function
        [2] https://en.wikipedia.org/wiki/deviation_(statistics)
        [3] https://en.wikipedia.org/wiki/errors_and_residuals

    """
    from nemoa.common import ndict

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = DIFF_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of discrepancy functions
    i = len(DIFF_PREFIX)
    return sorted([v['name'][i:] for v in d.values()])

def diff(
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
        dfunc: Name of discrepany function:
            'ssd': Sum of Square Difference (induced by Sum of Squares)
            'msd': Mean Square Difference (induced by Mean Square)
        **kwargs: Parameters of the given discrapancy function.
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

    # Get discrepancy function
    fname = DIFF_PREFIX + dfunc.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'dfunc' has an invalid value '{str(dfunc)}'")

    # Evaluate distance function
    return func(x, y, **nfunc.kwargs(func, default=kwargs))

def diff_ssd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
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
        [1] https://en.wikipedia.org/wiki/sum_of_squares
        [2] https://en.wikipedia.org/wiki/residual_sum_of_squares
        [3] https://en.wikipedia.org/wiki/explained_variation

    """
    return np.sum(np.square(np.add(x, np.multiply(y, -1))), axis=axis)

def diff_msd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
    """Calculate Mean Square Difference of two arrays along given axis.

    The 'Mean Squared Difference' (MSD) is a semi metric, which is induced by
    the 'Mean Square' (MS) [1]. The Mean Square in turn equals the square of the
    m2-Norm. Due to this nonlinear dependency the Mean Square does not satisfy
    the property of absolute homogeneity nor the triangle inequality and is
    therefore not a vector norm. Since the Mean Square however is positive
    definite and subhomogeneous, it induces a semi metric within its domain.

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
        [1] https://en.wikipedia.org/wiki/mean_square
        [2] https://en.wikipedia.org/wiki/mean_squared_error
        [3] https://en.wikipedia.org/wiki/risk_function

    """
    return np.mean(np.square(np.add(x, np.multiply(y, -1))), axis=axis)

def diff_rmsd(x: NpArray, y: NpArray, axis: NpAxis = 0) -> NpArray:
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
    return nvector.dist_qmean(x, y, axis=axis)
