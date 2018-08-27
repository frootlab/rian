# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import numpy
from typing import Union

ArrayLike = Union[numpy.ndarray, numpy.matrix, float, int]

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

def sigmoid(x: ArrayLike) -> ArrayLike:
    """Return standard logistic function."""
    return logistic(x)

def dsigmoid(x: ArrayLike) -> ArrayLike:
    """Return derivative of standard logistic function."""
    return dlogistic(x)

def logistic(x: ArrayLike) -> ArrayLike:
    """Return standard logistic function."""
    return 1. / (1. + numpy.exp(-x))

def dlogistic(x: ArrayLike) -> ArrayLike:
    """Return derivative of standard logistic function."""
    return ((1. / (1. + numpy.exp(-x)))
        * (1. - 1. / (1. + numpy.exp(-x))))

def tanh(x: ArrayLike) -> ArrayLike:
    """Return standard hyperbolic tangens function."""
    return numpy.tanh(x)

def dtanh(x: ArrayLike) -> ArrayLike:
    """Return derivative of standard hyperbolic tangens function."""
    return 1. - numpy.tanh(x) ** 2

def tanh_lecun(x: ArrayLike) -> ArrayLike:
    """Return hyperbolic tangens function, proposed in paper:
    'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
    return 1.7159 * numpy.tanh(0.6666 * x)
