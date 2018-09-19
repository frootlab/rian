# -*- coding: utf-8 -*-
"""Collection of frequently used numpy ndarray functions."""

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
from nemoa.common.ntype import (
    StrList, StrPairDict, StrListPair, NpAxis, NpArray, NpArrayLike, OptFloat)

VECNORM_PREFIX = 'vecnorm_'

#
#  Array Conversion Functions
#

def fromdict(d: StrPairDict, labels: StrListPair, na: float = 0.) -> NpArray:
    """Convert dictionary to array.

    Args:
        d: Dictionary of format {(<row>, <col>): value, ...}, where:
            <row> is an element of the <row list> of the argument labels and
            <col> is an element of the <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...].
        na: Value to mask NA (Not Available) entries. Missing entries in the
            dictionary are replenished by the NA value in the array.

    Returns:
        Numpy ndarray of shape (n, m), where n equals the length of the
        <row list> of the argument labels and m equals the length of the
        <col list> of the argument labels.

    """
    # Declare and initialize return value
    array: NpArray = np.empty(shape=(len(labels[0]), len(labels[1])))

    # Get numpy ndarray
    setitem = getattr(array, 'itemset')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            setitem((i, j), d.get((row, col), na))

    return array

def asdict(
        x: NpArray, labels: StrListPair, na: OptFloat = None) -> StrPairDict:
    """Convert two dimensional array to dictionary of pairs.

    Args:
        x: Numpy ndarray of shape (n, m), where n equals the length of the
            <row list> of the argument labels and m equals the length of the
            <col list> of the argument labels.
        labels: Tuple of format (<row list>, <col list>), where:
            <row list> is a list of row labels ['row1', 'row2', ...] and
            <col list> is a list of column labels ['col1', 'col2', ...]
        na: Optional value to mask NA (Not Available) entries. For cells in the
            array, which have this value, no entry in the returned dictionary
            is created.

    Returns:
        Dictionary of format {(<row>, <col>): value, ...}, where:
        <row> is an element of the <row list> of the argument labels and
        <col> is an element of the <col list> of the argument labels.

    """
    # Check argument 'array'
    if not hasattr(x, 'item'):
        raise TypeError(
            "argument 'arr' is required to by of type 'ndarray'"
            f", not '{type(x)}'")

    # Declare and initialize return value
    d: StrPairDict = {}

    # Get dictionary with pairs as keys
    getitem = getattr(x, 'item')
    for i, row in enumerate(labels[0]):
        for j, col in enumerate(labels[1]):
            val = getitem(i, j)
            if na is None or val != na:
                d[(row, col)] = val

    return d

#
# Vector norms and distances
#

def vecnorm(x: NpArrayLike, norm: str, axis: NpAxis = 0) -> NpArray:
    """Calculate vector norm along given axis.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of vector norm. Accepted values are:
            'L1': l1-Norm / Sum of Errors
            'L2': l2-Norm / Root Sum of Squared Errors
            'MAX': Maximum-Norm
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors
            'SD': Standard Deviation
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors
            'SSE': Sum of Squared Errors / Residual Sum of Squares
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    # Declare return value
    array: NpArray

    fname = VECNORM_PREFIX + norm.lower()
    module = nmodule.inst(nmodule.curname())
    try:
        array = getattr(module, fname)(x, axis=axis)
    except AttributeError as err:
        raise ValueError(
            f"argument 'norm' has an invalid assignment '{str(norm)}'")

    return array

def vecnorms() -> StrList:
    """Get sorted list of implemented vector norms."""
    from nemoa.common import ndict

    # Declare and initialize return value
    norms: StrList = []

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = VECNORM_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    #
    i = len(VECNORM_PREFIX)
    norms = [v['name'][i:].upper() for v in d.values()]

    return sorted(norms)

def vecnorm_l1(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate l1-Norm along given axis.

    The l1-norm (aka 'Sum of Errors') ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sum(np.abs(x), axis=axis)

def vecnorm_max(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    r"""Calculate Maximum-norm along given axis.

    The Maximum-norm is the limit of the Lp-norms for p \rightarrow \infty.
    It turns out that this limit is equivalent to the following definition ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.amax(np.abs(x), axis=axis)

def vecnorm_me(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate ME-Norm along given axis.

    The Mean of Errors ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.mean(np.abs(x), axis=axis)

def vecnorm_sse(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate SSE-Norm along given axis.

    The Sum of Squared Errors (aka 'Residual Sum of Squares') ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sum(np.square(x), axis=axis)

def vecnorm_mse(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate MSE-Norm along given axis.

    The Mean of Squared Errors ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.mean(np.square(x), axis=axis)

def vecnorm_l2(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate L2-Norm along given axis.

    The L2-norm, aka the 'Root Sum of Squared Errors' (RSSE), ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sqrt(np.sum(np.square(x), axis=axis))

def vecnorm_rmse(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate RMSE-Norm along given axis.

    The 'Root Mean of Squared Errors' (RMSE) ...

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    """
    return np.sqrt(np.mean(np.square(x), axis=axis))

def vecnorm_sd(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate SD-Norm along given axis.

    The 'Standard Deviation' (SD) can be interpreted as a norm on the vector
    space of mean zero random variables in a similar way, that the standard
    Euclidian norm in a three-dimensional space. [1]

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
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

    """
    return np.std(x, axis=axis)

def vecnorm_sde(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate SDE-Norm along given axis.

    The 'Standard Deviation of Errors' (SDE) can be interpreted as a norm on the
    vector space of mean zero random variables) in a similar way that the
    standard Euclidian norm in a three-dimensional space. [1]

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    Todo:
        * This is not a norm

    References:
        [1] https://stats.stackexchange.com/questions/269405

    """
    return np.std(np.abs(x), axis=axis)

def vecnorm_sdse(x: NpArrayLike, axis: NpAxis = 0) -> NpArray:
    """Calculate SDSE-Norm (SDev of Squared Errors) along given axis.

    The standard deviation can be interpreted as a norm (on the vector space
    of mean zero random variables) in a similar way that the standard Euclidian
    norm in a three-dimensional space. [1]

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimensions. This includes nested lists, tuples, scalars and existing
            arrays.
        axis: Axis (or axes) along which the norm is calculated. Within a
            one-dimensional array the axis always has index 0. A two-dimensional
            array has two corresponding axes: The first running vertically
            downwards across rows (axis 0), and the second running horizontally
            across columns (axis 1). Default: 0

    Returns:
        Numpy ndarray of dimension <dim x> - <number of axes>.

    Todo:
        * This is not a norm

    References:
        [1] https://stats.stackexchange.com/questions/269405

    """
    return np.std(np.square(x), axis=axis)
