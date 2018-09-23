# -*- coding: utf-8 -*-
"""Collection of curves like sigmoids and related functions."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import sys

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.types import Any, OptStr, NpArray, NpArrayLike

#
# Sigmoid Functions
#

def sigmoid(x: NpArrayLike, name: OptStr = None, **kwargs: Any) -> NpArray:
    """Calculate sigmoid functions.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        name: Name of sigmoid function. Default: 'logistic'

    Returns:
        Numpy ndarray which contains the evaluation of the sigmoid
        function to the given data.

    """
    funcs = ['logistic', 'tanh', 'lecun', 'elliot', 'hill', 'arctan']
    name = name or funcs[0]
    if name not in funcs:
        raise ValueError(f"sigmoid function '{name}' is not implemented")

    return getattr(sys.modules[__name__], name)(x, **kwargs)

def logistic(x: NpArrayLike) -> NpArray:
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

def tanh(x: NpArrayLike) -> NpArray:
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

def lecun(x: NpArrayLike) -> NpArray:
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

def elliot(x: NpArrayLike) -> NpArray:
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

def hill(x: NpArrayLike, n: float = 2.) -> NpArray:
    """Calculate Hill type activation function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        n: Hill coefficient

    Returns:
        Numpy ndarray which contains the evaluation of the Hill type
        activation function to the given data.

    """
    if n == 2.:
        return x / np.sqrt(1. + np.square(x))
    return x / np.power(1. + np.power(x, n), 1. / n)

def arctan(x: NpArrayLike) -> NpArray:
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
# Derivatives of Sigmoid Functions
#

def d_sigmoid(x: NpArrayLike, name: OptStr = None, **kwargs: Any) -> NpArray:
    """Calculate derivative of sigmoid function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        name: Name of derivative of sigmoid function. Default: 'd_logictic'

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        a sigmnoid function to the given data.

    """
    funcs = ['logistic', 'tanh', 'lecun', 'elliot', 'hill', 'arctan']
    name = name or funcs[0]
    if name not in funcs:
        raise ValueError(
            f"derivative of sigmoid function '{name}' is not implemented")

    return getattr(sys.modules[__name__], 'd_' + name)(x, **kwargs)

def d_logistic(x: NpArrayLike) -> NpArray:
    """Calculate derivative of the standard logistic function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the standard logistic function to the given data.

    """
    flog = logistic(x)
    return np.multiply(flog, -np.add(flog, -1.))

def d_elliot(x: NpArrayLike) -> NpArray:
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

def d_hill(x: NpArrayLike, n: float = 2.) -> NpArray:
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

def d_lecun(x: NpArrayLike) -> NpArray:
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


def d_tanh(x: NpArrayLike) -> NpArray:
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

def d_arctan(x: NpArrayLike) -> NpArray:
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
# Multiple Sigmoid Functions
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

    ma = logistic(sigma * np.add(x, -0.5 * scale))
    mb = logistic(sigma * np.add(x, +0.5 * scale))
    m = np.abs(x) * (np.add(ma, mb) - 1.)

    na = logistic(sigma * 0.5 * scale)
    nb = logistic(sigma * 1.5 * scale)
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
    m = np.divide(2., logistic(sigma)) - 1.

    return scale * (l + (logistic(sigma * r) / m - .5) + .5)
