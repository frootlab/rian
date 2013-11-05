#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import nemoa.system.base

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN)."""

    def _linkUnits(self):
        self._units = {}
        for id in range(len(self._params['units'])):
            self._units[self._params['units'][id]['name']] = \
                self._params['units'][id]
        return True

    def _linkLinks(self):
        self._links = {units: {'source': [], 'target': []} 
            for units in self._units.keys()}
        for id in self._params['links'].keys():
            source = self._params['links'][id]['source']
            target = self._params['links'][id]['target']
            self._links[source]['target'].append(target)
            self._links[target]['source'].append(source)
        return True

    def _initUnits(self, data = None):
        """Initialize system parameteres of all units using data."""
        for type in self._units.keys():
            if 'init' in self._config \
                and type in self._config['init']['ignoreUnits']:
                continue
            elif self._units[type]['class'] == 'bernoulli':
                self._initBernoulliUnits(type, data)
            elif self._units[type]['class'] == 'gauss':
                self._initGaussUnits(type, data)
            else:
                return False
        return True

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

    #def _getUnitParams(self, type):
        #if self._units[type]['class'] == 'gauss':
            #return self._getGaussUnitParams(type)
        #elif self._units[type]['class'] == 'bernoulli':
            #return self._getBernoulliUnitParams(type)

    def _deleteUnits(self, type, label = []):
        if self._units[type]['class'] == 'gauss':
            return self._deleteGaussUnits(type, label)
        elif self._units[type]['class'] == 'bernoulli':
            return self._deleteBernoulliUnits(type, label)

    # Bernoulli Units

    def _initBernoulliUnits(self, type, data = None):
        """Initialize system parameters of bernoulli distributed units using data."""
        self._units[type]['bias'] = \
            0.5 * numpy.ones((1, len(self._units[type]['label'])))
        return True

    #def _getBernoulliUnitParams(self, type):
        #return {'bias': self._units[type]['bias']}

    def _deleteBernoulliUnits(self, type, label):
        select = []
        for unitID, unit in enumerate(self._units[type]['label']):
            if not unit in label:
                select.append(unitID)
        self._units[type]['bias'] = self._units[type]['bias'][select]

        # 2DO delete units from link matrices

            
        ## cleanup input layer

        ## get ids for units not to delete
        #selectUnitIDs = []
        #for unitID, unit in enumerate(self._units[type]['label']):
            #if not unit in label:
                #selectUnitIDs.append(unitID)
        
        #inputLayer['params']['label'] = inputLayer['label']
        #for param in inputLayer['params'].keys():
            #if param == 'label':
                #continue
            #inputLayer['params'][param] = \
                #inputLayer['params'][param][0, selectUnitIDs]
        #inputLayerLinks = self._params['links'][(0, 1)]
        #for param in inputLayerLinks['params'].keys():
            #if type(inputLayerLinks['params'][param]).__module__ == numpy.__name__:
                #inputLayerLinks['params'][param] = \
                    #inputLayerLinks['params'][param][selectUnitIDs, :]


    # Gauss Units

    def _initGaussUnits(self, type, data = None, vSigma = 0.4):
        """Initialize system parameters of gauss distribued units using data."""
        size = len(self._units[type]['label'])
        if data == None:
            self._units[type]['bias'] = numpy.zeros([1, size])
            self._units[type]['lvar'] = numpy.zeros([1, size])
        else:
            if 'vSigma' in self._config['init']:
                vSigma = self._config['init']['vSigma']
            self._units[type]['bias'] = \
                numpy.mean(data, axis = 0).reshape(1, size)
            self._units[type]['lvar'] = \
                numpy.log((vSigma * numpy.ones((1, size))) ** 2)
        return True

    #def _getGaussUnitParams(self, type):
        #return {
            #'bias': self._units[type]['bias'],
            #'lvar': self._units[type]['lvar']}

    def _deleteGaussUnits(self, type, label):
        select = []
        for unitID, unit in enumerate(self._units[type]['label']):
            if not unit in label:
                select.append(unitID)
        self._units[type]['bias'] = self._units[type]['bias'][select]
        self._units[type]['lvar'] = self._units[type]['lvar'][select]

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
