#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'

import numpy

def intensify(x, factor = 10.0, bound = 1.0):
    """Return intensify function."""
    return numpy.abs(x) * (sigmoid(factor * (x + 0.5 * bound))
        + sigmoid(factor * (x - 0.5 * bound)) - 1.0) \
        / numpy.abs(sigmoid(1.5 * factor * bound)
        + sigmoid(0.5 * factor * bound) - 1.0)

def sigmoid(x):
    """Return standard sigmoid function."""
    return logistic(x)

def Dsigmoid(x):
    """Return derivation of standard sigmoid function."""
    return Dlogistic(x)

def logistic(x):
    """Return standard logistic function."""
    return 1.0 / (1.0 + numpy.exp(-x))

def Dlogistic(x):
    """Return derivation of standard logistic function."""
    return ((1.0 / (1.0 + numpy.exp(-x)))
        * (1.0 - 1.0 / (1.0 + numpy.exp(-x))))

def tanh(x):
    """Return standard hyperbolic tangens function."""
    return numpy.tanh(x)

def Dtanh(x):
    """Return derivation of standard hyperbolic tangens function."""
    return 1.0 - numpy.tanh(x) ** 2

def tanhEff(x):
    """Return hyperbolic tangens function, proposed in paper:
    'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
    return 1.7159 * numpy.tanh(0.6666 * x)
