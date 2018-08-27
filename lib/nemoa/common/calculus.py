# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import numpy
from typing import Union, Optional

ArrayLike = Union[numpy.ndarray, numpy.matrix, float, int]

#
# Sigmoid functions
#

def sigmoid(x: ArrayLike, func: Optional[str] = None) -> ArrayLike:
    """Calculate sigmoid function."""
    if isinstance(func, type(None)): return logistic(x)
    elif func == 'logistic': return logistic(x)
    elif func == 'tanh': return tanh(x)
    elif func == 'atan': return atan(x)
    elif func == 'tanh_lecun': return tanh_lecun(x)
    raise ValueError(f"sigmoid function {func} is not supported.")

def logistic(x: ArrayLike) -> ArrayLike:
    """Return standard logistic function."""
    return 1. / (1. + numpy.exp(-x))

def tanh(x: ArrayLike) -> ArrayLike:
    """Return standard hyperbolic tangens function."""
    return numpy.tanh(x)

def tanh_lecun(x: ArrayLike) -> ArrayLike:
    """Return hyperbolic tangens function, proposed in paper:
    'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
    return 1.7159 * numpy.tanh(0.6666 * x)

def atan(x: ArrayLike) -> ArrayLike:
    """Return trigonometric inverse tangent."""
    return numpy.arctan(x)

#
# Bell functions
#

def dsigmoid(x: ArrayLike, func: Optional[str] = None) -> ArrayLike:
    """Calculate derivative of sigmoid function."""
    if isinstance(func, type(None)): return dlogistic(x)
    elif func == 'dlogistic': return dlogistic(x)
    elif func == 'dtanh': return dtanh(x)
    elif func == 'datan': return datan(x)
    raise ValueError(f"bell function {func} is not supported.")

def dlogistic(x: ArrayLike) -> ArrayLike:
    """Return derivative of standard logistic function."""
    return ((1. / (1. + numpy.exp(-x))) * (1. - 1. / (1. + numpy.exp(-x))))

def dtanh(x: ArrayLike) -> ArrayLike:
    """Return derivative of hyperbolic tangent function."""
    return 1. - numpy.tanh(x) ** 2

def datan(x: ArrayLike) -> ArrayLike:
    """Return derivative of trigonometric inverse tangent function."""
    return 1. / (1 + x ** 2)

#
# Double sigmoid functions
#

def intensify(x: ArrayLike, factor: float = 10.,
    bound: float = 1.) -> ArrayLike:
    """Return intensify function."""
    factor = max(factor, 0.000001)
    return numpy.abs(x) * (logistic(factor * (x + 0.5 * bound))
        + logistic(factor * (x - 0.5 * bound)) - 1.) \
        / numpy.abs(logistic(1.5 * factor * bound)
        + logistic(0.5 * factor * bound) - 1.)

def softstep(x: ArrayLike, factor: float = 10.,
    bound: float = 1.) -> ArrayLike:
    """Return softstep function."""
    return numpy.tanh(intensify(x, factor = factor, bound = bound)) \
        / numpy.tanh(bound)
