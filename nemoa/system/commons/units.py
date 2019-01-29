# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

from nemoa.math import curve

class UnitsBaseClass:
    """Base Class for Unit Layer.

    Unification of common unit layer functions and attributes.
    """

    params = {}
    source = {}
    target = {}

    def __init__(self, params = None):
        if params:
            self.params = params
            if not self.check(params): self.initialize()

    def expect(self, data, source):

        if source['class'] == 'sigmoid':
            return self.expect_from_sigmoid_layer(
                data, source, self.weights(source))
        elif source['class'] == 'gauss':
            return self.expect_from_gauss_layer(
                data, source, self.weights(source))

        return False

    def get_updates(self, data, model, source):

        return self.get_param_updates(data, model, self.weights(source))

    def get_delta(self, in_data, out_delta, source, target):

        return self.delta_from_bprop(in_data, out_delta,
            self.weights(source), self.weights(target))

    def get_samples_from_input(self, data, source):

        if source['class'] == 'sigmoid':
            return self.get_samples(
                self.expect_from_sigmoid_layer(
                data, source, self.weights(source)))
        elif source['class'] == 'gauss':
            return self.get_samples(
                self.expect_from_gauss_layer(
                data, source, self.weights(source)))

        return False

    def weights(self, source):

        if 'source' in self.source \
            and source['layer'] == self.source['source']:
            return self.source['W']
        elif 'target' in self.target \
            and source['layer'] == self.target['target']:
            return self.target['W'].T
        else: raise ValueError("""could not get links:
            layers '%s' and '%s' are not connected!"""
            % (source['layer'], self.params['layer']))

    def links(self, source):

        if 'source' in self.source \
            and source['layer'] == self.source['source']:
            return self.source
        elif 'target' in self.target \
            and source['layer'] == self.target['target']:
            return {'W': self.target['W'].T, 'A': self.target['A'].T}
        else: raise ValueError("""could not get links:
            layers '%s' and '%s' are not connected!"""
            % (source['name'], self.params['name']))

    def adjacency(self, source):

        if 'source' in self.source \
            and source['layer'] == self.source['source']:
            return self.source['A']
        elif 'target' in self.target \
            and source['layer'] == self.target['target']:
            return self.target['A'].T
        else: raise ValueError("""could not get links:
            layers '%s' and '%s' are not connected!"""
            % (source['layer'], self.params['layer']))

class Sigmoid(UnitsBaseClass):
    """Sigmoidal Unit Layer.

    Layer of units with sigmoidal activation function and bernoulli
    distributed sampling.

    """

    def initialize(self, data = None):
        """Initialize system parameters of sigmoid distributed units
        using data. """

        size = len(self.params['id'])
        shape = (1, size)
        self.params['bias'] = 0.5 * numpy.ones(shape)
        return True

    def update(self, updates):
        """Update parameter of sigmoid units. """

        if 'bias'in updates:
            self.params['bias'] += updates['bias']

        return True

    @staticmethod
    def remove(layer, select):
        """Delete selection (list of ids) of units from parameter arrays. """

        layer['bias'] = layer['bias'][0, [select]]

        return True

    @staticmethod
    def check(layer):

        return 'bias' in layer

    def energy(self, data):
        """Return system energy of sigmoidal units as numpy array."""

        bias = self.params['bias']

        return - data * bias

    def expect_from_sigmoid_layer(self, data, source, weights):
        """Return expected values of a sigmoid output layer
        calculated from a sigmoid input layer. """

        bias = self.params['bias']

        return curve.sigmoid(bias + numpy.dot(data, weights))

    def expect_from_gauss_layer(self, data, source, weights):
        """Return expected values of a sigmoid output layer
        calculated from a gaussian input layer. """

        bias = self.params['bias']
        sdev = numpy.sqrt(numpy.exp(source['lvar']))

        return curve.sigmoid(bias + numpy.dot(data / sdev, weights))

    def get_param_updates(self, data, model, weights):
        """Return parameter updates of a sigmoidal output layer
        calculated from real data and modeled data. """

        size = len(self.params['id'])

        return {'bias': numpy.mean(data[1] - model[1], axis = 0).reshape((1, size))}

    def get_updates_delta(self, delta):

        size = len(self.params['id'])

        return {'bias': - numpy.mean(delta, axis = 0).reshape((1, size))}

    def delta_from_bprop(self, data, delta, win, wout):
        """

        data: input data
        delta: error delta out
        win: weights in
        wout: weights out
        """

        value = numpy.dot(delta, wout)
        bias = self.params['bias']
        backdelta = value * curve.dlogistic(
            (bias + numpy.dot(data, win)))

        return backdelta

    @staticmethod
    def grad(x):
        """Return gradiant of standard logistic function. """

        numpy.seterr(over = 'ignore')

        return ((1. / (1. + numpy.exp(-x)))
            * (1. - 1. / (1. + numpy.exp(-x))))

    @staticmethod
    def get_values(data):
        """Return median of bernoulli distributed layer
        calculated from expected values. """

        return (data > 0.5).astype(float)

    @staticmethod
    def get_samples(data):
        """Return sample of bernoulli distributed layer
        calculated from expected value. """

        return (data > numpy.random.rand(
            data.shape[0], data.shape[1])).astype(float)

    def get(self, unit):

        id = self.params['id'].index(unit)
        cl = self.params['class']
        visible = self.params['visible']
        bias = self.params['bias'][0, id]

        return {'label': unit, 'id': id, 'class': cl,
            'visible': visible, 'bias': bias}

class Gauss(UnitsBaseClass):
    """Layer of Gaussian Linear Units (GLU).

    Artificial neural network units with linear activation function
    and gaussian sampling.

    """

    def initialize(self, data = None, sigma = 0.1):
        """Initialize parameters of gauss distributed units. """

        # get mean and standard deviation
        size = len(self.params['id'])
        if isinstance(data, numpy.ndarray):
            mean = numpy.mean(data, axis = 0).reshape(1, size)
            sdev = numpy.std(data, axis = 0).reshape(1, size)
        else:
            mean = numpy.zeros([1, size])
            sdev = numpy.ones([1, size])

        # initialise bias and log variance of units
        self.params['bias'] = mean
        self.params['lvar'] = numpy.log(sigma * sdev ** 2)

        return True

    def update(self, updates):
        """Update gaussian units parameters."""

        if 'bias' in updates:
            self.params['bias'] += updates['bias']
        if 'lvar' in updates:
            self.params['lvar'] += updates['lvar']

        return True

    def get_param_updates(self, data, model, weights):
        """Return parameter updates of a gaussian output layer
        calculated from real data and modeled data. """

        shape = (1, len(self.params['id']))
        var = numpy.exp(self.params['lvar'])
        bias = self.params['bias']

        updBias = numpy.mean(
            data[1] - model[1], axis = 0).reshape(shape) / var
        updLVarData = numpy.mean(
            0.5 * (data[1] - bias) ** 2 - data[1]
            * numpy.dot(data[0], weights), axis = 0)
        updLVarModel = numpy.mean(
            0.5 * (model[1] - bias) ** 2 - model[1]
            * numpy.dot(model[0], weights), axis = 0)
        updLVar = (updLVarData - updLVarModel).reshape(shape) / var

        return { 'bias': updBias, 'lvar': updLVar }

    def get_updates_delta(self, delta):
        # 2do: calculate update for lvar

        shape = (1, len(self.params['id']))
        bias = - numpy.mean(delta, axis = 0).reshape(shape)

        return { 'bias': bias }

    @staticmethod
    def remove(layer, select):
        """Delete selection (list of ids) of units from parameter arrays. """

        layer['bias'] = layer['bias'][0, [select]]
        layer['lvar'] = layer['lvar'][0, [select]]

        return True

    def expect_from_sigmoid_layer(self, data, source, weights):
        """Return expected values of a gaussian output layer
        calculated from a sigmoid input layer. """

        return self.params['bias'] + numpy.dot(data, weights)

    def expect_from_gauss_layer(self, data, source, weights):
        """Return expected values of a gaussian output layer
        calculated from a gaussian input layer. """

        bias = self.params['bias']
        sdev = numpy.sqrt(numpy.exp(source['lvar']))

        return bias + numpy.dot(data / sdev, weights)

    @staticmethod
    def grad(x):
        """Return gradient of activation function."""

        return 1.

    @staticmethod
    def check(layer):

        return 'bias' in layer and 'lvar' in layer

    def energy(self, data):

        bias = self.params['bias']
        var = numpy.exp(self.params['lvar'])
        energy = 0.5 * (data - bias) ** 2 / var

        return energy

    @staticmethod
    def get_values(data):
        """Return median of gauss distributed layer
        calculated from expected values."""

        return data

    def get_samples(self, data):
        """Return sample of gauss distributed layer
        calculated from expected values. """

        sigma = numpy.sqrt(numpy.exp(self.params['lvar']))
        return numpy.random.normal(data, sigma)

    def get(self, unit):

        id = self.params['id'].index(unit)

        cl = self.params['class']
        bias = self.params['bias'][0, id]
        lvar = self.params['lvar'][0, id]
        visible = self.params['visible']

        return {
            'label': unit, 'id': id, 'class': cl,
            'visible': visible, 'bias': bias, 'lvar': lvar }
