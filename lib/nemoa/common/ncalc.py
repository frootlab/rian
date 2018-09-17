# -*- coding: utf-8 -*-
"""Collection of frequently used mathematical functions."""

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

from nemoa.common.ntype import Union, OptStr

ArrayLike = Union[np.ndarray, np.matrix, float, int]

# Sigmoid Functions

def sigmoid(x: ArrayLike, func: OptStr = None, **kwargs) -> ArrayLike:
    """Calculate sigmoid functions.

    Args:
        x: Numerical data arranged in an array-like structure
        func: Name of sigmoid function
            If not given, the standard logistic function is used.

    Returns:
        Array-like structure which contains the evaluation of the sigmoid
        function to the given data.

    """
    sigmoids = ['logistic', 'tanh', 'lecun', 'elliot', 'hill', 'arctan']

    if func is None:
        return getattr(sys.modules[__name__], sigmoids[0])(x, **kwargs)
    if func in sigmoids:
        return getattr(sys.modules[__name__], func)(x, **kwargs)

    raise ValueError(f"sigmoid function '{func}' is not supported")

def logistic(x: ArrayLike) -> ArrayLike:
    """Calculate standard logistic function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the standard
        logistic function to the given data.

    """
    return 1. / (1. + np.exp(-x))

def tanh(x: ArrayLike) -> ArrayLike:
    """Calculate hyperbolic tangent function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the hyperbolic
        tangent function to the given data.

    """
    return np.tanh(x)

def lecun(x: ArrayLike) -> ArrayLike:
    """Calculate normalized hyperbolic tangent function.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the LeCun
        hyperbolic tangent function to the given data.

    References:
        [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller,
            "Efficient BackProp" (1998)

    """
    return 1.7159 * np.tanh(0.6666 * x)

def elliot(x: ArrayLike) -> ArrayLike:
    """Calculate Elliot activation function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the Elliot
        activation function to the given data.

    References:
        [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
            Artificial Neural Networks" (1993)

    """
    return x / (1. + np.abs(x))

def hill(x: ArrayLike, n: float = 2.) -> ArrayLike:
    """Calculate Hill type activation function.

    Args:
        x: Numerical data arranged in an array-like structure
        n: Hill coefficient

    Returns:
        Array-like structure which contains the evaluation of the Hill type
        activation function to the given data.

    """
    if n == 2.:
        return x / np.sqrt(1. + x ** 2)
    return x / np.power(1. + x ** n, 1. / n)

def arctan(x: ArrayLike) -> ArrayLike:
    """Calculate inverse tangent function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the inverse
        tangent function to the given data.

    """
    return np.arctan(x)

# Derivatives of Sigmoid Functions

def d_sigmoid(x: ArrayLike, func: OptStr = None, **kwargs) -> ArrayLike:
    """Calculate derivative of sigmoid function.

    Args:
        x: Numerical data arranged in an array-like structure
        func: Name of derivative of sigmoid function
            If not given, the derivative of the standard logistic function is
            used.

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        a sigmnoid function to the given data.

    """
    d_sigmoids = [
        'd_logistic', 'd_tanh', 'd_lecun', 'd_elliot', 'd_hill', 'd_arctan']

    if func is None:
        return getattr(sys.modules[__name__], d_sigmoids[0])(x, **kwargs)
    if func in d_sigmoids:
        return getattr(sys.modules[__name__], func)(x, **kwargs)

    raise ValueError(
        f"derivative of sigmoid function '{func}' is not implemented")

def d_logistic(x: ArrayLike) -> ArrayLike:
    """Calculate derivative of the standard logistic function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the standard logistic function to the given data.

    """
    return (1. / (1. + np.exp(-x))) * (1. - 1. / (1. + np.exp(-x)))

def d_elliot(x: ArrayLike) -> ArrayLike:
    """Calculate derivative of the Elliot sigmoid function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the Elliot sigmoid function to the given data.

    References:
        [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
            Artificial Neural Networks", (1993)

    """
    return 1. / (1. + np.abs(x)) ** 2

def d_hill(x: ArrayLike, n: float = 2.) -> ArrayLike:
    """Calculate derivative of Hill type activation function.

    Args:
        x: Numerical data arranged in an array-like structure
        n: Hill coefficient

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the Hill type activation function to the given data.

    """
    if n == 2.:
        return 1. / np.power(1. + x ** 2, 3. / 2.)
    return 1. / np.power(1. + x ** n, (1. + n) / n)

def d_lecun(x: ArrayLike) -> ArrayLike:
    """Calculate derivative of LeCun hyperbolic tangent.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the LeCun hyperbolic tangent to the given data.

    References:
        [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller,
            "Efficient BackProp" (1998)

    """
    return 1.14382 / np.cosh(0.6666 * x) ** 2


def d_tanh(x: ArrayLike) -> ArrayLike:
    """Calculate derivative of hyperbolic tangent function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative
        of the hyperbolic tangent function to the given data.

    """
    return 1. - np.tanh(x) ** 2

def d_arctan(x: ArrayLike) -> ArrayLike:
    """Calculate derivative of inverse tangent function.

    Args:
        x: Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative
        of the inverse tangent function to the given data.

    """
    return 1. / (1. + x ** 2.)

# Multistep Sigmoid Functions

def dialogistic(
        x: ArrayLike, scale: float = 1., sigma: float = 10.) -> ArrayLike:
    """Calulate dialogistic function.

    Args:
        x: Numerical data arranged in an array-like structure
        scale: scale parameter, default is 1.
        sigma: sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the dialogistic
        function to the given data.

    """
    sigma = max(sigma, .000001)
    lle = logistic(sigma * (x - .5 * scale))
    lre = logistic(sigma * (x + .5 * scale))
    sle = logistic(.5 * sigma * scale)
    sre = logistic(1.5 * sigma * scale)

    return np.abs(x) * (lle + lre - 1.) / np.abs(sre + sle - 1.)

def softstep(x: ArrayLike, scale: float = 1., sigma: float = 10.) -> ArrayLike:
    """Calulate softstep function.

    Args:
        x: Numerical data arranged in an array-like structure
        scale: scale parameter, default is 1.
        sigma: sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the softstep
        function to the given data.

    """
    step = np.tanh(dialogistic(x, scale=scale, sigma=sigma))
    norm = np.tanh(scale)
    return step / norm

def multilogistic(
        x: ArrayLike, scale: float = 1., sigma: float = 10.) -> ArrayLike:
    """Calculate muliple logistic function.

    Args:
        x: Numerical data arranged in an array-like structure
        scale: scale parameter, default is 1.
        sigma: sharpness parameter, default is 10.

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

    fxs = x / scale
    ixs = np.floor(fxs)
    r = 2. * (fxs - ixs) - 1.
    m = 2. / logistic(sigma) - 1.

    return scale * (ixs + 1. / m * (logistic(sigma * r) - .5) + .5)
