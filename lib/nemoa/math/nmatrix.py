# -*- coding: utf-8 -*-
"""Collection of Matrix Norms and Metrices."""

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

from nemoa.core import nfunc, nmodule
from nemoa.math import nvector
from nemoa.types import Any, IntTuple, NpArray, NpArrayLike, StrList

NORM_PREFIX = 'norm_'
DIST_PREFIX = 'dist_'

#
# Matrix Norms
#

def norms() -> StrList:
    """Get sorted list of matrix norms.

    Returns:
        Sorted list of all matrix norms, that are implemented within the module.

    """
    from nemoa.core import ndict

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = NORM_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(NORM_PREFIX)
    return sorted([v['name'][i:] for v in d.values()])

def magnitude(
        x: NpArrayLike, norm: str = 'frobenius', **kwds: Any) -> NpArray:
    """Calculate magnitude of matrix by given norm.

    References:
        [1] https://en.wikipedia.org/wiki/magnitude_(mathematics)

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of two or
            more dimensions. This includes nested lists, tuples, scalars and
            existing arrays.
        norm: Name of matrix norm. Accepted values are:
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
    # Check Type of Argument 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "argument 'x' is required to be of type 'NumPy ArrayLike'") from err

    # Check dimension of ndarray 'x'
    if getattr(x, 'ndim') < 2:
        raise ValueError(
            "NumPy Array 'x' is required to have dimension > 1") from err

    # Get norm function
    fname = NORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        func = getattr(module, fname)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid value '{str(norm)}'")

    # Evaluate norm function
    return func(x, **nfunc.kwds(func, default=kwds))

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
        axis: Axes along which the norm is calculated. A two-dimensional
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
    # Check argument 'axes'
    if not isinstance(axes, tuple):
        raise TypeError(
            "argument 'axes' is required to be of type 'tuple'"
            f", not '{type(axes)}'")
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
        return nvector.norm_p(x, p=p, axis=axes)

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
        axis: Axes along which the norm is calculated. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1).
            Default: (0, 1)

    Returns:
        NumPy ndarray of dimension <dim x> - <number of axes>.

    References:
        [1] https://en.wikipedia.org/wiki/frobenius_norm

    """
    return nvector.norm_euclid(x, axis=axes)
