#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import nemoa.system.base

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN)."""

    ####################################################################
    # Configuration
    ####################################################################

    def _configure(self, config = {}, network = None, dataset = None, update = False, **kwargs):
        """Configure RBM to network and dataset."""
        if not 'check' in self._config:
            self._config['check'] = {'config': False, 'network': False, 'dataset': False}

        self._updateConfig(config)
        if not network == None:
            self._setNetwork(network, update)
        if not dataset == None:
            self._setDataset(dataset)
        return self._isConfigured()

    def _updateConfig(self, config, *args, **kwargs):
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

    def _updateUnitsAndLinks(self, *args, **kwargs):
        nemoa.log('info', 'update system units and links')
        self.setUnits(self._params['units'], update = True)
        self.setLinks(self._params['links'], update = True)
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

    def _initParams(self, dataset = None):
        """Initialize system parameters.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Initialize all unit and link parameters to dataset.
        """
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not initilize system parameters:
                invalid dataset instance given!""")
            return False
        return self._initUnits(dataset) \
            and self._initLinks(dataset)

    def getError(self, *args, **kwargs):
        """Return euclidean data reconstruction error of system."""
        return numpy.sum(self.getError(*args, **kwargs))

    def getPerformance(self, *args, **kwargs):
        """Return data reconstruction performance of system."""
        return numpy.mean(self.getUnitPerformance(*args, **kwargs))

    ####################################################################
    # Links
    ####################################################################

    def _initLinks(self, dataset = None):
        """Initialize link parameteres (weights).

        Keyword Arguments:
            dataset -- nemoa dataset instance OR None

        Description:
            If dataset is None, initialize weights matrices with zeros
            and all adjacency matrices with ones.
            if dataset is nemoa network instance,
            initialize weights with random values, that fit ....
        """
        if not(dataset == None) and \
            not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not initilize link parameters:
                invalid dataset argument given!""")
            return False

        for links in self._params['links']:
            source = self._params['links'][links]['source']
            target = self._params['links'][links]['target']
            A = self._params['links'][links]['A']
            x = len(self.units[source].params['label'])
            y = len(self.units[target].params['label'])
            alpha = self._config['init']['wSigma'] \
                if 'wSigma' in self._config['init'] else 1.0
            sigma = numpy.ones([x, 1], dtype = float) * alpha / x

            if dataset == None:
                random = numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.getColGroups():
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.getData(100000, rows = rows, cols = source)
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            elif dataset.getColLabels('*') \
                == self.units[source].params['label']:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.getData(100000, rows = rows, cols = '*')
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            else:
                random = numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random
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
            for units in self.units.keys()}
        for id in self._params['links'].keys():
            source = self._params['links'][id]['source']
            target = self._params['links'][id]['target']
            self._links[source]['target'][target] = \
                self._params['links'][id]
            self.units[source].target = \
                self._params['links'][id]
            self._links[target]['source'][source] = \
                self._params['links'][id]
            self.units[target].source = \
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

    def _initUnits(self, dataset = None):
        """Initialize unit parameteres.

        Keyword Arguments:
            dataset -- nemoa dataset instance OR None

        Description:
            Initialize all unit parameters.
        """
        if not(dataset == None) and \
            not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not initilize unit parameters:
                invalid dataset argument given!""")
            return False

        for layerName in self.units.keys():
            if dataset == None \
                or self.units[layerName].params['visible'] == False:
                data = None
            else:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                cols = layerName \
                    if layerName in dataset.getColGroups() else '*'
                data = dataset.getData(100000, rows = rows, cols = cols)

            self.units[layerName].initialize(data)
        return True

    def _setUnits(self, units):
        """Set unit labels of all layers."""
        if not isinstance(units, list):
            return False
        if len(units) < 2:
            return False
        self._params['units'] = units

        # get unit classes from system config
        visibleUnitsClass = self._config['params']['visibleClass']
        hiddenUnitsClass = self._config['params']['hiddenClass']
        for id in range(len(self._params['units'])):
            if self._params['units'][id]['visible'] == True:
                self._params['units'][id]['class'] \
                    = visibleUnitsClass
            else:
                self._params['units'][id]['class'] \
                    = hiddenUnitsClass

        # update 'units' dictionary
        self.units = {}
        for id in range(len(self._params['units'])):
            unitClass = self._params['units'][id]['class']
            name = self._params['units'][id]['name']
            if unitClass == 'sigmoid':
                self.units[name] = self.sigmoidUnits()
            elif unitClass == 'gauss':
                self.units[name] = self.gaussUnits()
            else:
                nemoa.log('error', """
                    could not create system:
                    unit class '%s' is not supported!
                    """ % (unitClass))
                return False
            self.units[name].params = self._params['units'][id]
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

    def _getUnitsFromNetwork(self, network):
        """Return tuple with lists of unit labels from network."""
        units = [{'name': layer, 'label':
            network.nodes(type = layer)}
            for layer in network.layers()]
        for group in units:
            group['visible'] = \
                network.node(group['label'][0])['params']['visible']
            group['id'] = \
                network.node(group['label'][0])['params']['type_id']
        return units

    def _getLayerOfUnit(self, unit):
        """Return name of layer of given unit."""
        for id in range(len(self._params['units'])):
            if unit in self._params['units'][id]['label']:
                return self._params['units'][id]['name']
        return None

    def _getUnitInformation(self, unit, layer = None):
        """Return dict information for a given unit."""
        if not layer:
            layer = self._getLayerOfUnit(unit)
        if not layer in self.units:
            return {}
        return self.units[layer].get(unit)

    def _removeUnits(self, layer = None, label = []):
        """Remove units from parameter space."""
        if not layer == None and not layer in self.units.keys():
            nemoa.log('error', """
                could not remove units:
                unknown layer '%'""" % (layer))
            return False

        # search for labeled units in given layer
        
        layer = self.units[layer].params
        select = []
        labels = []
        for id, unit in enumerate(layer['label']):
            if not unit in label:
                select.append(id)
                labels.append(unit)

        # remove units from unit labels
        layer['label'] = labels

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            self.gaussUnits.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            self.sigmoidUnits.remove(layer, select)

        # delete units from link parameter arrays
        self._removeUnitsLinks(layer, select)

        return True

    def _getMapping(self):
        return tuple([layer['name'] for layer in self._params['units']])

    def getUnitExpect(self, data, chain = None):
        """Return expected values of a layer
        calculated from a chain of mappings."""
        if chain == None:
            chain = self._getMapping()
        if len(chain) == 2:
            return self.units[chain[1]].expect(data,
                self.units[chain[0]].params)
        data = numpy.copy(data)
        for id in range(len(chain) - 1):
            data = self.units[chain[id + 1]].expect(data,
                self.units[chain[id]].params)
        return data

    def getUnitSamples(self, data, chain = None, expectLast = False):
        """Return sampled unit values calculated from a chain of mappings.
        
        Keyword Arguments:
            expectLast -- return expectation values of the units
                for the last step instead of sampled values"""

        if chain == None:
            chain = self._getMapping()
        if expectLast:
            if len(chain) == 1:
                return data
            elif len(chain) == 2:
                return  self.units[chain[1]].expect(
                    self.units[chain[0]].getSamples(data),
                    self.units[chain[0]].params)
            return self.units[chain[-1]].expect(
                self.getUnitSamples(data, chain[0:-1]),
                self.units[chain[-2]].params)
        else:
            if len(chain) == 1:
                return self.units[chain[0]].getSamples(data)
            elif len(chain) == 2:
                return self.units[chain[1]].getSamplesFromInput(
                    data, self.units[chain[0]])
            data = numpy.copy(data)
            for id in range(len(chain) - 1):
                data = self.units[chain[id + 1]].getSamplesFromInput(
                    data, self.units[chain[id]])
            return data

    def getUnitValues(self, data, chain = None, expectLast = False):
        """Return unit values calculated from a chain of mappings.
        
        Keyword Arguments:
            expectLast -- return expectation values of the units
                for the last step instead of maximum likelihood values"""

        if chain == None:
            chain = self._getMapping()
        if expectLast:
            if len(chain) == 1:
                return data
            elif len(chain) == 2:
                return self.units[chain[1]].expect(
                    self.units[chain[0]].getSamples(data),
                    self.units[chain[0]].params)
            return self.units[chain[-1]].expect(
                self.getUnitValues(data, chain[0:-1]),
                self.units[chain[-2]].params)
        else:
            if len(chain) == 1:
                return self.units[chain[0]].getValues(data)
            elif len(chain) == 2:
                return self.units[chain[1]].getValues(
                    self.units[chain[1]].expect(data,
                    self.units[chain[0]].params))
            data = numpy.copy(data)
            for id in range(len(chain) - 1):
                data = self.units[chain[id + 1]].getValues(
                    self.units[chain[id + 1]].expect(data,
                    self.units[chain[id]].params))
            return data

    def getUnitEnergy(self, data, chain = None):
        """Return unit energies of a layer
        calculated from a chain of mappings."""
        if len(chain) == 1:
            pass
        elif len(chain) == 2:
            data = self.getUnitValues(data, chain)
        else:
            data = self.getUnitValues(self.getUnitExpect(data, chain[0:-1]), chain[-2:])
        return self.units[chain[-1]].energy(data)

    def getUnitError(self, inputData, outputData, chain = None, block = [], **kwargs):
        """Return euclidean reconstruction error of units.
        error := ||outputData - modelOutput||
        """
        if chain == None:
            chain = self._getMapping()
        if block == []:
            modelOutput = self.getUnitExpect(inputData, chain)
        else:
            inputDataCopy = numpy.copy(inputData)
            for i in block:
                inputDataCopy[:,i] = numpy.mean(inputDataCopy[:,i])
            modelOutput = self.getUnitExpect(inputDataCopy, chain)
        return numpy.sqrt(((outputData - modelOutput) ** 2).sum(axis = 0))

    def getUnitPerformance(self, inputData, outputData, *args, **kwargs):
        """Return unit performance respective to data.
        
        Description:
            performance := 1 - error / ||data||
        """
        error = self.getUnitError(inputData, outputData, *args, **kwargs)
        norm = numpy.sqrt((outputData ** 2).sum(axis = 0))
        return 1.0 - error / norm

    class annUnits():
        """Class to unify common unit attributes."""

        params = {}
        source = {}
        target = {}

        def __init__(self):
            pass

        def expect(self, data, source):
            if source['class'] == 'sigmoid':
                return self.expectFromSigmoidInput(data, source,
                    self.getWeights(source))
            elif source['class'] == 'gauss':
                return self.expectFromGaussInput(data, source,
                    self.getWeights(source))

        def getSamplesFromInput(self, data, source):
            if source['class'] == 'sigmoid':
                return self.getSamples(self.expectFromSigmoidInput(
                    data, source, self.getWeights(source)))
            elif source['class'] == 'gauss':
                return self.getSamples(self.expectFromGaussInput(
                    data, source, self.getWeights(source)))

        def getWeights(self, source):
        
        # 2DO
                #if self._config['optimize']['useAdjacency']:
            #if target['name'] in self._links[source['name']]['target']:
                #return self._links[source['name']]['target'][target['name']]['W'] \
                    #* self._links[source['name']]['target'][target['name']]['A']
            #elif source['name'] in self._links[target['name']]['target']:
                #return (self._links[target['name']]['target'][source['name']]['W'] \
                    #* self._links[source['name']]['target'][target['name']]['A']).T

            if 'source' in self.source \
                and source['name'] == self.source['source']:
                return self.source['W']
            elif 'target' in self.target \
                and source['name'] == self.target['target']:
                return self.target['W'].T

            nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected.
                """ % (source['name'], self.params['name']))
            return None

    class sigmoidUnits(annUnits):
        """Units with sigmoidal activation function and binary distribution."""

        def initialize(self, data = None):
            """Initialize system parameters of sigmoid distributed units using data."""
            self.params['bias'] = 0.5 * numpy.ones((1, len(self.params['label'])))
            return True

        def update(self, updates):
            """Update parameter of sigmoid units."""
            self.params['bias'] += updates['bias']
            return True

        def overwrite(self, params):
            """Merge parameters of sigmoid units."""
            for i, u in enumerate(params['label']):
                if u in self.params['label']:
                    l = self.params['label'].index(u)
                    self.params['bias'][0, l] = params['bias'][0, i]
            return True

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays."""
            layer['bias'] = layer['bias'][0, [select]]
            return True

        @staticmethod
        def check(layer):
            return 'bias' in layer

        def energy(self, data):
            """Return system energy of sigmoidal units as numpy array."""
            return -numpy.mean(data * self.params['bias'], axis = 0)

        def expectFromSigmoidInput(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a sigmoid input layer."""
            return self.sigmoid(self.params['bias'] + numpy.dot(data, weights))

        def expectFromGaussInput(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a gaussian input layer."""
            return self.sigmoid(self.params['bias'] +
                numpy.dot(data / numpy.exp(source['lvar']), weights))

        def getValues(self, data):
            """Return median of bernoulli distributed layer
            calculated from expected values."""
            return (data > 0.5).astype(float)

        def getSamples(self, data):
            """Return sample of bernoulli distributed layer
            calculated from expected value."""
            return (data > numpy.random.rand(
                data.shape[0], data.shape[1])).astype(float)

        def get(self, unit):
            id = self.params['label'].index(unit)
            return {
                'label': unit, 'id': id, 'class': self.params['class'],
                'visible': self.params['visible'],
                'bias': self.params['bias'][0, id]}

        # common activation functions

        @staticmethod
        def sigmoid(x):
            """Standard logistic function."""
            return 1.0 / (1.0 + numpy.exp(-x))

        @staticmethod
        def tanh(x):
            """Standard hyperbolic tangens function."""
            return numpy.tanh(x)

        @staticmethod
        def tanhEff(x):
            """Hyperbolic tangens function, proposed in paper:
            'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
            return 1.7159 * numpy.tanh(0.6666 * x)

    class gaussUnits(annUnits):
        """Units with linear activation function and gaussian distribution"""

        def initialize(self, data = None, vSigma = 0.4):
            """Initialize system parameters of gauss distribued units using data."""
            size = len(self.params['label'])
            if data == None:
                self.params['bias'] = numpy.zeros([1, size])
                self.params['lvar'] = numpy.zeros([1, size])
            else:
                self.params['bias'] = \
                    numpy.mean(data, axis = 0).reshape(1, size)
                self.params['lvar'] = \
                    numpy.log((vSigma * numpy.ones((1, size))) ** 2)
            return True

        def update(self, updates):
            """Update Gauss units."""
            self.params['bias'] += updates['bias']
            self.params['lvar'] += updates['lvar']
            return True

        def overwrite(self, params):
            """Merge parameters of gaussian units."""
            for i, u in enumerate(params['label']):
                if u in self.params['label']:
                    l = self.params['label'].index(u)
                    self.params['bias'][0, l] = params['bias'][0, i]
                    self.params['lvar'][0, l] = params['lvar'][0, i]
            return True

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays."""
            layer['bias'] = layer['bias'][0, [select]]
            layer['lvar'] = layer['lvar'][0, [select]]
            return True

        def expectFromSigmoidInput(self, data, source, weights):
            """Return expected values of a gaussian output layer
            calculated from a sigmoid input layer."""
            return self.params['bias'] + numpy.dot(data, weights)

        @staticmethod
        def check(layer):
            return 'bias' in layer and 'lvar' in layer

        def energy(self, data):
            return -numpy.mean((data - self.params['bias']) ** 2
                / numpy.exp(self.params['lvar']), axis = 0) / 2

        def getValues(self, data):
            """Return median of gauss distributed layer
            calculated from expected values."""
            return data

        def getSamples(self, data):
            """Return sample of gauss distributed layer
            calculated from expected values."""
            return numpy.random.normal(
                data, numpy.sqrt(numpy.exp(self.params['lvar'])))

        def get(self, unit):
            id = self.params['label'].index(unit)
            return {
                'label': unit, 'id': id, 'class': self.params['class'],
                'visible': self.params['visible'],
                'bias': self.params['bias'][0, id],
                'lvar': self.params['bias'][0, id]}
