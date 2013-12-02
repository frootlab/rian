#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# This python module contains a generic class for layered artificial   #
# neuronal networks aimed to provide common attributes and subclasses  #
# to special subtypes of artificial neuronal networks                  #
########################################################################

import nemoa.system.base, numpy

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN).

    Description:
        Artificial Neuronal Networks are graphical models.

    Reference:
    """

    def _configure(self, config = {}, network = None, dataset = None, update = False, **kwargs):
        """Configure RBM to network and dataset."""
        if not 'check' in self._config:
            self._config['check'] = {'config': False, 'network': False, 'dataset': False}

        self.setConfig(config)
        if not network == None:
            self._setNetwork(network, update)
        if not dataset == None:
            self._setDataset(dataset)
        return self._isConfigured()

    def _updateUnitsAndLinks(self, *args, **kwargs):
        nemoa.log('info', 'update system units and links')
        self.setUnits(self._params['units'], initialize = False)
        self.setLinks(self._params['links'], initialize = False)
        return True

    def _setNetwork(self, network, update = False, *args, **kwargs):
        """Update units and links to network instance."""
        nemoa.log('info', 'get system units and links from network \'%s\'' % (network.getName()))
        nemoa.setLog(indent = '+1')

        if not nemoa.type.isNetwork(network):
            nemoa.log("error", "could not configure system: network instance is not valid!")
            nemoa.setLog(indent = '-1')
            return False

        self.setUnits(self._getUnitsFromNetwork(network), initialize = (update == False))
        self.setLinks(self._getLinksFromNetwork(network), initialize = (update == False))

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

    #
    # 2DO: implement GRprop!!
    #

    def _optimizeRprop(self, dataset, schedule):
        nemoa.log('info', 'starting resiliant backpropagation (Rprop)')
        nemoa.setLog(indent = '+1')

        # get training data
        layers = self._getMapping()
        inLayer = layers[0]
        outLayer = layers[-1]
        data = dataset.getData(cols = (inLayer, outLayer))

        # init inspector with training data as test data
        if self._config['optimize']['inspect']:
            inspector = nemoa.system.base.inspector(self)
            inspector.setTestData(data)


        # update parameters
        for epoch in xrange(self._config['optimize']['updates']):

            print self.getPerformance(data)

            # 1. Forward pass (compute estimated values, from given output)

            out = {}
            for id, layer in enumerate(layers):
                if id == 0:
                    out[layer] = data[0]
                    continue
                out[layer] = self.getUnitExpect(
                    out[layers[id - 1]], layers[id - 1:id + 1])

            # 2. Backward pass (backpropagate deltas, from given output)

            delta = {}
            for id in range(len(layers) - 1)[::-1]:
                src = layers[id]
                tgt = layers[id + 1]
                if id == len(layers) - 2:
                    delta[(src, tgt)] = out[tgt] - data[1]
                    continue
                inData = self.units[tgt].params['bias'] \
                    + numpy.dot(out[src], self._params['links'][(id, id + 1)]['W'])
                DinData = ((1.0 / (1.0 + numpy.exp(-inData)))
                    * (1.0 - 1.0 / (1.0 + numpy.exp(-inData))))
                delta[(src, tgt)] = numpy.dot(delta[(tgt, layers[id + 2])],
                    self._params['links'][(id + 1, id + 2)]['W'].T) * DinData

            # 3. Compute updates

            updates = {}
            for id, layer in enumerate(layers[:-1]):
                src = layer
                tgt = layers[id + 1]
                updates[(src, tgt)] = {}
                updates[(src, tgt)]['W'] = -1.0 \
                    * numpy.dot(out[src].T, delta[src, tgt]) \
                    / out[src].size

            # 4. update parameters
            
            for id, layer in enumerate(layers[:-1]):
                src = layer
                tgt = layers[id + 1]
                self._params['links'][(id, id + 1)]['W'] += \
                    updates[(src, tgt)]['W']





            #quit() 
            continue



        # initialize update rates
        acceleration = (0.5, 1.0, 1.2)
        initialUpdateRate = 0.001
        minFactor = 0.00001
        maxFactor = 50.0
        unitUpdates = {}
        unitUpdateRates = {}
        linkUpdates = {}
        linkUpdateRates = {}


        quit()
        
            #values
            
            ## get values for real data and model data
            #lData = (
                #self.getUnitValues(data[0], mapping = layers[:inID + 1]),
                #self.getUnitValues(data[1], mapping = layers[inID + 1:][::-1]))
            #lModel = (lData[0],
                #self.getUnitValues(lData[0], mapping = layers[inID:(inID + 2)]))

        

        
        # 3. compute updates



        #
        # crap!
        #

        quit()

        # init inspector with first step
        for inID, lName in enumerate(layers[1:]):
            
            # get values for real data and model data
            lData = (
                self.getUnitValues(data[0], mapping = layers[:inID + 1]),
                self.getUnitValues(data[1], mapping = layers[inID + 1:][::-1]))
            lModel = (lData[0],
                self.getUnitValues(lData[0], mapping = layers[inID:(inID + 2)]))

            # calulate updates for unit layer
            unitUpdates[lName] = \
                self.units[lName].getUpdates(data = lData, model = lModel,
                source = self.units[layers[inID]].params)
            unitUpdateRates[lName] = \
                self.units[lName].multiply(
                    self.units[lName].one(unitUpdates[lName]), initialUpdateRate)

            # calculate updates for link layer
            linkUpdates[(inID, inID + 1)] = \
                self.annLinks().getUpdates(data = lData, model = lModel)
            linkUpdateRates[(inID, inID + 1)] = \
                self.annLinks().multiply(
                    self.annLinks().one(linkUpdates[(inID, inID + 1)]), initialUpdateRate)

        inspector.writeToStore(
            units = unitUpdates, unitRates = unitUpdateRates,
            links = linkUpdates, linkRates = linkUpdateRates)

        #print self.getPerformance(data)
        #print inspector.readFromStore()
        #quit()

        # update parameters
        for epoch in xrange(self._config['optimize']['updates']):

            print self.getPerformance(data)

            # obtain previous / initial updates and update rates
            prevUpdates = inspector.readFromStore()
            prevUnitUpdates = prevUpdates['units']
            prevUnitRates = prevUpdates['unitRates']
            prevLinkUpdates = prevUpdates['links']
            prevLinkRates = prevUpdates['linkRates']

            # obtain direction and magnitude for updates (gradient descent)
            unitUpdates = {}
            unitUpdateRates = {}
            linkUpdates = {}
            linkUpdateRates = {}

            for inID, lName in enumerate(layers[1:]):

                # get values for real data and model data
                lData = (
                    self.getUnitValues(data[0], mapping = layers[:inID + 1]),
                    self.getUnitValues(data[1], mapping = layers[inID + 1:][::-1]))
                lModel = (lData[0],
                    self.getUnitValues(lData[0], mapping = layers[inID:(inID + 2)]))

                # calulate updates for unit layer
                unitUpdates[lName] = \
                    self.units[lName].getUpdates(data = lData, model = lModel,
                    source = self.units[layers[inID]].params)
                unitUpdateRates[lName] = \
                    self.units[lName].multiply(
                    self.units[lName].minmax(
                    self.units[lName].multiply(prevUnitRates[lName],
                    self.units[lName].sign(self.units[lName].multiply(
                    prevUnitUpdates[lName], unitUpdates[lName]), acceleration)), minFactor, maxFactor),
                    self.units[lName].sign(unitUpdates[lName]))

                # calculate updates for link layer
                linkUpdates[(inID, inID + 1)] = \
                    self.annLinks().getUpdates(data = lData, model = lModel)
                linkUpdateRates[(inID, inID + 1)] = \
                    self.annLinks().multiply(
                    self.annLinks().minmax(
                    self.annLinks().multiply(prevLinkRates[(inID, inID + 1)],
                    self.annLinks().sign(self.annLinks().multiply(
                    prevLinkUpdates[(inID, inID + 1)], linkUpdates[(inID, inID + 1)]),
                    acceleration)), minFactor, maxFactor),
                    self.annLinks().sign(linkUpdates[(inID, inID + 1)]))

                #prv = prevLinkUpdates[(inID, inID + 1)]
                #cur = linkUpdates[(inID, inID + 1)]
                #chd = {key: numpy.sign(prv[key] * cur[key]) for key in cur.keys()}
                #(decFactor * (numpy.sign(dict[key]) < 0.0)
                #+ 0.0 * (numpy.sign(dict[key]) == 0.0)
                #+ remap[2] * (numpy.sign(dict[key]) > 0.0)
                
                #linkUpdateRates[(inID, inID + 1)] = \
                    #self.annLinks().multiply(
                    #self.annLinks().minmax(
                    #self.annLinks().multiply(prevLinkRates[(inID, inID + 1)],
                    #self.annLinks().sign(
                        #{key: prv[key] * cur[key] for key in cur.keys()},
                    #(decFactor, 0.0, incFactor))), minFactor, maxFactor),
                    #{key: numpy.sign(linkUpdates[(inID, inID + 1)][key]) for key in linkUpdates[(inID, inID + 1)].keys()}
                    #)
                
                #print '%.6f' % (linkUpdateRates[(inID, inID + 1)]['W'].mean())

            inspector.writeToStore(
                units = unitUpdates,
                unitRates = unitUpdateRates,
                links = linkUpdates,
                linkRates = linkUpdateRates)

            # update parameters
            for inID, lName in enumerate(layers[1:]):
                self._params['links'][(inID, inID + 1)]['W'] += \
                    linkUpdateRates[(inID, inID + 1)]['W']
                #self.units[lName].update(unitUpdateRates[lName])

            #
            # 2DO!
            # Do not use derived function for assuming update rates!!!!
            # This could (and will) lead to diverging objective functions
            # see paper about GRprop
            #

            # set updates
            for inID, lName in enumerate(layers[1:]):

                #updateRate = 0.1

                #weightRate = 1.0
                #biasRate = 0.01
                #lvarRate = 0.0

                #layerInRate = 0.1
                #layerOutRate = 1.0

                ##self.units[lName].update(unitUpdates[lName])
                self._params['links'][(inID, inID + 1)]['W'] += \
                    linkUpdateRates[(inID, inID + 1)]['W']
                
                #self._params['links'][(inID, inID + 1)]['W'] += \
                    #self._config['optimize']['updateRate'] \
                    #* linkUpdates[(inID, inID + 1)]['W'] * updateRate * weightRate * layerInRate

            ##
            ## output unit layer
            ##

            #updates2 = self.units['anchor'].getUpdates(data = lData, model = lModel, source = self.units['h'].params)
            
            ##
            ##
            ##

            #updateRate = 0.1

            #weightRate = 1.0
            #biasRate = 0.01
            #lvarRate = 0.0

            #layerInRate = 0.1
            #layerOutRate = 1.0

            #self._params['links'][(0,1)]['W'] += \
                #self._config['optimize']['updateRate'] \
                #* updates01['W'] * updateRate * weightRate * layerInRate

            #self._params['links'][(1,2)]['W'] += \
                #self._config['optimize']['updateRate'] \
                #* updates12['W'] * updateRate * weightRate * layerOutRate

            #updates2['lvar'] = updateRate * lvarRate * layerOutRate * updates2['lvar']
            #updates2['bias'] = updateRate * biasRate * layerOutRate * updates2['bias']
            ##print updates2

            #self.units['anchor'].update(updates2)

            inspector.trigger()
            
            #if inspector.difference() < 0:
            #    nemoa.log('warning', """
            #        aborting optimization:
            #        diverging weights and objective function!""")
            #    break

        #quit()

        #################################################################
        ## test to optimize input link layer (tf -> hidden)
        ## -> looks good
        #################################################################

        #lDataIn = data[0]
        #lDataOut = self.getUnitValues(data[1], mapping = ('anchor', 'h'))
        #lData = (lDataIn, lDataOut)

        #for epoch in xrange(self._config['optimize']['updates']):
        
            ## update params, starting from last layer to first layer
            #lModelOut = self.getUnitValues(lDataIn, mapping = ('tf', 'h'))
            #lModel = (lDataIn, lModelOut)
            
            #updates = self.annLinks().getUpdates(data = lData, model = lModel)
            
            #self._params['links'][(0,1)]['W'] += \
                #self._config['optimize']['updateRate'] * updates['W']

            #inspector.trigger()
        
        #quit()

        #################################################################
        ## test to optimize hidden layer
        ## -> fails # why?
        #################################################################

        #lDataIn = data[0]
        #lDataOut = self.getUnitValues(data[1], mapping = ('anchor', 'h'))
        #lData = (lDataIn, lDataOut)

        #for epoch in xrange(self._config['optimize']['updates']):
        
            ## update params, starting from last layer to first layer
            #lModelOut = self.getUnitValues(lDataIn, mapping = ('tf', 'h'))
            #lModel = (lDataIn, lModelOut)

            #updates = self.units['h'].getUpdates(data = lData, model = lModel, source = self.units['tf'].params)
            #self.units['h'].update(updates)

            ## monitoring of optimization process
            #inspector.trigger()

        #inspector.reset()

        #################################################################
        ## test to optimize output unit layer (anchor)
        ## -> looks good!
        #################################################################
        
        #lDataIn = self.getUnitValues(data[0], mapping = ('tf', 'h'))

        #for epoch in xrange(self._config['optimize']['updates']):
        
            ## update params, starting from last layer to first layer
            #lModelOut = self.getUnitValues(lDataIn, mapping = ('h', 'anchor'))
            #lData = (lDataIn, data[1])
            #lModel = (lDataIn, lModelOut)

            #updates = self.units['anchor'].getUpdates(data = lData, model = lModel, source = self.units['h'].params)
            #self.units['anchor'].update(updates)

            ## monitoring of optimization process
            #inspector.trigger()

        #################################################################
        ## test to optimize output link layer (hidden -> anchor)
        ## -> looks good
        #################################################################

        #lDataIn = self.getUnitValues(data[0], mapping = ('tf', 'h'))

        #for epoch in xrange(self._config['optimize']['updates']):
        
            ## update params, starting from last layer to first layer
            #lModelOut = self.getUnitValues(lDataIn, mapping = ('h', 'anchor'))
            #lData = (lDataIn, data[1])
            #lModel = (lDataIn, lModelOut)
            
            #updates = self.annLinks().getUpdates(data = lData, model = lModel)
            
            #self._params['links'][(1,2)]['W'] += \
                #self._config['optimize']['updateRate'] * updates['W']

            #inspector.trigger()

        nemoa.setLog(indent = '-1')
        return True

    def _getDataEval(self, data, func = 'performance', **kwargs):
        """Return scalar value for system evaluation."""
        if func == 'energy':
            return self._getDataEvalEnergy(data, **kwargs)
        if func == 'performance':
            return self.getPerformance(data, **kwargs)
        if func == 'error':
            return self.getError(data, **kwargs)
        return False

    def getError(self, data, *args, **kwargs):
        """Return data reconstruction error of system."""
        return 0.5 * numpy.sum(self.getUnitError(data, *args, **kwargs) ** 2)

    def getPerformance(self, data, *args, **kwargs):
        """Return data reconstruction performance of system."""
        return numpy.mean(self.getUnitPerformance(data, *args, **kwargs))

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
        """Return ..."""
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

    def _getUnits(self, group = False, **kwargs):
        """Return tuple with units that match a given property.
        
        Examples:
            return visible units: self._getUnits(visible = True)
        """

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

    def _setUnits(self, units):
        """Create instances for units."""
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

        # create instances of unit classes
        # and link units params to local params dict
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

    def _setLinks(self, links):

        # update link parameters
        self._params['links'] = {}
        for layerID in range(len(self._params['units']) - 1):
            source = self._params['units'][layerID]['name']
            target = self._params['units'][layerID + 1]['name']
            x = len(self.units[source].params['label'])
            y = len(self.units[target].params['label'])
            self._params['links'][(layerID, layerID + 1)] = {
                'source': source, 'target': target,
                'A': numpy.ones([x, y], dtype = bool)}
        return True

    def _getMapping(self):
        """Return tuple with names of layers from input to output."""
        return tuple([layer['name'] for layer in self._params['units']])

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

    ####################################################################
    # Unit evaluation                                                  #
    ####################################################################

    def getUnitExpect(self, inData, mapping = None):
        """Return expected values of a layer."""
        if mapping == None:
            mapping = self._getMapping()
        if len(mapping) == 2:
            return self.units[mapping[1]].expect(inData,
                self.units[mapping[0]].params)
        outData = numpy.copy(inData)
        for id in range(len(mapping) - 1):
            outData = self.units[mapping[id + 1]].expect(outData,
                self.units[mapping[id]].params)
        return outData

    def getUnitSamples(self, data, mapping = None, expectLast = False):
        """Return sampled unit values calculated from mapping.
        
        Keyword Arguments:
            expectLast -- return expectation values of the units
                for the last step instead of sampled values"""

        if mapping == None:
            mapping = self._getMapping()
        if expectLast:
            if len(mapping) == 1:
                return data
            elif len(mapping) == 2:
                return  self.units[mapping[1]].expect(
                    self.units[mapping[0]].getSamples(data),
                    self.units[mapping[0]].params)
            return self.units[mapping[-1]].expect(
                self.getUnitSamples(data, mapping[0:-1]),
                self.units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self.units[mapping[0]].getSamples(data)
            elif len(mapping) == 2:
                return self.units[mapping[1]].getSamplesFromInput(
                    data, self.units[mapping[0]])
            data = numpy.copy(data)
            for id in range(len(mapping) - 1):
                data = self.units[mapping[id + 1]].getSamplesFromInput(
                    data, self.units[mapping[id]])
            return data

    def getUnitValues(self, data, mapping = None, expectLast = False):
        """Return unit values calculated from mappings.
        
        Keyword Arguments:
            expectLast -- return expectation values of the units
                for the last step instead of maximum likelihood values"""

        if mapping == None:
            mapping = self._getMapping()
        if expectLast:
            if len(mapping) == 1:
                return data
            elif len(mapping) == 2:
                return self.units[mapping[1]].expect(
                    self.units[mapping[0]].getSamples(data),
                    self.units[mapping[0]].params)
            return self.units[mapping[-1]].expect(
                self.getUnitValues(data, mapping[0:-1]),
                self.units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self.units[mapping[0]].getValues(data)
            elif len(mapping) == 2:
                return self.units[mapping[1]].getValues(
                    self.units[mapping[1]].expect(data,
                    self.units[mapping[0]].params))
            data = numpy.copy(data)
            for id in range(len(mapping) - 1):
                data = self.units[mapping[id + 1]].getValues(
                    self.units[mapping[id + 1]].expect(data,
                    self.units[mapping[id]].params))
            return data

    def getUnitEnergy(self, data, mapping = None):
        """Return unit energies of a layer."""
        if len(mapping) == 1:
            pass
        elif len(mapping) == 2:
            data = self.getUnitValues(data, mapping)
        else:
            data = self.getUnitValues(self.getUnitExpect(data, mapping[0:-1]), mapping[-2:])
        return self.units[mapping[-1]].energy(data)

    def getUnitError(self, data, mapping = None, block = [], **kwargs):
        """Return euclidean reconstruction error of units.
        
        Description:
            distance := ||dataOut - modelOut||
        """

        if mapping == None:
            mapping = self._getMapping()
        if block == []:
            modelOut = self.getUnitExpect(data[0], mapping)
        else:
            dataInCopy = numpy.copy(data[0])
            for i in block:
                dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self.getUnitExpect(dataInCopy, mapping)
        return numpy.sqrt(((data[1] - modelOut) ** 2).sum(axis = 0))

    def getUnitPerformance(self, data, *args, **kwargs):
        """Return unit performance respective to input and output data.

        Arguments:
            dataIn -- Numpy array containing real input data for system
            dataOut -- Numpy array containing real output data of system

        Description:
            performance := 1 - error / ||data||
        """

        err = self.getUnitError(data, *args, **kwargs)
        nrm = numpy.sqrt((data[1] ** 2).sum(axis = 0))
        return 1.0 - err / nrm

    ####################################################################
    # Artificial neuronal network links                                #
    ####################################################################

    class annLinks():
        """Class to unify common ann link attributes."""

        params = {}

        def __init__(self):
            pass

        @staticmethod
        def getUpdates(data, model):
            """Return weight updates of a link layer."""
            pData = numpy.dot(data[0].T, data[1])
            pModel = numpy.dot(model[0].T, model[1])
            wDelta = (pData - pModel) / float(data[1].size)
            return { 'W': wDelta }

        #def calcLogisticUpdates(self, data, model, weights):
            #"""Return parameter updates of a sigmoidal output layer
            #calculated from real data and modeled data."""
            #shape = (1, len(self.params['label']))
            #updBias = \
                #numpy.mean(data[1] - model[1], axis = 0).reshape(shape)
            #return { 'bias': updBias }


        # lets calculate with link params

        @staticmethod
        def one(dict):
            return {key: numpy.ones(shape = dict[key].shape) for key in dict.keys()}

        @staticmethod
        def zero(dict):
            return {key: numpy.zeros(shape = dict[key].shape) for key in dict.keys()}

        @staticmethod
        def sign(dict, remap = None):
            if remap == None:
                return {key: numpy.sign(dict[key]) for key in dict.keys()}
            return {key:
                (remap[0] * (numpy.sign(dict[key]) < 0.0)
                + remap[1] * (numpy.sign(dict[key]) == 0.0)
                + remap[2] * (numpy.sign(dict[key]) > 0.0)) for key in dict.keys()}

        @staticmethod
        def minmax(dict, min = None, max = None):
            if min == None:
                return {key: numpy.minimum(dict[key], max)
                    for key in dict.keys()}
            if max == None:
                return {key: numpy.maximum(dict[key], min)
                    for key in dict.keys()}
            return {key: numpy.maximum(numpy.minimum(dict[key], max), min)
                for key in dict.keys()}

        @staticmethod
        def sum(left, right):
            if isinstance(left, float) or isinstance(left, int):
                return {key: left + right[key] for key in left.keys()}
            if isinstance(right, float) or isinstance(right, int):
                return {key: left[key] + right for key in left.keys()}
            return {key: left[key] + right[key] for key in left.keys()}

        @staticmethod
        def multiply(left, right):
            if isinstance(left, float) or isinstance(left, int):
                return {key: left * right[key] for key in left.keys()}
            if isinstance(right, float) or isinstance(right, int):
                return {key: left[key] * right for key in left.keys()}
            return {key: left[key] * right[key] for key in left.keys()}

    ####################################################################
    # Artificial neuronal network units                                #
    ####################################################################

    class annUnits():
        """Class to unify common ann unit attributes."""

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

        def getUpdates(self, data, model, source):
            return self.getParamUpdates(data, model, self.getWeights(source))

        def getDelta(self, inData, outDelta, source, target):
            return self.getDeltaFromBackpropagation(inData, outDelta,
                self.getWeights(source), self.getWeights(target))

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

        # lets calculate with unit params

        @staticmethod
        def one(dict):
            return {key: numpy.ones(shape = dict[key].shape) for key in dict.keys()}

        @staticmethod
        def zero(dict):
            return {key: numpy.zeros(shape = dict[key].shape) for key in dict.keys()}

        @staticmethod
        def sign(dict, remap = None):
            if remap == None:
                return {key: numpy.sign(dict[key]) for key in dict.keys()}
            return {key:
                (remap[0] * (numpy.sign(dict[key]) < 0.0)
                + remap[1] * (numpy.sign(dict[key]) == 0.0)
                + remap[2] * (numpy.sign(dict[key]) > 0.0)) for key in dict.keys()}

        @staticmethod
        def minmax(dict, min = None, max = None):
            if min == None:
                return {key: numpy.minimum(dict[key], max)
                    for key in dict.keys()}
            if max == None:
                return {key: numpy.maximum(dict[key], min)
                    for key in dict.keys()}
            return {key: numpy.maximum(numpy.minimum(dict[key], max), min)
                for key in dict.keys()}

        @staticmethod
        def sum(left, right):
            if isinstance(left, float) or isinstance(left, int):
                return {key: left + right[key] for key in left.keys()}
            if isinstance(right, float) or isinstance(right, int):
                return {key: left[key] + right for key in left.keys()}
            return {key: left[key] + right[key] for key in left.keys()}

        @staticmethod
        def multiply(left, right):
            if isinstance(left, float) or isinstance(left, int):
                return {key: left * right[key] for key in left.keys()}
            if isinstance(right, float) or isinstance(right, int):
                return {key: left[key] * right for key in left.keys()}
            return {key: left[key] * right[key] for key in left.keys()}

    ####################################################################
    # Sigmoidal artificial neuronal network units                      #
    ####################################################################

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

        def getParamUpdates(self, data, model, weights):
            """Return parameter updates of a sigmoidal output layer
            calculated from real data and modeled data."""
            shape = (1, len(self.params['label']))
            updBias = \
                numpy.mean(data[1] - model[1], axis = 0).reshape(shape)
            return { 'bias': updBias }

        def getDeltaFromBackpropagation(self, data_in, delta_out, W_in, W_out):
            return numpy.dot(delta_out, W_out) * self.Dlogistic((self.params['bias'] + numpy.dot(data_in, W_in)))

        #def calcLinearUpdates(self, data, model, weights):
            #"""Return parameter updates of a linear output layer
            #calculated from real data and modeled data."""
            #shape = (1, len(self.params['label']))
            #updBias = \
                #numpy.mean(data[1] - model[1], axis = 0).reshape(shape)
            #return { 'bias': updBias }

        #def calcLogisticUpdates(self, data, model, weights):
            #"""Return parameter updates of a sigmoidal output layer
            #calculated from real data and modeled data."""
            #shape = (1, len(self.params['label']))
            #updBias = \
                #numpy.mean(data[1] - model[1], axis = 0).reshape(shape)
            #return { 'bias': updBias }

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
        def logistic(x):
            """Standard logistic function."""
            return 1.0 / (1.0 + numpy.exp(-x))

        @staticmethod
        def Dlogistic(x):
            """Derivation of standard logistic function."""
            return ((1.0 / (1.0 + numpy.exp(-x)))
                * (1.0 - 1.0 / (1.0 + numpy.exp(-x))))

        @staticmethod
        def tanh(x):
            """Standard hyperbolic tangens function."""
            return numpy.tanh(x)

        @staticmethod
        def Dtanh(x):
            """Derivation of standard hyperbolic tangens function."""
            return 1.0 - tanh(x) ** 2

        @staticmethod
        def tanhEff(x):
            """Hyperbolic tangens function, proposed in paper:
            'Efficient BackProp' by LeCun, Bottou, Orr, Müller"""
            return 1.7159 * numpy.tanh(0.6666 * x)

    ####################################################################
    # Gaussian artificial neuronal network units                       #
    ####################################################################

    class gaussUnits(annUnits):
        """Units with linear activation function and gaussian distribution"""

        def initialize(self, data = None, vSigma = 0.4):
            """Initialize parameters of gauss distributed units."""
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
            """Update gaussian units."""
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

        def getParamUpdates(self, data, model, weights):
            """Return parameter updates of a gaussian output layer
            calculated from real data and modeled data."""
            shape = (1, len(self.params['label']))
            var = numpy.exp(self.params['lvar'])
            bias = self.params['bias']
            
            updBias = \
                numpy.mean(data[1] - model[1], axis = 0).reshape(shape) / var
            updData = \
                numpy.mean(0.5 * (data[1] - bias) ** 2 - data[1]
                * numpy.dot(data[0], weights), axis = 0)
            updModel = \
                numpy.mean(0.5 * (model[1] - bias) ** 2 - model[1]
                * numpy.dot(model[0], weights), axis = 0)
            updLVar = (updData - updModel).reshape(shape) / var

            return { 'bias': updBias, 'lvar': updLVar }

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
