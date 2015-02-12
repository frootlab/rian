# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import numpy

def intensify(x, factor = 10., bound = 1.):
    """Return intensify function."""
    factor = max(factor, 0.000001)
    return numpy.abs(x) * (logistic(factor * (x + 0.5 * bound))
        + logistic(factor * (x - 0.5 * bound)) - 1.) \
        / numpy.abs(logistic(1.5 * factor * bound)
        + logistic(0.5 * factor * bound) - 1.)

def sigmoid(x):
    """Return standard logistic function."""
    return logistic(x)

def dsigmoid(x):
    """Return derivation of standard logistic function."""
    return dlogistic(x)

def logistic(x):
    """Return standard logistic function."""
    return 1. / (1. + numpy.exp(-x))

def dlogistic(x):
    """Return derivation of standard logistic function."""
    return ((1. / (1. + numpy.exp(-x)))
        * (1. - 1. / (1. + numpy.exp(-x))))

def tanh(x):
    """Return standard hyperbolic tangens function."""
    return numpy.tanh(x)

def dtanh(x):
    """Return derivation of standard hyperbolic tangens function."""
    return 1. - numpy.tanh(x) ** 2

def tanheff(x):
    """Return hyperbolic tangens function, proposed in paper:
    'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
    return 1.7159 * numpy.tanh(0.6666 * x)
