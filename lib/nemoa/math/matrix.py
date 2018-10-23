# -*- coding: utf-8 -*-
"""Matrix Norms and Metrices."""

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

from nemoa.base import nfunc, nmodule
from nemoa.math import vector
from nemoa.types import Any, IntTuple, NpArray, NpArrayLike, StrList

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
    return nmodule.crop_functions(prefix=_NORM_PREFIX)

def norm(x: NpArrayLike, name: str = 'frobenius', **kwds: Any) -> NpArray:
    """Calculate norm of matrix.

    References:
        [1] https://en.wikipedia.org/wiki/magnitude_(mathematics)

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        name: Name of matrix norm. Accepted values are:
            'pq': pq-norm (induces: pq-distances)
                Remark: requires additional parameters 'p' and 'q'
            'frobenius': Frobenius norm (induces: Frobenius distance)
            Default: 'frobenius'
        **kwds: Parameters of the given norm / class of norms.
            The norm Parameters are documented within the respective 'norm'
            functions.

    Returns:
        NumPy ndarray of dimension <dim x> - 2.

    """
    # Check Type of 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "first argument 'x' is required to be array-like") from err

    # Check dimension of 'x'
    if x.ndim < 2:
        raise ValueError("'x' is required to have dimension > 1")

    # Get norm function
    fname = _NORM_PREFIX + name.lower()
    module = nmodule.get_instance(nmodule.get_curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"norm with name '{str(norm)}' is not known") from err

    # Evaluate norm function
    return func(x, **nfunc.get_kwds(func, default=kwds))

def norm_pq(x: NpArray,
        p: float = 2., q: float = 2., axes: IntTuple = (0, 1)) -> NpArray:
    """Calculate pq-norm of an array along given axes.

    The class of pq-norms generalizes the p-norms by a twice application in
    two dimensions [1]. Thereby a 'p-norm', which is parametrized by 'p', is
    applied to the columns of the matrix (more generally: the first axis index
    withon the parameter 'axes'). Afterwards a further 'p-norm', which is
    parametrized by 'q' is applied to the rows of the matrix (more generally:
    the second axis index within the parameter 'axes'). For the case that
    p = q = 2, the pq-norm is the Frobenius norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        p: Positive real number, which determines the first p-norm by the p-th
            root of the summed p-th powered absolute values. For p < 1, the
            function does not satisfy the triangle inequality and yields a
            quasi-norm [2]. For p >= 1 the p-norm is a norm.
            Default: 2.
        q: Positive real number, which determines the second p-norm by the q-th
            root of the summed q-th powered absolute values. For q < 1, the
            function does not satisfy the triangle inequality and yields a
            quasi-norm [2]. For q >= 1 the p-norm is a norm.
            Default: 2.
        axes: Axes along which the norm is calculated. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: (0, 1)

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/matrix_norm#L2,1_and_Lp,q_norms
        [2] https://en.wikipedia.org/wiki/quasinorm

    """
    # Check type of 'axes'
    if not isinstance(axes, tuple):
        raise TypeError(
            "argument 'axes' is required to be of type 'tuple'"
            f", not '{type(axes)}'")

    # Check value of 'axes'
    if len(axes) != 2:
        raise np.AxisError(
            f"exactly two axes are required but {len(axes)} were given")
    if axes[0] == axes[1]:
        raise np.AxisError(
            "first and second axis have to be different")

    # For special cases prefer specific implementations for faster calculation
    if p == q == 2.: # Use the Frobenius norm
        return norm_frobenius(x, axes=axes)
    if p == q: # Use the p-norm in two dimensions
        return vector.norm_p(x, p=p, axis=axes)

    # If the first axis id is smaller then the second, then the second one
    # has to be corrected by the collapsed dimension of the first sum
    if axes[0] < axes[1]:
        axisp, axisq = axes[0], axes[1] - 1
    else:
        axisp, axisq = axes[0], axes[1]

    psum = np.sum(np.power(np.abs(x), p), axis=axisp)
    qsum = np.sum(np.power(psum, q / p), axis=axisq)
    return np.power(qsum, 1. / q)

def norm_frobenius(x: NpArray, axes: IntTuple = (0, 1)) -> NpArray:
    """Calculate Frobenius norm of an array along given axes.

    The Frobenius norm is the Euclidean norm on the space of (m, n) matrices.
    It equals the pq-norm for p = q = 2 and thus is calculated by the entrywise
    root sum of squared values [1]. From this it follows, that the Frobenius is
    sub-multiplicative.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        axes: Axes along which the norm is calculated. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: (0, 1)

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/frobenius_norm

    """
    return vector.norm_euclid(x, axis=axes)

#
# Matrix Metrices
#

def metrices() -> StrList:
    """Get sorted list of matrix metrices.

    Returns:
        Sorted list of all matrix metrices, that are implemented within the
        module.

    """
    return nmodule.crop_functions(prefix=_DIST_PREFIX)

def distance(
        x: NpArrayLike, y: NpArrayLike, metric: str = 'frobenius',
        **kwds: Any) -> NpArray:
    """Calculate matrix distances of two arrays along given axis.

    A matrix distance function, also known as metric, is a function d(x, y),
    which quantifies the proximity of matrices in a vector space as non-negative
    real numbers. If the distance is zero, then the matrices are equivalent with
    respect to the distance function [1]. Distance functions are often used as
    error, loss or risk functions, to evaluate statistical estimations [2].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        metric: Name of the matrix distance function. Accepted values are:
            'frobenius': Frobenius distance (induced by Frobenius norm)
            Default: 'frobenius'
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
            "first argument 'x' is required to be array-like") from err
    try:
        y = np.array(y)
    except TypeError as err:
        raise TypeError(
            "second argument 'y' is required to be array-like") from err

    # Check shapes and dtypes of 'x' and 'y'
    if x.shape != y.shape:
        raise ValueError(
            "arrays 'x' and 'y' can not be broadcasted together")

    # Get distance function
    fname = _DIST_PREFIX + metric.lower()
    module = nmodule.get_instance(nmodule.get_curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'metric' has an invalid value '{str(metric)}'")

    # Evaluate distance function
    return func(x, y, **nfunc.get_kwds(func, default=kwds))

def dist_frobenius(x: NpArray, y: NpArray, axes: IntTuple = (0, 1)) -> NpArray:
    """Calculate Frobenius distances of two arrays along given axis.

    The Frobenius distance is induced by the Frobenius norm [1] and the natural
    distance in geometric interpretations.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        y: Any sequence that can be interpreted as a numpy ndarray with the same
            dimension, shape and datatypes as 'x'.
        axes: Axes along which the norm is calculated. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: (0, 1)

    Returns:
        NumPy ndarray of dimension dim *x* - 2.

    References:
        [1] https://en.wikipedia.org/wiki/frobenius_norm

    """
    return norm_frobenius(np.add(x, np.multiply(y, -1)), axes=axes)
