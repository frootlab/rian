# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as e: raise ImportError(
    "nemoa.common.calculus requires numpy: https://scipy.org") from e

from typing import Union, Optional

ArrayLike = Union[numpy.ndarray, numpy.matrix, float, int]

#
# Sigmoid Functions
#

def sigmoid(x: ArrayLike, func: Optional[str] = None, **kwargs) -> ArrayLike:
    """Calculate sigmoid functions.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        func (string, optional): Name of sigmoid function
            If not given, the standard logistic function is used.

    Returns:
        Array-like structure which contains the evaluation of the sigmoid
        function to the given data.

    """

    if func is None: return logistic(x, **kwargs)
    if func == 'logistic': return logistic(x, **kwargs)
    if func == 'tanh': return tanh(x, **kwargs)
    if func == 'lecun': return lecun(x, **kwargs)
    if func == 'elliot': return elliot(x, **kwargs)
    if func == 'hill': return hill(x, **kwargs)
    if func == 'arctan': return arctan(x, **kwargs)

    raise ValueError(f"function {func} is not supported.")

def logistic(x: ArrayLike) -> ArrayLike:
    """Calculate standard logistic function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the standard
        logistic function to the given data.

    """

    return 1. / (1. + numpy.exp(-x))

def tanh(x: ArrayLike) -> ArrayLike:
    """Hyperbolic tangent function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the hyperbolic
        tangent function to the given data.

    """

    return numpy.tanh(x)

def lecun(x: ArrayLike) -> ArrayLike:
    """LeCun hyperbolic tangent function.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller, "Efficient BackProp" (1998)

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the LeCun
        hyperbolic tangent function to the given data.

    """

    return 1.7159 * numpy.tanh(0.6666 * x)

def elliot(x: ArrayLike) -> ArrayLike:
    """Elliot activation function.

    [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
        Artificial Neural Networks" (1993)

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the Elliot
        activation function to the given data.

    """

    return x / (1. + numpy.abs(x))

def hill(x: ArrayLike, n: float = 2.) -> ArrayLike:
    """Hill type activation function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        n (int, optional): Hill coefficient

    Returns:
        Array-like structure which contains the evaluation of the Hill type
        activation function to the given data.

    """

    if n == 2.: return x / numpy.sqrt(1. + x ** 2)
    return numpy.power(x ** n / 1. + x ** n, 1. / n)

def arctan(x: ArrayLike) -> ArrayLike:
    """Inverse tangent function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the inverse
        tangent function to the given data.

    """

    return numpy.arctan(x)

#
# Derivatives of Sigmoid Functions
#

def d_sigmoid(x: ArrayLike, func: Optional[str] = None) -> ArrayLike:
    """Derivative of sigmoid function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        func (string, optional): Name of derivative of sigmoid function
            If not given, the derivative of the standard logistic function is
            used.

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        a sigmnoid function to the given data.

    """

    if isinstance(func, type(None)): return d_logistic(x)
    if func == 'd_logistic': return d_logistic(x)
    if func == 'd_elliot': return d_elliot(x)
    if func == 'd_hill': return d_hill(x)
    if func == 'd_lecun': return d_lecun(x)
    if func == 'd_tanh': return d_tanh(x)
    if func == 'd_arctan': return d_arctan(x)

    raise ValueError(f"function {func} is not supported")

def d_logistic(x: ArrayLike) -> ArrayLike:
    """Derivative of the standard logistic function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the standard logistic function to the given data.

    """

    return ((1. / (1. + numpy.exp(-x))) * (1. - 1. / (1. + numpy.exp(-x))))

def d_elliot(x: ArrayLike) -> ArrayLike:
    """Derivative of the Elliot sigmoid function.

    [1] D.L. Elliott, David L. Elliott, "A better Activation Function for
        Artificial Neural Networks", (1993)

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the Elliot sigmoid function to the given data.

    """

    return 1. / (1. + numpy.abs(x)) ** 2

def d_hill(x: ArrayLike, n: float = 2.) -> ArrayLike:
    """Derivative of Hill type activation function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        n (int, optional): Hill coefficient

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the Hill type activation function to the given data.

    """

    if n == 2.: return 1. / numpy.power(1. + x^2, 3. / 2.)
    return numpy.power(1. + x ** n, -(1. + n) / n)

def d_lecun(x: ArrayLike) -> ArrayLike:
    """Derivative of LeCun hyperbolic tangent.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    [1] Y. LeCun, L. Bottou, G. B. Orr, K. Müller, "Efficient BackProp" (1998)

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative of
        the LeCun hyperbolic tangent to the given data.

    """

    return 1.14382 / numpy.cosh(0.6666 * x) ** 2


def d_tanh(x: ArrayLike) -> ArrayLike:
    """Derivative of hyperbolic tangent function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative
        of the hyperbolic tangent function to the given data.

    """

    return 1. - numpy.tanh(x) ** 2

def d_arctan(x: ArrayLike) -> ArrayLike:
    """Derivative of inverse tangent function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Returns:
        Array-like structure which contains the evaluation of the derivative
        of the inverse tangent function to the given data.

    """

    return 1. / (1. + x ** 2)

#
# Multistep Sigmoid Functions
#

def dialogistic(x: ArrayLike, scale: float = 1.,
    sigma: float = 10.) -> ArrayLike:
    """Calulate dialogistic function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        scale (float, optional): scale parameter, default is 1.
        sigma (float, optional): sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the dialogistic
        function to the given data.

    """

    sigma = max(sigma, .000001)

    return numpy.abs(x) * (logistic(sigma * (x + .5 * scale))
        + logistic(sigma * (x - .5 * scale)) - 1.) \
        / numpy.abs(logistic(1.5 * sigma * scale)
        + logistic(.5 * sigma * scale) - 1.)

def softstep(x: ArrayLike, scale: float = 1., sigma: float = 10.) -> ArrayLike:
    """Calulate softstep function.

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        scale (float, optional): scale parameter, default is 1.
        sigma (float, optional): sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the softstep
        function to the given data.

    """

    norm = numpy.tanh(scale)

    return numpy.tanh(dialogistic(x, scale = scale, sigma = sigma)) / norm

def multilogistic(x: ArrayLike, scale: float = 1.,
    sigma: float = 10.) -> ArrayLike:
    """Muliple logistic function.

    [1] https://math.stackexchange.com/questions/\
        2529531/multiple-soft-step-function

    Args:
        x (ArrayLike): Numerical data arranged in an array-like structure

    Kwargs:
        scale (float, optional): scale parameter, default is 1.
        sigma (float, optional): sharpness parameter, default is 10.

    Returns:
        Array-like structure which contains the evaluation of the multiple
        logistic function to the given data.

    """

    # the multilogistic function approximates the identity function
    # iff the scaling or the sharpness parameter goes to zero
    if scale == 0. or sigma == 0.: return x

    xs = x / scale
    xsf = numpy.floor(xs)
    r = 2. * (xs - xsf) - 1.
    m = 2. / logistic(sigma) - 1.

    return scale * (xsf + 1. / m * (logistic(sigma * r) - .5) + .5)
