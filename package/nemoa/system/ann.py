#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import nemoa.system.base

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN)."""

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
        """Update units and links to dataset instance."""

        if not nemoa.type.isDataset(dataset):
            nemoa.log("error", "could not configure system: dataset instance is not valid!")
            return False
            dataset.getColLabels()
        if dataset.getColLabels() != self._params['units'][0]['label']:
            # 2DO!!
            # something went wrong
            print dataset.getColLabels()
            print self._params['units'][0]['label']
            print 'I\'m system/ann.py/_setDataset'
            print 'What\'s wrong with me?'
            quit()

        self._config['check']['dataset'] = True
        return True

    def _isConfigured(self):
        """Return configuration state of ANN."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    def _indexUnits(self):
        self._units = {}
        for id in range(len(self._params['units'])):
            self._units[self._params['units'][id]['name']] = \
                self._params['units'][id]
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

    def _getUnitInformation(self, unit, layer = None):
        # set first (input) layer if no layer is given
        if not layer:
            layer = self._params['units'][0]['name']
        if not layer in self._units:
            return {}
        layer = self._units[layer]
        if not unit in layer['label']:
            return {}
        unitid = layer['label'].index(unit)
        if layer['class'] == 'gauss':
            info = self._getGaussUnitInfo(layer, unitid)
        elif layer['class'] == 'bernoulli':
            info = self._getBernoulliUnitInfo(layer, unitid)
        else:
            info = {}
        info['id'] = unitid
        info['class'] = layer['class']
        info['visible'] = layer['visible']
        return info

    def _checkParams(self, params):
        """Check if system parameter dictionary is valid."""
        return self._checkUnitParams(params) \
            and self._checkLinkParams(params)

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
                and not self._checkGaussUnits(layer):
                return False
            elif params['units'][id]['class'] == 'bernoulli' \
                and not self._checkBernoulliUnits(layer):
                return False
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

    def _initUnits(self, data = None):
        """Initialize system parameteres of all units using data."""
        for layerName in self._units.keys():
            layer = self._units[layerName]
            if 'init' in self._config \
                and layerName in self._config['init']['ignoreUnits']:
                continue
            elif layer['class'] == 'bernoulli':
                self._initBernoulliUnits(layer, data)
            elif layer['class'] == 'gauss':
                self._initGaussUnits(layer, data)
            else:
                return False
        return True

    def _initParams(self, data = None):
        """Initialize system parameters using data."""
        return (self._initUnits(data) and self._initLinks(data))

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
                        sigma = (self._config['init']['weightSigma']
                            * numpy.std(data, axis = 0).reshape(1, x).T) + 0.0001
                else:
                    sigma = numpy.std(data, axis = 0).reshape(1, x).T + 0.0001
                self._params['links'][links]['W'] = (self._params['links'][links]['A']
                    * numpy.random.normal(numpy.zeros((x, y)), sigma))
        return True

    def _getTransposedLinks(self, id):
        return {
            'source': self._params['links'][id]['target'],
            'target': self._params['links'][id]['source'],
            'A': self._params['links'][id]['A'].T,
            'W': self._params['links'][id]['W'].T}

    def _removeUnits(self, layer, label = []):

        if not layer in self._units:
            nemoa.log('error', """
                could not delete units:
                unknown layer '%'""" % (layer))
            return False

        # search for labeled units in given layer
        layer = self._units[layer]
        links = self._links[layer['name']]
        select = []
        for id, unit in enumerate(layer['label']):
            if not unit in label:
                select.append(id)

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            self._removeGaussUnits(layer, select)
        elif layer['class'] == 'bernoulli':
            self._removeBernoulliUnits(layer, select)
        
        # delete units from link parameter arrays
        for src in links['source'].keys():
            links['source'][src]['A'] = \
                links['source'][src]['A'][select, :]
            links['source'][src]['W'] = \
                links['source'][src]['W'][select, :]
        for tgt in links['target'].keys():
            links['target'][tgt]['A'] = \
                links['target'][tgt]['A'][:, select]
            links['target'][tgt]['W'] = \
                links['target'][tgt]['W'][:, select]
        return True

    # Bernoulli Units

    def _initBernoulliUnits(self, layer, data = None):
        """Initialize system parameters of bernoulli distributed units using data."""
        layer['bias'] = 0.5 * numpy.ones((1, len(layer['label'])))
        return True

    def _checkBernoulliUnits(self, layer):
        return 'bias' in layer

    def _removeBernoulliUnits(self, layer, select):
        """Delete selection (list of ids) of units from parameter arrays."""
        layer['bias'] = layer['bias'][0, [select]]
        return True

    def _getBernoulliUnitInfo(self, layer, unitid):
        return {'bias': layer['bias'][0, unitid]}

    # Gauss Units

    def _initGaussUnits(self, layer, data = None, vSigma = 0.4):
        """Initialize system parameters of gauss distribued units using data."""
        size = len(layer['label'])
        if data == None:
            layer['bias'] = numpy.zeros([1, size])
            layer['lvar'] = numpy.zeros([1, size])
        else:
            if 'vSigma' in self._config['init']:
                vSigma = self._config['init']['vSigma']
            layer['bias'] = \
                numpy.mean(data, axis = 0).reshape(1, size)
            layer['lvar'] = \
                numpy.log((vSigma * numpy.ones((1, size))) ** 2)
        return True

    def _checkGaussUnits(self, layer):
        return 'bias' in layer and 'lvar' in layer

    def _removeGaussUnits(self, layer, select):
        """Delete selection (list of ids) of units from parameter arrays."""
        layer['bias'] = layer['bias'][0, [select]]
        layer['lvar'] = layer['lvar'][0, [select]]
        return True

    def _getGaussUnitInfo(self, layer, unitid):
        return {'bias': layer['bias'][0, unitid],
            'lvar': layer['lvar'][0, unitid]}

    # common activation functions

    @staticmethod
    def _sigmoid(x):
        """Standard logistic function"""
        return 1.0 / (1.0 + numpy.exp(-x))

    @staticmethod
    def _tanh(x):
        """Hyperbolic tangens"""
        return numpy.tanh(x)

    @staticmethod
    def _tanhEff(x):
        """Hyperbolic tangens proposed in paper 'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
        return 1.7159 * numpy.tanh(0.6666 * x)
