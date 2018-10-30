# -*- coding: utf-8 -*-
"""Curves.

This module provides implementation of various curves, that appear in machine
learning and statistics. These comprise::

    * Sigmoidal shaped curves
    * Bell shaped curves (e.g. derivatives of sigmoidal shaped functions)
    * Multiple Step Functions

.. References:
.. _Gaussian functions:
    https://en.wikipedia.org/wiki/Gaussian_function
.. _normally distributed:
    https://en.wikipedia.org/wiki/Normal_distribution

"""

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

from nemoa.base import assess, this
from nemoa.types import Any, NpArray, NpArrayLike, StrList

_SIGM_PREFIX = 'sigm_'
_BELL_PREFIX = 'bell_'

#
# Sigmoidal shaped functions
#

def sigmoids() -> StrList:
    """Get sorted list of sigmoid functions.

    Returns:
        Sorted list of all sigmoid functions, that are implemented within the
        module.

    """
    return this.crop_functions(prefix=_SIGM_PREFIX)

def sigmoid(x: NpArrayLike, name: str = 'logistic', **kwds: Any) -> NpArray:
    """Evaluate sigmoidal shaped function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        name: Name of sigmoid function. Default: 'logistic'

    Returns:
        Numpy ndarray which contains the evaluation of the sigmoid
        function to the given data.

    """
    # Check type of 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "First argument 'x' is required to be array-like") from err

    # Get function
    func = this.get_attr(_SIGM_PREFIX + name.lower())
    if not callable(func):
        raise ValueError(f"name '{str(name)}' is not supported")

    # Evaluate function
    supp_kwds = assess.get_function_kwds(func, default=kwds)
    return func(x, **supp_kwds) # pylint: disable=E1102

def sigm_logistic(x: NpArrayLike) -> NpArray:
    """Calculate standard logistic function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the standard
        logistic function to the given data.

    """
    return 1. / (1. + np.exp(np.multiply(-1, x)))

def sigm_tanh(x: NpArrayLike) -> NpArray:
    """Calculate hyperbolic tangent function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the hyperbolic
        tangent function to the given data.

    """
    return np.tanh(x)

def sigm_lecun(x: NpArrayLike) -> NpArray:
    """Calculate normalized hyperbolic tangent function.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the LeCun
        hyperbolic tangent function to the given data.

    References:
        [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller,
            "Efficient BackProp" (1998)

    """
    return 1.7159 * np.tanh(np.multiply(0.6666, x))

def sigm_elliot(x: NpArrayLike) -> NpArray:
    """Calculate Elliot activation function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the Elliot
        activation function to the given data.

    References:
        [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
            Artificial Neural Networks" (1993)

    """
    return x / (1. + np.abs(x))

def sigm_hill(x: NpArrayLike, n: int = 2) -> NpArray:
    """Calculate Hill type activation function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        n: Even numbered Hill coefficient

    Returns:
        Numpy ndarray which contains the evaluation of the Hill type
        activation function to the given data.

    """
    if n == 2:
        return x / np.sqrt(1. + np.square(x))
    # Check if Hill coefficient is odd numbered
    if n & 0x1:
        raise ValueError(
            f"'n' is required to be an even number, not {n}")
    return x / np.power(1. + np.power(x, n), 1. / float(n))

def sigm_arctan(x: NpArrayLike) -> NpArray:
    """Calculate inverse tangent function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the inverse
        tangent function to the given data.

    """
    return np.arctan(x)

#
# Bell shaped functions
#

def bells() -> StrList:
    """Get sorted list of bell shaped functions.

    Returns:
        Sorted list of all bell shaped functions, that are implemented within
        the module.

    """
    return this.crop_functions(prefix=_BELL_PREFIX)

def bell(x: NpArrayLike, name: str = 'gauss', **kwds: Any) -> NpArray:
    """Evaluate bell shaped function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        name: Name of bell shaped function. By default the Gauss function is
            used.

    Returns:
        Evaluation of the bell shaped function at given data.

    """
    # Check type of 'x'
    try:
        x = np.array(x)
    except TypeError as err:
        raise TypeError(
            "First argument 'x' is required to be array-like") from err

    # Get function
    func = this.get_attr(_BELL_PREFIX + name.lower())
    if not callable(func):
        raise ValueError(f"name '{str(name)}' is not supported")

    # Evaluate function
    supp_kwds = assess.get_function_kwds(func, default=kwds)
    return func(x, **supp_kwds) # pylint: disable=E1102

def bell_gauss(x: NpArrayLike, mu: float = 0., sigma: float = 1.) -> NpArray:
    """Calculate Gauss function.

    ``Gaussian functions``_ are used in statisttics to describe the probability
    density of ``normally distributed``_ random variables  and therfore allow to
    model the error of quantities, that are expected to be the sum of many
    independent processes.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        mu: The real-valued location parameter *mu* determines the expectation
            value of the normally distributed random variable.
        sigma: The positive, real-valued scale parameter *sigma* determines the
            standard deviation of the normally distributed random variable.

    Returns:
        Numpy ndarray which contains the evaluation of the Gauss function to the
        given data.

    """
    pre_factor = 1. / (sigma * (np.sqrt(2 * np.pi)))
    exp_term = np.power(np.e, -0.5 * np.square(np.add(x, -mu) / sigma))
    return pre_factor * exp_term

def bell_d_logistic(x: NpArrayLike) -> NpArray:
    """Calculate derivative of the standard logistic function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the standard logistic function to the given data.

    """
    flog = sigm_logistic(x)
    return np.multiply(flog, -np.add(flog, -1.))

def bell_d_elliot(x: NpArrayLike) -> NpArray:
    """Calculate derivative of the Elliot sigmoid function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the Elliot sigmoid function to the given data.

    References:
        [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
            Artificial Neural Networks", (1993)

    """
    return 1. / (1. + np.abs(x)) ** 2

def bell_d_hill(x: NpArrayLike, n: float = 2.) -> NpArray:
    """Calculate derivative of Hill type activation function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        n: Hill coefficient

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the Hill type activation function to the given data.

    """
    return 1. / np.power(1. + np.power(x, n), (1. + n) / n)

def bell_d_lecun(x: NpArrayLike) -> NpArray:
    """Calculate derivative of LeCun hyperbolic tangent.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the LeCun hyperbolic tangent to the given data.

    References:
        [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller,
            "Efficient BackProp" (1998)

    """
    return 1.14382 / np.cosh(np.multiply(0.6666, x)) ** 2

def bell_d_tanh(x: NpArrayLike) -> NpArray:
    """Calculate derivative of hyperbolic tangent function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative
        of the hyperbolic tangent function to the given data.

    """
    return 1. - np.tanh(x) ** 2

def bell_d_arctan(x: NpArrayLike) -> NpArray:
    """Calculate derivative of inverse tangent function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative
        of the inverse tangent function to the given data.

    """
    return 1. / (1. + np.square(x))

#
# Multiple Sigmoidal Functions
#

def dialogistic(
        x: NpArrayLike, scale: float = 1., sigma: float = 10.) -> NpArray:
    """Calulate dialogistic function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        scale: Scale parameter. Default: 1.
        sigma: Sharpness parameter. Default: 10.

    Returns:
        Numpy ndarray which contains the evaluation of the dialogistic
        function to the given data.

    """
    sigma = max(sigma, .000001)

    ma = sigm_logistic(sigma * np.add(x, -0.5 * scale))
    mb = sigm_logistic(sigma * np.add(x, +0.5 * scale))
    m = np.abs(x) * (np.add(ma, mb) - 1.)

    na = sigm_logistic(sigma * 0.5 * scale)
    nb = sigm_logistic(sigma * 1.5 * scale)
    n = np.abs(np.add(na, nb) - 1.)

    return m / n

def softstep(x: NpArrayLike, scale: float = 1., sigma: float = 10.) -> NpArray:
    """Calulate softstep function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        scale: Scale parameter, default is 1.
        sigma: Sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the softstep
        function to the given data.

    """
    step = np.tanh(dialogistic(x, scale=scale, sigma=sigma))
    norm = np.tanh(scale)

    return step / norm

def multilogistic(
        x: NpArrayLike, scale: float = 1., sigma: float = 10.) -> NpArray:
    """Calculate muliple logistic function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        scale: Scale parameter. Default: 1.
        sigma: Sharpness parameter. Default: 10.

    Returns:
        Array-like structure which contains the evaluation of the multiple
        logistic function to the given data.

    References:
        [1] https://math.stackexchange.com/questions/2529531/

    """
    # the multilogistic function approximates the identity function
    # iff the scaling or the sharpness parameter goes to zero
    if scale == 0. or sigma == 0.:
        return x

    y = np.multiply(x, 1 / scale)
    l = np.floor(y)
    r = 2. * (y - l) - 1.
    m = np.divide(2., sigm_logistic(sigma)) - 1.

    return scale * (l + (sigm_logistic(sigma * r) / m - .5) + .5)
