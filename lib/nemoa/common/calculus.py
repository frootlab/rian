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
# Sigmoid functions / Soft Step functions
#

def sigmoid(x: ArrayLike, func: Optional[str] = None) -> ArrayLike:
    """Calculate sigmoid functions."""

    if func is None: return logistic(x)
    if func == 'logistic': return logistic(x)
    if func == 'tanh': return tanh(x)
    if func == 'atan': return atan(x)
    if func == 'tanh_lecun': return tanh_lecun(x)

    raise ValueError(f"function {func} is not supported.")

def logistic(x: ArrayLike, approx: Optional[int] = None) -> ArrayLike:
    """Return standard logistic function."""

    if approx is None: return 1. / (1. + numpy.exp(-x))
    if approx == 1: return x / (1. + numpy.abs(x))
    if approx == 2: return x / numpy.sqrt(1. + x ** 2)

    raise ValueError(f"approximation flag '{str(approx)}' is not supported.")

def tanh(x: ArrayLike) -> ArrayLike:
    """Return standard hyperbolic tangent function."""

    return numpy.tanh(x)

def tanh_lecun(x: ArrayLike) -> ArrayLike:
    """Return hyperbolic tangent function.

    Hyperbolic tangent function, which has been proposed to be more efficient
    in learning Artificial Neural Networks [1].

    [1] "Efficient BackProp", LeCun, Bottou, Orr, Müller

    """

    return 1.7159 * numpy.tanh(0.6666 * x)

def atan(x: ArrayLike) -> ArrayLike:
    """Return trigonometric inverse tangent function."""

    return numpy.arctan(x)

#
# Multiple Soft Step Functions
#

def dialogistic(x: ArrayLike, scale: float = 1.,
    sigma: float = 10.) -> ArrayLike:
    """Calulate dialogistic function.

    Args:
        x (ArrayLike):

    Kwargs:
        scale (float): scaling parameter
        sigma (float): sharpness parameter

    """

    sigma = max(sigma, .000001)

    return numpy.abs(x) * (logistic(sigma * (x + .5 * scale))
        + logistic(sigma * (x - .5 * scale)) - 1.) \
        / numpy.abs(logistic(1.5 * sigma * scale)
        + logistic(.5 * sigma * scale) - 1.)

def softstep(x: ArrayLike, scale: float = 1., sigma: float = 10.) -> ArrayLike:
    """Calulate softstep function.

    Args:
        x (ArrayLike):

    Kwargs:
        scale (float): scaling parameter
        sigma (float): sharpness parameter

    """

    norm = numpy.tanh(scale)

    return numpy.tanh(dialogistic(x, scale = scale, sigma = sigma)) / norm

def multilogistic(x: ArrayLike, scale: float = 1.,
    sigma: float = 10.) -> ArrayLike:
    """Calulate muliple logistic function

    Args:
        x (ArrayLike):

    Kwargs:
        scale (float): scaling parameter
        sigma (float): sharpness parameter

    [1] https://math.stackexchange.com/questions/\
        2529531/multiple-soft-step-function

    """

    # the multilogistic function approximates the identity function, if ether
    # the scaling or the sharpness parameter goes to zero
    if scale == 0. or sigma == 0.: return x

    xs = x / scale
    xsf = numpy.floor(xs)
    r = 2. * (xs - xsf) - 1.
    m = 2. / logistic(sigma) - 1.
    f = scale * (xsf + 1. / m * (logistic(sigma * r) - .5) + .5)

    return f

#
# Bell Shaped Functions
#

def dsigmoid(x: ArrayLike, func: Optional[str] = None) -> ArrayLike:
    """Calculate derivative of sigmoid functions."""

    if isinstance(func, type(None)): return dlogistic(x)
    if func == 'dlogistic': return dlogistic(x)
    if func == 'dtanh': return dtanh(x)
    if func == 'datan': return datan(x)

    raise ValueError(f"function {func} is not supported.")

def dlogistic(x: ArrayLike) -> ArrayLike:
    """Return derivative of standard logistic function."""

    return ((1. / (1. + numpy.exp(-x))) * (1. - 1. / (1. + numpy.exp(-x))))

def dtanh(x: ArrayLike) -> ArrayLike:
    """Return derivative of hyperbolic tangent function."""

    return 1. - numpy.tanh(x) ** 2

def datan(x: ArrayLike) -> ArrayLike:
    """Return derivative of trigonometric inverse tangent function."""

    return 1. / (1 + x ** 2)
