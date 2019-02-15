# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Curves.

This module provides implementations of different curves. These comprise::

    * Sigmoidal shaped curves
    * Bell shaped curves (e.g. derivatives of sigmoidal shaped functions)
    * Further "SoftStep" based curves

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any
import numpy as np
from flab.base import call, catalog
from flab.base.types import StrList
from nemoa.base import array
from nemoa.typing import NpArray, NpArrayLike

#
# Define Catalog Categories
#

@catalog.category
class Curve:
    name: str

@catalog.category
class Bell(Curve):
    pass

@catalog.category
class SoftStep(Curve):
    pass

@catalog.category
class Sigmoid(SoftStep):
    pass

#
# Sigmoidal shaped curves
#

def sigmoids() -> StrList:
    """Get sorted list of sigmoid functions.

    Returns:
        Sorted list of all sigmoid functions, that are implemented within the
        module.

    """
    return sorted(catalog.search(Sigmoid).get('name'))

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
    # Try to cast 'x' as array and get function from catalog
    x = array.cast(x)
    f = catalog.pick(Sigmoid, name=name)

    # Evaluate function
    return call.safe_call(f, x=x, **kwds)

@catalog.register(Sigmoid, name='logistic')
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

@catalog.register(Sigmoid, name='tanh')
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

@catalog.register(Sigmoid, name='lecun')
def tanh_lecun(x: NpArrayLike) -> NpArray:
    """Calculate normalized hyperbolic tangent function.

    The LeCun hyperbolic tangent [LECUN1998]_ is a reparametrized hyperbolic
    tangent function, which is used as an activation function for learning
    Artificial Neural Networks.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the LeCun
        hyperbolic tangent function to the given data.

    """
    return 1.7159 * np.tanh(np.multiply(0.6666, x))

@catalog.register(Sigmoid, name='elliot')
def elliot(x: NpArrayLike) -> NpArray:
    """Calculate Elliot activation function.

    Thi Elliot activation function [ELLIOT1993] is used as an activation
    function for learning Artificial Neural Networks.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the Elliot
        activation function to the given data.

    """
    return x / (1. + np.abs(x))

@catalog.register(Sigmoid, name='hill')
def hill(x: NpArrayLike, n: int = 2) -> NpArray:
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

@catalog.register(Sigmoid, name='arctan')
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
# Bell shaped functions
#

def bells() -> StrList:
    """Get sorted list of bell shaped functions.

    Returns:
        Sorted list of all bell shaped functions, that are implemented within
        the module.

    """
    return sorted(catalog.search(Bell).get('name'))

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
    # Try to cast 'x' as array and get function from catalog
    x = array.cast(x)
    f = catalog.pick(Bell, name=name)

    # Evaluate function
    return call.safe_call(f, x=x, **kwds)

@catalog.register(Bell, name='gauss')
def gauss(x: NpArrayLike, mu: float = 0., sigma: float = 1.) -> NpArray:
    """Calculate Gauss function.

    Gaussian functions are used in statistics to describe the probability
    density of normally distributed random variables and therfore allow to
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
    factor = 1. / (sigma * (np.sqrt(2 * np.pi)))
    exp = np.power(np.e, -0.5 * np.square(np.add(x, -mu) / sigma))

    return factor * exp

@catalog.register(Bell, name='d_logistic')
def dlogistic(x: NpArrayLike) -> NpArray:
    """Calculate total derivative of the standard logistic function.

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

@catalog.register(Bell, name='d_elliot')
def delliot(x: NpArrayLike) -> NpArray:
    """Calculate total derivative of the Elliot activation function.

    Thi Elliot activation function [ELLIOT1993] is used as an activation
    function for learning Artificial Neural Networks.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the Elliot sigmoid function to the given data.

    """
    return 1. / (np.abs(x) + 1.) ** 2

@catalog.register(Bell, name='d_hill')
def dhill(x: NpArrayLike, n: float = 2.) -> NpArray:
    """Calculate total derivative of a Hill function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.
        n: Hill coefficient

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the Hill type activation function to the given data.

    """
    return 1. / np.power(np.power(x, n) + 1., (n + 1.) / n)

@catalog.register(Bell, name='d_tanh_lecun')
def dtanh_lecun(x: NpArrayLike) -> NpArray:
    """Calculate total derivative of the LeCun hyperbolic tangent.

    The LeCun hyperbolic tangent [LECUN1998]_ is a reparametrized hyperbolic
    tangent function, which is used as an activation function for learning
    Artificial Neural Networks.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative of
        the LeCun hyperbolic tangent to the given data.

    """
    return 1.14382 / np.cosh(np.multiply(0.6666, x)) ** 2

@catalog.register(Bell, name='d_tanh')
def dtanh(x: NpArrayLike) -> NpArray:
    """Calculate total derivative of the hyperbolic tangent function.

    Args:
        x: Any sequence that can be interpreted as a numpy ndarray of arbitrary
            dimension. This includes nested lists, tuples, scalars and existing
            arrays.

    Returns:
        Numpy ndarray which contains the evaluation of the derivative
        of the hyperbolic tangent function to the given data.

    """
    return 1. - np.tanh(x) ** 2

@catalog.register(Bell, name='d_arctan')
def darctan(x: NpArrayLike) -> NpArray:
    """Calculate total derivative of the inverse tangent function.

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
# Further SoftStep functions, that are not Sigmoidal shaped
#

@catalog.register(SoftStep, name='dialogistic')
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

    a = logistic(sigma * np.add(x, -0.5 * scale))
    b = logistic(sigma * np.add(x, +0.5 * scale))
    m = np.abs(x) * (np.add(a, b) - 1.)

    c = logistic(sigma * 0.5 * scale)
    d = logistic(sigma * 1.5 * scale)
    n = np.abs(np.add(c, d) - 1.)

    return m / n

@catalog.register(SoftStep, name='softstep')
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

@catalog.register(SoftStep, name='multi_logistic')
def multi_logistic(
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
    # The multiple logistic function approximates the identity function
    # if the scaling or the sharpness parameter goes to zero
    if scale == 0. or sigma == 0.:
        return x

    y = np.multiply(x, 1 / scale)
    l = np.floor(y)
    r = 2. * (y - l) - 1.
    m = np.divide(2., logistic(sigma)) - 1.

    return scale * (l + (logistic(sigma * r) / m - .5) + .5)
