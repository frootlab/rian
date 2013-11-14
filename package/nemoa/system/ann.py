#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import nemoa.system.base


# common activation functions

def sigmoid(x):
    """Standard logistic function."""
    return 1.0 / (1.0 + numpy.exp(-x))

def tanh(x):
    """Standard hyperbolic tangens function."""
    return numpy.tanh(x)

def tanhEff(x):
    """Hyperbolic tangens function, proposed in paper:
    'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
    return 1.7159 * numpy.tanh(0.6666 * x)

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN)."""

    ####################################################################
    # Configuration
    ####################################################################

    def _configure(self, config = {}, network = None, dataset = None, update = False, **kwargs):
        """Configure RBM to network and dataset."""
        if not 'check' in self._config:
            self._config['check'] = {'config': False, 'network': False, 'dataset': False}

        self._setConfig(config)
        if not network == None:
            self._setNetwork(network, update)
        if not dataset == None:
            self._setDataset(dataset)
        return self._isConfigured()

    def _setConfig(self, config, *args, **kwargs):
        """Set configuration from dictionary."""
        nemoa.common.dictMerge(self._getSystemDefaultConfig(), self._config)
        nemoa.common.dictMerge(config, self._config)

        units = self._getUnitsFromConfig()
        if units:
            self.setUnits(units, update = False)
        links = self._getLinksFromConfig()
        if links:
            self.setLinks(links, update = False)

        self._config['check']['config'] = True
        return True

    def _setNetwork(self, network, update = False, *args, **kwargs):
        """Update units and links to network instance."""
        nemoa.log('info', 'get system units and links from network \'%s\'' % (network.getName()))
        nemoa.setLog(indent = '+1')

        if not nemoa.type.isNetwork(network):
            nemoa.log("error", "could not configure system: network instance is not valid!")
            nemoa.setLog(indent = '-1')
            return False

        self.setUnits(self._getUnitsFromNetwork(network), update = update)
        self.setLinks(self._getLinksFromNetwork(network), update = update)

        self._config['check']['network'] = True
        nemoa.setLog(indent = '-1')
        return True

    def _setDataset(self, dataset, *args, **kwargs):
        """check if dataset columns match with visible units."""

        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not configure system:
                dataset instance is not valid!""")
            return False

        # compare visible units labels with dataset columns
        if dataset.getColLabels() != self.getUnits(visible = True):
            nemoa.log('error', """
            could not configure system:
            visible units differ from dataset columns!""")
            return False

        self._config['check']['dataset'] = True
        return True

    def _isConfigured(self):
        """Return configuration state of ANN."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    def _checkParams(self, params):
        """Check if system parameter dictionary is valid."""
        return self._checkUnitParams(params) \
            and self._checkLinkParams(params)

    def _initParams(self, data = None):
        """Initialize system parameters using data."""
        return (self._initUnits(data) and self._initLinks(data))

    ####################################################################
    # System Links
    ####################################################################

    def _initLinks(self, data = None):
        """Initialize system parameteres of all links using data."""
        for links in self._params['links']:
            x = len(self._units[self._params['links'][links]['source']]['label'])
            y = len(self._units[self._params['links'][links]['target']]['label'])

            if data == None:
                self._params['links'][links]['A'] = numpy.ones([x, y], dtype = bool)
                self._params['links'][links]['W'] = numpy.zeros([x, y], dtype = float)
            else:
                # 2DO can be done much better!!!
                if 'init' in self._config \
                    and 'weightSigma' in self._config['init']:
                        sigma = (self._config['init']['weightSigma'] \
                            * numpy.std(data, axis = 0).reshape(1, x).T) + 0.0001
                else:
                    sigma = numpy.std(data, axis = 0).reshape(1, x).T + 0.0001
                self._params['links'][links]['W'] = (self._params['links'][links]['A']
                    * numpy.random.normal(numpy.zeros((x, y)), sigma))
        return True

    def _checkLinkParams(self, params):
        """Check if system parameter dictionary is valid respective to links."""
        if not isinstance(params, dict) \
            or not 'links' in params.keys() \
            or not isinstance(params['links'], dict):
            return False
        for id in params['links'].keys():
            if not isinstance(params['links'][id], dict):
                return False
            for attr in ['A', 'W', 'source', 'target']:
                if not attr in params['links'][id].keys():
                    return False
        return True

    def _indexLinks(self):
        self._links = {units: {'source': {}, 'target': {}} 
            for units in self._units.keys()}
        for id in self._params['links'].keys():
            source = self._params['links'][id]['source']
            target = self._params['links'][id]['target']
            self._links[source]['target'][target] = \
                self._params['links'][id]
            self._links[target]['source'][source] = \
                self._params['links'][id]
        return True

    def _getWeightsFromLayers(self, source, target):
        if self._config['optimize']['useAdjacency']:
            if target['name'] in self._links[source['name']]['target']:
                return self._links[source['name']]['target'][target['name']]['W'] \
                    * self._links[source['name']]['target'][target['name']]['A']
            elif source['name'] in self._links[target['name']]['target']:
                return (self._links[target['name']]['target'][source['name']]['W'] \
                    * self._links[source['name']]['target'][target['name']]['A']).T
        else:
            if target['name'] in self._links[source['name']]['target']:
                return self._links[source['name']]['target'][target['name']]['W']
            elif source['name'] in self._links[target['name']]['target']:
                return self._links[target['name']]['target'][source['name']]['W'].T

        nemoa.log('error', """Could not get links:
            Layer '%s' and layer '%s' are not connected.
            """ % (source['name'], target['name']))
        return None

    def _removeUnitsLinks(self, layer, select):
        """Remove links to a given list of units."""
        links = self._links[layer['name']]

        for src in links['source'].keys():
            links['source'][src]['A'] = \
                links['source'][src]['A'][:, select]
            links['source'][src]['W'] = \
                links['source'][src]['W'][:, select]
        for tgt in links['target'].keys():
            links['target'][tgt]['A'] = \
                links['target'][tgt]['A'][select, :]
            links['target'][tgt]['W'] = \
                links['target'][tgt]['W'][select, :]

        return True

    ####################################################################
    # Units
    ####################################################################

    def _initUnits(self, data = None):
        """Initialize system parameteres of all units using data."""
        for layerName in self._units.keys():
            layer = self._units[layerName]
            if 'init' in self._config \
                and layerName in self._config['init']['ignoreUnits']:
                continue
            elif layer['class'] == 'sigmoid':
                self.sigmoidUnits.initialize(layer, data)
            elif layer['class'] == 'gauss':
                if 'vSigma' in self._config['init']:
                    self.gaussUnits.initialize(layer, data,
                        vSigma = self._config['init']['vSigma'])
                else:
                    self.gaussUnits.initialize(layer, data)
            else:
                return False
        return True

    def _indexUnits(self):
        self._units = {}
        for id in range(len(self._params['units'])):
            self._units[self._params['units'][id]['name']] = \
                self._params['units'][id]
        return True

    def _checkUnitParams(self, params):
        """Check if system parameter dictionary is valid respective to units."""
        if not isinstance(params, dict) \
            or not 'units' in params.keys() \
            or not isinstance(params['units'], list):
            return False
        for id in range(len(params['units'])):
            layer = params['units'][id]
            if not isinstance(layer, dict):
                return False
            for attr in ['name', 'visible', 'class', 'label']:
                if not attr in layer.keys():
                    return False
            if layer['class'] == 'gauss' \
                and not self.gaussUnits.check(layer):
                return False
            elif params['units'][id]['class'] == 'sigmoid' \
                and not self.sigmoidUnits.check(layer):
                return False
        return True

    def _getUnitsFromSystem(self, group = False, **kwargs):
        """Return tuple with lists of unit labels ([units1], [units2], ...)."""
        filter = []
        for key in kwargs.keys():
            if key in self._params['units'][0].keys():
                filter.append((key, kwargs[key]))
        layers = ()
        for layer in self._params['units']:
            valid = True
            for key, val in filter:
                if not layer[key] == val:
                    valid = False
                    break
            if valid:
                layers += (layer['label'], )
        if group:
            return layers
        units = []
        for layer in layers:
            units += layer
        return units

    def _getLayerOfUnit(self, unit):
        for id in range(len(self._params['units'])):
            if unit in self._params['units'][id]['label']:
                return self._params['units'][id]['name']
        return None

    def _getUnitInformation(self, unit, layer = None):
        # search for layer if no layer is given
        if not layer:
            layer = self._getLayerOfUnit(unit)
        if not layer in self._units:
            return {}
        layer = self._units[layer]
        if not unit in layer['label']:
            return {}
        unitid = layer['label'].index(unit)
        if layer['class'] == 'gauss':
            info = self.gaussUnits.get(layer, unitid)
        elif layer['class'] == 'sigmoid':
            info = self.sigmoidUnits.get(layer, unitid)
        else:
            info = {}
        info['id'] = unitid
        info['class'] = layer['class']
        info['visible'] = layer['visible']
        return info

    def _removeUnits(self, layer = None, label = []):

        if not layer == None and not layer in self._units:
            nemoa.log('error', """
                could not remove units:
                unknown layer '%'""" % (layer))
            return False

        # search for labeled units in given layer
        layer = self._units[layer]
        select = []
        units = []
        for id, unit in enumerate(layer['label']):
            if not unit in label:
                select.append(id)
                units.append(unit)

        # remove units from unit labels
        layer['label'] = units

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            self.gaussUnits.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            self.sigmoidUnits.remove(layer, select)

        # delete units from link parameter arrays
        self._removeUnitsLinks(layer, select)

        return True

    def _getExpect(self, data, chain):
        """Return expected values of a layer
        calculated from a chain of mappings."""
        if len(chain) == 2:
            return self._getExpectSourceTarget(data,
                self._units[chain[0]], self._units[chain[1]])
        data = numpy.copy(data)
        for id in range(len(chain) - 1):
            data = self._getExpectSourceTarget(data,
                self._units[chain[id]], self._units[chain[id + 1]])
        return data

    def _getExpectSourceTarget(self, data, source, target):
        """Return expected unit values of a layer
        calculated from the expected valus of another layer."""
        weights = self._getWeightsFromLayers(source, target)
        if source['class'] == 'sigmoid' and target['class'] == 'sigmoid':
            return self.sigmoidUnits.expectFromSigmoidInput(data, source, target, weights)
        elif source['class'] == 'sigmoid' and target['class'] == 'gauss':
            return self.gaussUnits.expectFromSigmoidInput(data, source, target, weights)
        elif source['class'] == 'gauss' and target['class'] == 'sigmoid':
            return self.sigmoidUnits.expectFromGaussInput(data, source, target, weights)

    def _getSample(self, data, chain):
        """Return sampled unit values of a layer
        calculated from a chain of mappings."""
        if len(chain) == 1:
            return self._getUnitSample(data, self._units[chain[0]])
        elif len(chain) == 2:
            return self._getUnitSample(
                self._getExpectSourceTarget(data,
                    self._units[chain[0]], self._units[chain[1]]),
                    self._units[chain[1]])
        data = numpy.copy(data)
        for id in range(len(chain) - 1):
            data = self._getUnitSample(
                self._getExpectSourceTarget(data,
                    self._units[chain[id]], self._units[chain[id + 1]]),
                    self._units[chain[id + 1]])
        return data

    def _getSampleExpect(self, data, chain):
        """Return expected value
        for a chain mappings of sampled units values."""
        if len(chain) == 1:
            return data
        elif len(chain) == 2:
            return self._getExpectSourceTarget(
                self._getUnitSample(data, self._units[chain[0]]),
                self._units[chain[0]], self._units[chain[1]])
        return self._getExpectSourceTarget(
            self._getSample(data, chain[0:-1]),
            self._units[chain[-2]], self._units[chain[-1]])

    def _getValue(self, data, chain):
        """Return unit median values of a layer
        calculated from a chain of mappings."""
        if len(chain) == 1:
            return self._getUnitMedian(data, self._units[chain[0]])
        elif len(chain) == 2:
            return self._getUnitMedian(
                self._getExpectSourceTarget(data,
                    self._units[chain[0]], self._units[chain[1]]),
                    self._units[chain[1]])
        data = numpy.copy(data)
        for id in range(len(chain) - 1):
            data = self._getUnitMedian(
                self._getExpectSourceTarget(data,
                    self._units[chain[id]], self._units[chain[id + 1]]),
                    self._units[chain[id + 1]])
        return data

    def _getValueExpect(self, data, chain):
        """Return expected value
        for a chain of mappings of maximum likelihood units values."""
        if len(chain) == 1:
            return data
        elif len(chain) == 2:
            return self._getExpectSourceTarget(
                self._getUnitSample(data, self._units[chain[0]]),
                self._units[chain[0]], self._units[chain[1]])
        return self._getExpectSourceTarget(
            self._getValue(data, chain[0:-1]),
            self._units[chain[-2]], self._units[chain[-1]])

    def _getUnitMedian(self, data, layer):
        if layer['class'] == 'sigmoid':
            return self.sigmoidUnits.getValueFromExpect(data, layer)
        elif layer['class'] == 'gauss':
            return self.gaussUnits.getValueFromExpect(data, layer)

    def _getUnitSample(self, data, layer):
        if layer['class'] == 'sigmoid':
            return self.sigmoidUnits.getSampleFromExpect(data, layer)
        elif layer['class'] == 'gauss':
            return self.gaussUnits.getSampleFromExpect(data, layer)

    def _getUnitEnergy(self, data, chain):
        """Return unit energies of a layer
        calculated from a chain of mappings."""
        if len(chain) == 1:
            pass
        elif len(chain) == 2:
            data = self._getValue(data, chain)
        else:
            data = self._getValue(self._getExpect(data, chain[0:-1]), chain[-2:])
        layer = self._units[chain[-1]]
        if layer['class'] == 'sigmoid':
            return self.sigmoidUnits.energy(data, layer)
        elif layer['class'] == 'gauss':
            return self.gaussUnits.energy(data, layer)

    def _getUnitError(self, inputData, outputData, chain, block = [], **kwargs):
        """Return euclidean reconstruction error of units.
        error := ||outputData - modelOutput||
        """
        if block == []:
            modelOutput = self._getExpect(inputData, chain)
        else:
            inputDataCopy = numpy.copy(inputData)
            for i in block:
                inputDataCopy[:,i] = numpy.mean(inputDataCopy[:,i])
            modelOutput = self._getExpect(inputDataCopy, chain)
        return numpy.sqrt(((outputData - modelOutput) ** 2).sum(axis = 0))

    def _getUnitPerformance(self, inputData, outputData, chain, **kwargs):
        """Return unit performance respective to data.
        
        Description:
            performance := 1 - error / ||data||
        """
        error = self._getUnitError(inputData, outputData, chain, **kwargs)
        norm = numpy.sqrt((outputData ** 2).sum(axis = 0))
        return 1.0 - error / norm

    def _getPerformance(self, inputData, outputData, chain, **kwargs):
        """Return system performance respective to data."""
        return numpy.mean(self._getUnitPerformance(
            inputData, outputData, chain, **kwargs))

    class units(): pass

    class sigmoidUnits(units):
        """Units with sigmoidal activation and binary distribution."""

        @staticmethod
        def initialize(layer, data = None):
            """Initialize system parameters of sigmoid distributed units using data."""
            layer['bias'] = 0.5 * numpy.ones((1, len(layer['label'])))
            return True

        @staticmethod
        def update(layer, updates):
            """Update parameter of sigmoid units."""
            layer['bias'] += updates['bias']
            return True

        @staticmethod
        def overwrite(layer, params):
            """Merge parameters of sigmoid units."""
            for i, u in enumerate(params['label']):
                if u in layer['label']:
                    l = layer['label'].index(u)
                    layer['bias'][0, l] = params['bias'][0, i]
            return True

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays."""
            layer['bias'] = layer['bias'][0, [select]]
            return True

        @staticmethod
        def check(layer):
            return 'bias' in layer

        @staticmethod
        def energy(data, layer):
            """Return system energy of sigmoidal units as numpy array."""
            return -numpy.mean(data * layer['bias'], axis = 0)

        @staticmethod
        def expectFromSigmoidInput(data, source, target, weights):
            """Return expected values of a sigmoid output layer
            calculated from a sigmoid input layer."""
            return sigmoid(target['bias'] + numpy.dot(data, weights))

        @staticmethod
        def expectFromGaussInput(data, source, target, weights):
            """Return expected values of a sigmoid output layer
            calculated from a gaussian input layer."""
            return sigmoid(target['bias'] +
                numpy.dot(data / numpy.exp(source['lvar']), weights))

        @staticmethod
        def getValueFromExpect(data, layer):
            """Return median of bernoulli distributed layer
            calculated from expected values."""
            return (data > 0.5).astype(float)

        @staticmethod
        def getSampleFromExpect(data, layer):
            """Return sample of bernoulli distributed layer
            calculated from expected value."""
            return (data > numpy.random.rand(data.shape[0], data.shape[1])).astype(float)

        @staticmethod
        def get(layer, unitid):
            return {'bias': layer['bias'][0, unitid]}

    class gaussUnits(units):
        """Units with linear activation and gaussian distribution"""

        @staticmethod
        def initialize(layer, data = None, vSigma = 0.4):
            """Initialize system parameters of gauss distribued units using data."""
            size = len(layer['label'])
            if data == None:
                layer['bias'] = numpy.zeros([1, size])
                layer['lvar'] = numpy.zeros([1, size])
            else:
                layer['bias'] = \
                    numpy.mean(data, axis = 0).reshape(1, size)
                layer['lvar'] = \
                    numpy.log((vSigma * numpy.ones((1, size))) ** 2)
            return True

        @staticmethod
        def update(layer, updates):
            """Update Gauss units."""
            layer['bias'] += updates['bias']
            layer['lvar'] += updates['lvar']
            return True

        @staticmethod
        def overwrite(layer, params):
            """Merge parameters of gaussian units."""
            for i, u in enumerate(params['label']):
                if u in layer['label']:
                    l = layer['label'].index(u)
                    layer['bias'][0, l] = params['bias'][0, i]
                    layer['lvar'][0, l] = params['lvar'][0, i]
            return True

        @staticmethod
        def expectFromSigmoidInput(data, source, target, weights):
            """Return expected values of a gaussian output layer
            calculated from a sigmoid input layer."""
            return target['bias'] + numpy.dot(data, weights)

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays."""
            layer['bias'] = layer['bias'][0, [select]]
            layer['lvar'] = layer['lvar'][0, [select]]
            return True

        @staticmethod
        def check(layer):
            return 'bias' in layer and 'lvar' in layer

        @staticmethod
        def energy(data, layer):
            return -numpy.mean((data - layer['bias']) ** 2
                / numpy.exp(layer['lvar']), axis = 0) / 2

        @staticmethod
        def getValueFromExpect(data, layer):
            """Return median of gauss distributed layer
            calculated from expected values."""
            return data

        @staticmethod
        def getSampleFromExpect(data, layer):
            """Return sample of gauss distributed layer
            calculated from expected values."""
            return numpy.random.normal(data, numpy.sqrt(numpy.exp(layer['lvar'])))

        @staticmethod
        def get(layer, unitid):
            return {'bias': layer['bias'][0, unitid],
                'lvar': layer['lvar'][0, unitid]}
