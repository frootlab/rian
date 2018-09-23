# -*- coding: utf-8 -*-
"""Collection of Matrix Norms and Metrices."""

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
# Matrix Norms
#

def norms() -> StrList:
    """Get sorted list of matrix norms.

    Returns:
        Sorted list of all matrix norms, that are implemented within the module.

    """
    from nemoa.common import ndict

    # Get dictionary of functions with given prefix
    module = nmodule.inst(nmodule.curname())
    pattern = NORM_PREFIX + '*'
    d = nmodule.functions(module, pattern=pattern)

    # Create sorted list of norm names
    i = len(NORM_PREFIX)
    return sorted([v['name'][i:] for v in d.values()])

def volume(x: NpArrayLike, norm: str = 'euclid', **kwargs: Any) -> NpArray:
    """Calculate generalized volume of matrix by given norm.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        norm: Name of matrix norm. Accepted values are:

            Default: 'euclid'
        **kwargs: Parameters of the given norm / class of norms.
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
    return func(x, **nfunc.kwargs(func, default=kwargs))
