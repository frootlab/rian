#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# This python module contains a generic class for layered artificial   #
# neural networks aimed to provide common attributes, methods and      #
# optimization strategies like backpropagation and subclasses like     #
# different types of units to special subtypes of artificial neural    #
# networks like restricted boltzmann machines or deep beliefe networks #
########################################################################

import nemoa.system.base, numpy

class ann(nemoa.system.base.system):
    """Artificial Neuronal Network (ANN).

    References:
        "Learning representations by back-propagating errors",
        Rumelhart, D. E., Hinton, G. E., and Williams, R. J. (1986)"""

    ####################################################################
    # (Artificial Neuronal Network) System Configuration               #
    ####################################################################

    def _configure(self, config = {},
        network = None, dataset = None, update = False):
        """Configure ANN to network and dataset.

        Keyword Arguments:
            config -- dictionary containing system configuration
            network -- nemoa network instance
            dataset -- nemoa dataset instance """

        if not 'check' in self._config: self._config['check'] = {
            'config': False, 'network': False, 'dataset': False}
        self.setConfig(config)
        if not network == None: self._setNetwork(network, update)
        if not dataset == None: self._setDataset(dataset)

        return self.isConfigured()

    def _updateUnitsAndLinks(self, *args, **kwargs):

        nemoa.log('update system units and links')
        self.setUnits(self._params['units'], initialize = False)
        self.setLinks(self._params['links'], initialize = False)

        return True

    def _setNetwork(self, network, update = False, *args, **kwargs):
        """Update units and links to network instance. """

        nemoa.log("""get system units and links from network '%s'
            """ % (network.name()))
        nemoa.setLog(indent = '+1')

        if not nemoa.type.isNetwork(network):
            nemoa.log('error', """could not configure system:
                network instance is not valid!""")
            nemoa.setLog(indent = '-1')
            return False

        self.setUnits(self._getUnitsFromNetwork(network),
            initialize = (update == False))
        self.setLinks(self._getLinksFromNetwork(network),
            initialize = (update == False))

        self._config['check']['network'] = True
        nemoa.setLog(indent = '-1')

        return True

    def _setDataset(self, dataset, *args, **kwargs):
        """check if dataset columns match with visible units. """

        # check dataset instance
        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not configure system: dataset instance is not valid!')

        # compare visible units labels with dataset columns
        mapping = self.getMapping()
        unitsInGroups = self.getUnits(visible = True)
        units = []
        for group in unitsInGroups: units += group
        if dataset.getColLabels() != units: return nemoa.log('error',
            'could not configure system: visible units differ from dataset columns!')

        self._config['check']['dataset'] = True

        return True

    def _checkParams(self, params):
        """Check if system parameter dictionary is valid. """

        return self._checkUnitParams(params) \
            and self._checkLinkParams(params)

    ####################################################################
    # (Artificial Neuronal Network) Unit Configuration                 #
    ####################################################################

    def _initUnits(self, dataset = None):
        """Initialize unit parameteres.

        Keyword Arguments:
            dataset -- nemoa dataset instance OR None

        Description:
            Initialize all unit parameters. """

        if not (dataset == None) and not nemoa.type.isDataset(dataset):
            return nemoa.log('error', """
                could not initilize unit parameters:
                invalid dataset argument given!""")

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
        """Create instances for units."""

        if not isinstance(units, list): return False
        if len(units) < 2: return False
        self._params['units'] = units

        # get unit classes from system config
        visibleUnitsClass = self._config['params']['visibleClass']
        hiddenUnitsClass = self._config['params']['hiddenClass']
        for id in range(len(self._params['units'])):
            if self._params['units'][id]['visible'] == True:
                self._params['units'][id]['class'] = visibleUnitsClass
            else: self._params['units'][id]['class'] = hiddenUnitsClass

        # create instances of unit classes
        # and link units params to local params dict
        self.units = {}
        for id in range(len(self._params['units'])):
            unitClass = self._params['units'][id]['class']
            name = self._params['units'][id]['name']
            if unitClass == 'sigmoid': self.units[name] = self.UnitLayerSigmoid()
            elif unitClass == 'gauss': self.units[name] = self.UnitLayerGauss()
            else: return nemoa.log('error', """
                could not create system:
                unit class '%s' is not supported!""" % (unitClass))
            self.units[name].params = self._params['units'][id]

        return True

    def _checkUnitParams(self, params):
        """Check if system parameter dictionary is valid respective to units. """

        if not isinstance(params, dict) \
            or not 'units' in params.keys() \
            or not isinstance(params['units'], list): return False
        for id in range(len(params['units'])):
            layer = params['units'][id]
            if not isinstance(layer, dict):
                return False
            for attr in ['name', 'visible', 'class', 'label']:
                if not attr in layer.keys():
                    return False
            if layer['class'] == 'gauss' \
                and not self.UnitLayerGauss.check(layer):
                return False
            elif params['units'][id]['class'] == 'sigmoid' \
                and not self.UnitLayerSigmoid.check(layer):
                return False

        return True

    def _getUnitsFromNetwork(self, network):
        """Return tuple with lists of unit labels from network. """

        units = [{'name': layer, 'label':
            network.nodes(type = layer)}
            for layer in network.layers()]
        for group in units:
            group['visible'] = network.node(group['label'][0])['params']['visible']
            group['id'] = network.node(group['label'][0])['params']['layerId']

        return units

    def _getUnitInformation(self, unit, layer = None):
        """Return dict information for a given unit. """

        if not layer: layer = self.getGroupOfUnit(unit)
        if not layer in self.units: return {}

        return self.units[layer].get(unit)

    def _removeUnits(self, layer = None, label = []):
        """Remove units from parameter space. """

        if not layer == None and not layer in self.units.keys():
            return nemoa.log('error', """could not remove units:
                unknown layer '%'""" % (layer))

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
            self.UnitLayerGauss.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            self.UnitLayerSigmoid.remove(layer, select)

        # delete units from link parameter arrays
        self._removeUnitsLinks(layer, select)

        return True

    ####################################################################
    # (Artificial Neuronal Network) Link Configuration                 #
    ####################################################################

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

    def _initLinks(self, dataset = None):
        """Initialize link parameteres (weights).

        Keyword Arguments:
            dataset -- nemoa dataset instance OR None

        Description:
            If dataset is None, initialize weights matrices with zeros
            and all adjacency matrices with ones.
            if dataset is nemoa network instance,
            initialize weights with random values, that fit ...."""

        if not(dataset == None) and \
            not nemoa.type.isDataset(dataset): return nemoa.log('error', """
            could not initilize link parameters:
            invalid dataset argument given!""")

        for links in self._params['links']:
            source = self._params['links'][links]['source']
            target = self._params['links'][links]['target']
            A = self._params['links'][links]['A']
            x = len(self.units[source].params['label'])
            y = len(self.units[target].params['label'])
            alpha = self._config['init']['wSigma'] \
                if 'wSigma' in self._config['init'] else 1.0
            sigma = numpy.ones([x, 1], dtype = float) * alpha / x

            if dataset == None: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)
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
            else: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random

        return True

    def _checkLinkParams(self, params):
        """Check if system parameter dictionary is valid respective to links."""

        if not isinstance(params, dict) \
            or not 'links' in params.keys() \
            or not isinstance(params['links'], dict): return False
        for id in params['links'].keys():
            if not isinstance(params['links'][id], dict): return False
            for attr in ['A', 'W', 'source', 'target']:
                if not attr in params['links'][id].keys(): return False

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

        return nemoa.log('error', """Could not get links:
            Layer '%s' and layer '%s' are not connected.
            """ % (source['name'], target['name']))

    def _getLinksFromConfig(self):
        """Return links from adjacency matrix. """

        groups = self.getGroups()
        if not groups: return False

        links = ()
        for g in range(len(groups) - 1):
            s = groups[g]
            t = groups[g + 1]

            lg = []
            for i, u in enumerate(self.units[s].params['label']):
                for j, v in enumerate(self.units[t].params['label']):
                    if not 'A' in self._params \
                        or self._params['links'][(g, g + 1)]['A'][i, j]:
                        lg.append((u, v))

            links += (lg, )

        return links

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
    # (Artificial Neuronal Network) Parameter Optimization             #
    ####################################################################

    # Parameter Initialization

    def _initParams(self, dataset = None):
        """Initialize system parameters.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Initialize all unit and link parameters to dataset. """

        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not initilize system: invalid dataset instance given!')

        return self._initUnits(dataset) and self._initLinks(dataset)


    # Generic Parameter Functions

    def _optGetData(self, dataset, **kwargs):

        config = self._config['optimize']
        kwargs['size'] = config['minibatchSize']
        if config['modCorruptionEnable']: kwargs['corruption'] = \
            (config['modCorruptionType'], config['modCorruptionFactor'])
        return dataset.getData(**kwargs)

    def _optGetValues(self, inputData):
        """Forward pass (compute estimated values, from given input). """

        layers = self.getMapping()
        out = {}
        for id, layer in enumerate(layers):
            if id == 0:
                out[layer] = inputData
                continue
            out[layer] = self.evalUnitExpect(
                out[layers[id - 1]], layers[id - 1:id + 1])

        return out

    def _optGetDeltas(self, outputData, out):
        """Return weight delta from backpropagation of error. """

        layers = self.getMapping()
        delta = {}
        for id in range(len(layers) - 1)[::-1]:
            src = layers[id]
            tgt = layers[id + 1]
            if id == len(layers) - 2:
                delta[(src, tgt)] = out[tgt] - outputData
                continue
            inData = self.units[tgt].params['bias'] \
                + numpy.dot(out[src], self._params['links'][(id, id + 1)]['W'])
            grad = self.units[tgt].grad(inData)
            delta[(src, tgt)] = numpy.dot(delta[(tgt, layers[id + 2])],
                self._params['links'][(id + 1, id + 2)]['W'].T) * grad

        return delta

    def _optUpdateParams(self, updates):
        """Update parameters from dictionary."""

        layers = self.getMapping()
        for id, layer in enumerate(layers[:-1]):
            src = layer
            tgt = layers[id + 1]
            self._params['links'][(id, id + 1)]['W'] += \
                updates['links'][(src, tgt)]['W']
            self.units[tgt].update(updates['units'][tgt])

        return True

    # Backpropagation of Error (BPROP) specific Functions

    def _optBPROP(self, dataset, schedule, tracker):
        """Optimize parameters using backpropagation."""

        cnf = self._config['optimize']
        layers = self.getMapping()

        # update parameters
        for epoch in xrange(cnf['updates']):

            # Get data (sample from minibatches)
            if epoch % cnf['minibatchInterval'] == 0:
                #data = dataset.getData(size = cnf['minibatchSize'],
                #    cols = (layers[0], layers[-1]))
                data = self._optGetData(dataset, cols = (layers[0], layers[-1]))
            # Forward pass (Compute value estimations from given input)
            out = self._optGetValues(data[0])
            # Backward pass (Compute deltas from backpropagation of error)
            delta = self._optGetDeltas(data[1], out)
            # Compute parameter updates
            updates = self._optGetUpdatesBPROP(out, delta)
            # Update parameters
            self._optUpdateParams(updates)
            # Trigger tracker (getch, calc inspect function etc)
            event = tracker.trigger()
            if event:
                if event == 'abort': break

        return True

    def _optGetUpdatesBPROP(self, out, delta, rate = 0.1):
        """Compute parameter update directions from weight deltas."""

        def getUpdate(grad, rate): return {
            key: rate * grad[key] for key in grad.keys()}

        layers = self.getMapping()
        links = {}
        units = {}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            units[tgt] = getUpdate(
                self.units[tgt].getUpdatesFromDelta(
                delta[src, tgt]), rate)
            links[(src, tgt)] = getUpdate(
                self.LinkLayer.getUpdatesFromDelta(out[src],
                delta[src, tgt]), rate)

        return {'units': units, 'links': links}

    # Resilient Backpropagation (RPROP) specific Functions

    def _optRPROP(self, dataset, schedule, tracker):
        """Optimize parameters using resiliant backpropagation."""

        cnf = self._config['optimize']
        layers = self.getMapping()

        # update parameters
        for epoch in xrange(cnf['updates']):

            # Get data (sample from minibatches)
            if epoch % cnf['minibatchInterval'] == 0:
                data = dataset.getData(size = cnf['minibatchSize'],
                    cols = (layers[0], layers[-1]))
            # Forward pass (Compute value estimations from given input)
            out = self._optGetValues(data[0])
            # Backward pass (Compute deltas from backpropagation of error)
            delta = self._optGetDeltas(data[1], out)
            # Compute updates
            updates = self._optGetUpdatesRPROP(out, delta, tracker)
            # Update parameters
            self._optUpdateParams(updates)
            # Trigger tracker (getch, calc inspect function etc)
            event = tracker.trigger()
            if event:
                if event == 'abort': break

        return True

    def _optGetUpdatesRPROP(self, out, delta, tracker):

        def getDict(dict, val): return {key: val * numpy.ones(
            shape = dict[key].shape) for key in dict.keys()}

        def getUpdate(prevGrad, prevUpdate, grad, accel, minFactor, maxFactor):
            update = {}
            for key in grad.keys():
                sign = numpy.sign(grad[key])
                a = numpy.sign(prevGrad[key]) * sign
                magnitude = numpy.maximum(numpy.minimum(prevUpdate[key] \
                    * (accel[0] * (a == -1) + accel[1] * (a == 0)
                    + accel[2] * (a == 1)), maxFactor), minFactor)
                update[key] = magnitude * sign
            return update

        # RProp parameters
        accel     = (0.5, 1.0, 1.2)
        initRate  = 0.001
        minFactor = 0.000001
        maxFactor = 50.0

        layers = self.getMapping()

        # Compute gradient from delta rule
        grad = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            grad['units'][tgt] = \
                self.units[tgt].getUpdatesFromDelta(delta[src, tgt])
            grad['links'][(src, tgt)] = \
                self.LinkLayer.getUpdatesFromDelta(out[src], delta[src, tgt])

        # Get previous gradients and updates
        prev = tracker.read()
        if not prev:
            prev = {
                'gradient': grad,
                'update': {'units': {}, 'links': {}}}
            for id, src in enumerate(layers[:-1]):
                tgt = layers[id + 1]
                prev['update']['units'][tgt] = \
                    getDict(grad['units'][tgt], initRate)
                prev['update']['links'][(src, tgt)] = \
                    getDict(grad['links'][(src, tgt)], initRate)
        prevGradient = prev['gradient']
        prevUpdate = prev['update']

        # Compute updates
        update = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]

            # calculate current rates for units
            update['units'][tgt] = getUpdate(
                prevGradient['units'][tgt],
                prevUpdate['units'][tgt],
                grad['units'][tgt],
                accel, minFactor, maxFactor)

            # calculate current rates for links
            update['links'][(src, tgt)] = getUpdate(
                prevGradient['links'][(src, tgt)],
                prevUpdate['links'][(src, tgt)],
                grad['links'][(src, tgt)],
                accel, minFactor, maxFactor)

        # Save updates to store
        tracker.write(gradient = grad, update = update)

        return update

    ####################################################################
    # Evaluation                                                       #
    ####################################################################

    ####################################################################
    # (Artificial Neuronal Network) System Evaluation                  #
    ####################################################################

    def evalSystem(self, data, func = 'accuracy', **kwargs):
        """Return evaluation value for system respective to data.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            func -- string containing system evaluation function
                For a full list of available system evaluation functions
                see: system.about('eval') """

        # get evaluation function
        methods = self._getSystemEvalMethods()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate system: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate units: unknown method '%s'" % (method))

        # prepare arguments for evaluation function
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # prepare keyword arguments for evaluation function
        evalKwargs = kwargs.copy()
        if not 'mapping' in evalKwargs.keys() \
            or evalKwargs['mapping'] == None:
            evalKwargs['mapping'] = self.getMapping()

        # evaluate
        values = getattr(self, method)(*evalArgs, **evalKwargs)

        # create output
        retFmt = methods[func]['return']
        if retFmt == 'scalar': return values
        return nemoa.log('warning', 'could not perform evaluation')

    @staticmethod
    def _getSystemEvalMethods(): return {
        'energy': {
            'name': 'total energy',
            'description': 'sum of unit and link energies',
            'method': 'evalSystemEnergy',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'error': {
            'name': 'total error',
            'description': 'sum of errors of reconstructed values',
            'method': 'evalSystemError',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'accuracy': {
            'name': 'average accuracy',
            'description': 'mean accuracy of reconstructed values',
            'method': 'evalSystemAccuracy',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'precision': {
            'name': 'average precision',
            'description': 'mean precision of reconstructed values',
            'method': 'evalSystemPrecision',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'}
        }

    def evalSystemError(self, *args, **kwargs):
        """Return sum of data reconstruction errors of output units. """
        return numpy.sum(self.evalUnitError(*args, **kwargs))

    def evalSystemAccuracy(self, *args, **kwargs):
        """Return mean data reconstruction accuracy of output units. """
        return numpy.mean(self.evalUnitAccuracy(*args, **kwargs))

    def evalSystemPrecision(self, *args, **kwargs):
        """Return mean data reconstruction precision of output units. """
        return numpy.mean(self.evalUnitPrecision(*args, **kwargs))

    def evalSystemEnergy(self, data, *args, **kwargs):
        """Return system energy. """

        mapping = list(self.getMapping())
        energy = 0.0

        # sum energy of units and links
        for i in range(1, len(mapping) + 1): energy += \
            numpy.sum(self.evalUnitEnergy(data[0],
            mapping = tuple(mapping[:i])))
        for i in range(1, len(mapping)): energy += \
            numpy.sum(self.evalLinkEnergy(data[0],
            mapping = tuple(mapping[:i+1])))

        return energy

    ####################################################################
    # (Artificial Neuronal Network) Unit Evaluation                    #
    ####################################################################

    def evalUnits(self, data, func = 'accuracy', units = None, **kwargs):
        """Return dictionary with unit evaluation values.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            func -- string containing unit evaluation function
                For a full list of available system evaluation functions
                see: system.about('units') """

        # get unit evaluation function
        methods = self._getUnitEvalMethods()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate units: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate units: unknown method '%s'" % (method))

        # prepare data for evaluation functions
        if not isinstance(data, tuple): return nemoa.log('error',
            'could not evaluate units: invalid data format given')
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # prepare keyword arguments for evaluation functions
        evalKwargs = kwargs.copy()
        if not 'mapping' in evalKwargs.keys() \
            or evalKwargs['mapping'] == None:
            evalKwargs['mapping'] = self.getMapping()
        if isinstance(units, str):
            evalKwargs['mapping'] = self.getMapping(tgt = units)

        # evaluate
        values = getattr(self, method)(*evalArgs, **evalKwargs)

        # create unit dictionary
        labels = self.getUnits(group = evalKwargs['mapping'][-1])[0]
        retFmt = methods[func]['return']

        if retFmt == 'vector': return {unit: values[:, id] \
            for id, unit in enumerate(labels)}
        elif retFmt == 'scalar': return {unit: values[id] \
            for id, unit in enumerate(labels)}
        return nemoa.log('warning', 'could not perform evaluation')

    @staticmethod
    def _getUnitEvalMethods(): return {
        'energy': {
            'name': 'energy',
            'description': 'energy of units',
            'method': 'evalUnitEnergy',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'expect': {
            'name': 'expect',
            'description': 'reconstructed values',
            'method': 'evalUnitExpect',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'values': {
            'name': 'values',
            'description': 'reconstructed values',
            'method': 'evalUnitValues',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'samples': {
            'name': 'samples',
            'description': 'reconstructed samples',
            'method': 'evalUnitSamples',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'mean': {
            'name': 'mean values',
            'description': 'mean of reconstructed values',
            'method': 'evalUnitMean',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'variance': {
            'name': 'variance',
            'description': 'variance of reconstructed values',
            'method': 'evalUnitVariance',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'residuals': {
            'name': 'residuals',
            'description': 'residuals of reconstructed values',
            'method': 'evalUnitResiduals',
            'show': 'histogram',
            'args': 'all', 'return': 'vector', 'format': '%.3f'},
        'error': {
            'name': 'error',
            'description': 'error of reconstructed values',
            'method': 'evalUnitError',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'accuracy': {
            'name': 'accuracy',
            'description': 'accuracy of reconstructed values',
            'method': 'evalUnitAccuracy',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'precision': {
            'name': 'precision',
            'description': 'precision of reconstructed values',
            'method': 'evalUnitPrecision',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'correlation': {
            'name': 'correlation',
            'description': 'correlation of reconstructed to real values',
            'method': 'evalUnitCorrelation',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'}
        }

    def evalUnitExpect(self, data, mapping = None, block = None):
        """Return (most) expected values of a layer.

        Keyword Arguments:
            data -- numpy array containing data corresponding
                to the input layer (first argument of mapping)
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple) """

        if mapping == None: mapping = self.getMapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if len(mapping) == 2: return self.units[mapping[1]].expect(
            inData, self.units[mapping[0]].params)
        outData = numpy.copy(inData)
        for id in range(len(mapping) - 1):
            outData = self.units[mapping[id + 1]].expect(
                outData, self.units[mapping[id]].params)

        return outData

    def evalUnitValues(self, data, mapping = None, block = None, expectLast = False):
        """Return unit values calculated from mappings.

        Keyword Arguments:
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            expectLast -- return expectation values of the units
                for the last step instead of maximum likelihood values """

        if mapping == None: mapping = self.getMapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if expectLast:
            if len(mapping) == 1: return inData
            elif len(mapping) == 2: return self.units[mapping[1]].expect(
                self.units[mapping[0]].getSamples(inData),
                self.units[mapping[0]].params)
            return self.units[mapping[-1]].expect(
                self.evalUnitValues(data, mapping[0:-1]),
                self.units[mapping[-2]].params)
        else:
            if len(mapping) == 1: return self.units[mapping[0]].getValues(inData)
            elif len(mapping) == 2: return self.units[mapping[1]].getValues(
                self.units[mapping[1]].expect(inData,
                self.units[mapping[0]].params))
            data = numpy.copy(inData)
            for id in range(len(mapping) - 1):
                data = self.units[mapping[id + 1]].getValues(
                    self.units[mapping[id + 1]].expect(data,
                    self.units[mapping[id]].params))
            return data

    def evalUnitSamples(self, data, mapping = None, block = None, expectLast = False):
        """Return sampled unit values calculated from mapping.

        Keyword Arguments:
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            expectLast -- return expectation values of the units
                for the last step instead of sampled values """

        if mapping == None: mapping = self.getMapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if expectLast:
            if len(mapping) == 1: return data
            elif len(mapping) == 2: return self.units[mapping[1]].expect(
                self.units[mapping[0]].getSamples(data),
                self.units[mapping[0]].params)
            return self.units[mapping[-1]].expect(
                self.evalUnitSamples(data, mapping[0:-1]),
                self.units[mapping[-2]].params)
        else:
            if len(mapping) == 1: return self.units[mapping[0]].getSamples(data)
            elif len(mapping) == 2: return self.units[mapping[1]].getSamplesFromInput(
                    data, self.units[mapping[0]].params)
            data = numpy.copy(data)
            for id in range(len(mapping) - 1):
                data = self.units[mapping[id + 1]].getSamplesFromInput(
                    data, self.units[mapping[id]].params)
            return data

    def evalUnitResiduals(self, data, mapping = None, block = None):
        """Return reconstruction residuals of units.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays containing input and
                output data coresponding to the first and the last layer
                in the mapping
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            block -- list of strings containing labels of units in the input
                layer that are blocked by setting the values to their means """

        dIn, dOut = data

        # set mapping: inLayer to outLayer (if not set)
        if mapping == None: mapping = self.getMapping()

        # set unit values to mean (optional)
        if isinstance(block, list):
            dIn = numpy.copy(dIn)
            for i in block: dIn[:, i] = numpy.mean(dIn[:, i])

        # calculate estimated output values
        mOut = self.evalUnitExpect(dIn, mapping)

        # calculate residuals
        res = dOut - mOut

        return res

    def evalUnitEnergy(self, data, mapping = None):
        """Return unit energies of a layer.

        Keyword Arguments:
            data -- input data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple) """

        # set mapping: inLayer to outLayer (if not set)
        if mapping == None: mapping = self.getMapping()

        data = self.evalUnitExpect(data, mapping)

        return self.units[mapping[-1]].energy(data)

    def evalUnitMean(self, data, mapping = None, block = None, **kwargs):
        """Return mean of reconstructed unit values.

        Keyword Arguments:
            data -- input data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            block -- list of string containing labels of units in the input
                layer that are blocked by setting the values to their means """

        if mapping == None: mapping = self.getMapping()
        if block == None: modelOut = self.evalUnitExpect(data[0], mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self.evalUnitExpect(dataInCopy, mapping)

        return modelOut.mean(axis = 0)

    def evalUnitVariance(self, data, mapping = None, block = None, **kwargs):
        """Return variance of reconstructed unit values.

        Keyword Arguments:
            data -- input data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            block -- list of string containing labels of units in the input
                layer that are blocked by setting the values to their means """

        if mapping == None: mapping = self.getMapping()
        if block == None: modelOut = self.evalUnitExpect(data, mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self.evalUnitExpect(dataInCopy, mapping)

        return modelOut.var(axis = 0)

    def evalUnitError(self, data, norm = 'ME', **kwargs):
        """Return reconstruction error of units (depending on norm)

        Keyword Arguments:
            data -- see evalUnitResiduals
            mapping -- see evalUnitResiduals
            block -- see evalUnitResiduals
            norm -- used norm to calculate data reconstuction error
                from residuals. see getDataMean for a list of provided norms """

        res = self.evalUnitResiduals(data, **kwargs)
        error = self.getDataMean(res, norm = norm)

        return error

    def evalUnitAccuracy(self, data, norm = 'MSE', **kwargs):
        """Return unit reconstruction accuracy.

        Keyword Arguments:
            data -- see evalUnitResiduals
            mapping -- see evalUnitResiduals
            block -- see evalUnitResiduals
            norm -- used norm to calculate accuracy
                see getDataNorm for a list of provided norms

        Description:
            accuracy := 1 - norm(residuals) / norm(data). """

        res = self.evalUnitResiduals(data, **kwargs)
        normres = self.getDataMean(res, norm = norm)
        normdat = self.getDataMean(data[1], norm = norm)

        return 1.0 - normres / normdat

    def evalUnitPrecision(self, data, norm = 'SD', **kwargs):
        """Return unit reconstruction precision.

        Keyword Arguments:
            data -- see evalUnitResiduals
            mapping -- see evalUnitResiduals
            block -- see evalUnitResiduals
            norm -- used norm to calculate precision
                see getDataDeviation for a list of provided norms

        Description:
            precision := 1 - dev(residuals) / dev(data). """

        res = self.evalUnitResiduals(data, **kwargs)
        devres = self.getDataDeviation(res, norm = norm)
        devdat = self.getDataDeviation(data[1], norm = norm)

        return 1.0 - devres / devdat

    # 2 Do
    def evalUnitCorrelation(self, data, mapping = None, block = None, **kwargs):
        """Return reconstruction correlation of units.

        Keyword Arguments:
            data -- input data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)
            block -- list of string containing labels of units in the input
                layer that are blocked by setting the values to their means """

        if mapping == None: mapping = self.getMapping()
        if block == None: modelOut = self.evalUnitExpect(data, mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self.evalUnitExpect(dataInCopy, mapping)

        M = numpy.corrcoef(numpy.hstack(data).T)

        return True

    #def _getUnitEvalIntAccuracy(self, data, k = 1, **kwargs):
        #"""Return 'intrinsic accuracy' of units.

        #'intrinsic accuracy' := relperf
            #where model(v) is generated with: data(u not v) = mean(data(u))"""
        #vSize = len(self.units['visible'].params['label'])
        #relIntApprox = numpy.empty(vSize)
        #for v in range(vSize):
            #block = range(vSize)
            #block.pop(v)
            #relIntApprox[v] = self._getUnitevalSystemAccuracy(
                #data, block = block, k = k)[0][v]
        #return relIntApprox, None

    #def _getUnitEvalExtAccuracy(self, data, block = [], k = 1, **kwargs):
        #"""Return 'extrinsic accuracy' of units.

        #'extrinsic accuracy' := relApprox
            #where model(v) is generated with data(v) = mean(data(v))"""
        #relExtApprox = numpy.empty(len(self.units['visible'].params['label']))
        #for v in range(len(self.units['visible'].params['label'])):
            #relExtApprox[v] = self._getUnitevalSystemAccuracy(
                #data, block = block + [v], k = k)[0][v]
        #return relExtApprox, None

    #def _getUnitEvalRelativeIntAccuracy(self, data, k = 1, **kwargs):
        #"""Return 'intrinsic relative accuracy' of units

        #'intrinsic relative accuracy' := relperf
            #where model(v) is generated with data(u not v) = mean(data(u))"""
        #vSize = len(self.units['visible'].params['label'])
        #relIntApprox = numpy.empty(vSize)
        #for v in range(vSize):
            #block = range(vSize)
            #block.pop(v)
            #relIntApprox[v] = self._getUnitEvalRelativeAccuracy(
                #data = data, block = block, k = k)[0][v]
        #return relIntApprox, None

#    def _getUnitEvalRelativeExtAccuracy(self, data, block = [], k = 1, **kwargs):
#        """Return "accuracy (extrinsic)" of units.
#
#        extrelperf := relApprox where model(v) is generated with data(v) = mean(data(v))"""
#        relExtApprox = numpy.empty(len(self.units['visible'].params['label']))
#        for v in range(len(self.units['visible'].params['label'])):
#            relExtApprox[v] = self._getUnitEvalRelativeAccuracy(
#                data = data, block = block + [v], k = k)[0][v]
#        return relExtApprox, None


    ####################################################################
    # (Artificial Neuronal Network) Link Evaluation                    #
    ####################################################################

    def evalLinks(self, data, func = 'energy', **kwargs):
        """Evaluate system links respective to data.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            func -- string containing link evaluation function
                For a full list of available link evaluation functions
                see: system.about('links') """

        # get link evaluation function
        methods = self._getLinkEvalMethods()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate links: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate links: unknown method '%s'" % (method))

        # prepare arguments for evaluation functions
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # prepare keyword arguments for evaluation functions
        evalKwargs = kwargs.copy()
        if not 'mapping' in evalKwargs.keys() \
            or evalKwargs['mapping'] == None:
            evalKwargs['mapping'] = self.getMapping()

        # evaluate
        values = getattr(self, method)(*evalArgs, **evalKwargs)

        # create link dictionary
        inLabels = self.getUnits(group = evalKwargs['mapping'][-2])[0]
        outLabels = self.getUnits(group = evalKwargs['mapping'][-1])[0]
        outFmt = methods[func]['return']
        if outFmt == 'scalar':
            relDict = {}
            for inId, inUnit in enumerate(inLabels):
                for outId, outUnit in enumerate(outLabels):
                    relDict[(inUnit, outUnit)] = values[inId, outId]
            return relDict
        return nemoa.log('warning', 'could not perform evaluation')

    @staticmethod
    def _getLinkEvalMethods(): return {
        'energy': {
            'name': 'energy',
            'description': 'local energy of links',
            'method': 'evalLinkEnergy',
            'show': 'graph',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'}
        }

    def evalLinkEnergy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Keyword Arguments:
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple) """

        if len(mapping) == 1:
            return nemoa.log('error', 'bad implementation of ann.evalLinkEnergy')
        elif len(mapping) == 2:
            dIn  = data
            dOut = self.evalUnitValues(dIn, mapping)
        else:
            dIn  = self.evalUnitExpect(data, mapping[0:-1])
            dOut = self.evalUnitValues(dIn, mapping[-2:])

        sID = self.getMapping().index(mapping[-2])
        tID = self.getMapping().index(mapping[-1])
        links = self._params['links'][(sID, tID)]
        src = self.units[mapping[-2]].params
        tgt = self.units[mapping[-1]].params

        return self.LinkLayer.energy(dIn, dOut, src, tgt, links)

    ####################################################################
    # (Artificial Neuronal Network) Relations between Units            #
    ####################################################################

    def evalRelations(self, data, func = 'correlation', relations = None, **kwargs):
        """Return dictionary with unit relation values.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            func -- string containing unit relation function
                For a full list of available unit relation functions
                see: system.about('relations') """

        # get evaluation function
        methods = self._getRelationEvalMethods()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate relations: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate relations: unknown method '%s'" % (method))

        # prepare arguments for evaluation function
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # extract keyword arguments:
        # 'transform', 'format' and 'evalStat'
        if 'transform' in kwargs.keys():
            transform = kwargs['transform']
            del kwargs['transform']
        else: transform = ''
        if not isinstance(transform, str): transform = ''
        if 'format' in kwargs.keys():
            retFmt = kwargs['format']
            del kwargs['format']
        else: retFmt = 'dict'
        if not isinstance(retFmt, str): retFmt = 'dict'
        if 'evalStat' in kwargs.keys():
            evalStat = kwargs['evalStat']
            del kwargs['evalStat']
        else: evalStat = True
        if not isinstance(evalStat, bool): evalStat = True

        # prepare keyword arguments for evaluation function
        evalKwargs = kwargs.copy()
        if not 'mapping' in evalKwargs.keys() \
            or evalKwargs['mapping'] == None:
            evalKwargs['mapping'] = self.getMapping()

        # evaluate relations and get information about relation values
        values = getattr(self, method)(*evalArgs, **evalKwargs)
        valuesFmt = methods[func]['return']

        # create formated return values as matrix or dict
        # (for scalar relation evaluations)
        if valuesFmt == 'scalar':
            # optionally transform relation using 'transform' string
            # syntax for 'transform' string:
            #     'M' is the relation
            #     'C' is the standard correlation
            # example: 'M**2 - C'
            if transform:
                M = values
                if 'C' in transform: C = self.evalRelCorrelation(data)
                try:
                    T = eval(transform)
                    values = T
                except: return nemoa.log('error',
                    'could not transform relations: invalid syntax!')

            # create formated return values
            if retFmt == 'array': retVal = values
            elif retFmt == 'dict':
                inUnits = self.getUnits(group = evalKwargs['mapping'][0])[0]
                outUnits = self.getUnits(group = evalKwargs['mapping'][-1])[0]
                retVal = nemoa.common.dictFromArray(values, (inUnits, outUnits))

                # optionally evaluate statistical values over all relations
                if evalStat:
                    A = numpy.array([retVal[key] for key in retVal.keys()
                        if not key[0].split(':')[1] == key[1].split(':')[1]])
                    retVal['max']  = numpy.amax(A)
                    retVal['min']  = numpy.amin(A)
                    retVal['mean'] = numpy.mean(A)
                    retVal['std']  = numpy.std(A)
                    # force symmetric distribution with mean at 0
                    # by adding additive inverse values
                    B = numpy.concatenate((A, -A))
                    retVal['cstd'] = numpy.std(B) - numpy.mean(A)
            else: return nemoa.log('warning', 'could not perform evaluation')

            return retVal

    @staticmethod
    def _getRelationEvalMethods(): return {
        'correlation': {
            'name': 'correlation',
            'description': """
                undirected data based relation describing
                the 'linearity' between variables (units) """,
            'directed': False, 'signed': True, 'normal': True,
            'method': 'evalRelCorrelation', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'capacity': {
            'name': 'network capacity',
            'description': """
                directed graph based relation describing
                the 'network capacity' between units (variables). """,
            'directed': True, 'signed': True, 'normal': False,
            'method': 'evalRelCapacity', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'knockout': {
            'name': 'knockout effect',
            'description': """
                directed data manipulation based relation describing
                the increase of the data reconstruction error of a given
                output unit, when setting the values of a given input
                unit to its mean value. """,
            'directed': True, 'signed': True, 'normal': False,
            'method': 'evalRelKnockout', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'induction': {
            'name': 'induced deviation',
            'description': """
                directed data manipulation based relation describing
                the induced deviation of reconstructed values of a given
                output unit, when manipulating the values of a given
                input unit. """,
            'directed': True, 'signed': True, 'normal': True,
            'method': 'evalRelInduction', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        }

    def evalRelCorrelation(self, data, mapping = None, **kwargs):
        """Return correlation matrix as numpy array.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple) """

        if not mapping: mapping = self.getMapping()
        inLabels = self.getUnits(group = mapping[0])[0]
        outLabels = self.getUnits(group = mapping[-1])[0]

        # calculate symmetric correlation matrix
        M = numpy.corrcoef(numpy.hstack(data).T)
        uList = inLabels + outLabels

        # create asymmetric output matrix
        R = numpy.zeros(shape = (len(inLabels), len(outLabels)))
        for i, u1 in enumerate(inLabels):
            k = uList.index(u1)
            for j, u2 in enumerate(outLabels):
                l = uList.index(u2)
                R[i, j] = M[k, l]

        return R

    def evalRelCapacity(self, data, mapping = None, **kwargs):
        """Return network capacity as numpy array.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Description:
            Measure network capacity between input and output units. """

        if mapping == None: mapping = self.getMapping()

        # calculate product of weight matrices
        for i in range(1, len(mapping))[::-1]:
            W = self.units[mapping[i-1]].links({'name': mapping[i]})['W']
            if i == len(mapping) - 1: R = W.copy()
            else: R = numpy.dot(R.copy(), W)

        return R.T

    def evalRelKnockout(self, data, mapping = None, **kwargs):
        """Return knockout matrix as numpy array.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Description:
            Knockout units and measure effect on other units,
            respective to given data """

        if not mapping: mapping = self.getMapping()
        inLabels = self.getUnits(group = mapping[0])[0]
        outLabels = self.getUnits(group = mapping[-1])[0]

        # prepare knockout matrix
        R = numpy.zeros((len(inLabels), len(outLabels)))

        # calculate unit values without knockout
        if not 'measure' in kwargs: measure = 'error'
        else: measure = kwargs['measure']
        methodName = self.about('units', measure, 'name')
        default = self.evalUnits(data, func = measure, mapping = mapping)

        # calculate unit values with knockout
        for inId, inUnit in enumerate(inLabels):

            # modify unit and calculate unit values
            knockout = self.evalUnits(data, func = measure,
                mapping = mapping, block = [inId])

            # store difference in knockout matrix
            for outId, outUnit in enumerate(outLabels):
                R[inId, outId] = knockout[outUnit] - default[outUnit]

        return R

    def evalRelInduction(self, data, mapping = None, **kwargs):
        """Return induced deviation as numpy array.

        Keyword Arguments:
            data -- 2-tuple with numpy arrays: input data and output data
            mapping -- tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Description:
            Measure unit impact to other units,
            respective to given data """

        points  = 10
        amplify = 2.0
        gauge   = 0.05

        if not mapping: mapping = self.getMapping()
        iUnits = self.getUnits(group = mapping[0])[0]
        oUnits = self.getUnits(group = mapping[-1])[0]
        R = numpy.zeros((len(iUnits), len(oUnits)))

        # get indices of representatives
        rIds = [int((i + 0.5) * int(float(data[0].shape[0])
            / points)) for i in range(points)]

        for iId, iUnit in enumerate(iUnits):
            iCurve = numpy.take(numpy.sort(data[0][:, iId]), rIds)
            iCurve = amplify * iCurve

            # create output matrix for each output
            C = {oUnit: numpy.zeros((data[0].shape[0], points)) \
                for oUnit in oUnits}
            for pId in range(points):
                iData  = data[0].copy()
                iData[:, iId] = iCurve[pId]
                oExpect = self.evalUnits((iData, data[1]),
                    func = 'expect', mapping = mapping)
                for oUnit in oUnits: C[oUnit][:, pId] = oExpect[oUnit]

            # calculate mean of standard deviations of outputs
            for oId, oUnit in enumerate(oUnits):

                # calculate sign by correlating input and output
                corr = numpy.zeros(data[0].shape[0])
                for i in range(data[0].shape[0]):
                    corr[i] = numpy.correlate(C[oUnit][i, :], iCurve)
                sign = numpy.sign(corr.mean())

                # calculate norm by mean over maximum 5% of data
                bound = int((1.0 - gauge) * data[0].shape[0])
                subset = numpy.sort(C[oUnit].std(axis = 1))[bound:]
                norm = subset.mean() / data[1][:, oId].std()

                # calculate influence
                R[iId, oId] = sign * norm

        return R

    ####################################################################
    # Unit groups                                                      #
    ####################################################################

    def getMapping(self, src = None, tgt = None):
        """Return tuple with names of unit groups from source to target.

        Keyword Arguments:
            src -- name of source unit group
            tgt -- name of target unit group """

        mapping = tuple([g['name'] for g in self._params['units']])
        sid = mapping.index(src) \
            if isinstance(src, str) and src in mapping else 0
        tid = mapping.index(tgt) \
            if isinstance(tgt, str) and tgt in mapping else len(mapping)

        return mapping[sid:tid + 1] if sid <= tid \
            else mapping[tid:sid + 1][::-1]

    def _getTestData(self, dataset):
        """Return tuple with default test data."""

        return dataset.getData(
            cols = (self.getMapping()[0], self.getMapping()[-1]))

    ####################################################################
    # Link Layer Classes                                               #
    ####################################################################

    class LinkLayer():
        """Class to unify common ann link attributes."""

        params = {}

        def __init__(self): pass

        # 2DO
        # create classes for links

        @staticmethod
        def energy(dIn, dOut, src, tgt, links):
            """Return link energy as numpy array."""
            W = links['W']
            A = links['A']
            dSize = dIn.shape[0]
            classes = {'gauss': 0, 'sigmoid': 1}
            srcType = classes[src['class']]
            tgtType = classes[tgt['class']]
            lType = (srcType, tgtType)

            if lType == (0, 0): return \
                -(A * W * numpy.dot((dIn / numpy.exp(src['lvar'])).T, dOut) / dSize)
            if lType == (0, 1): return \
                -(A * W * numpy.dot((dIn / numpy.exp(src['lvar'])).T, dOut) / dSize)
            if lType == (1, 0): return \
                -(A * W * numpy.dot(dIn.T, dOut) / dSize)
            if lType == (1, 1): return \
                -(A * W * numpy.dot(dIn.T, dOut) / dSize)

        @staticmethod
        def getUpdates(data, model):
            """Return weight updates of a link layer."""

            D = numpy.dot(data[0].T, data[1]) / float(data[1].size)
            M = numpy.dot(model[0].T, model[1]) / float(data[1].size)

            return { 'W': D - M }

        @staticmethod
        def getUpdatesFromDelta(data, delta):

            return { 'W': -numpy.dot(data.T, delta) / data.size }

    ####################################################################
    # Gaussian to Sigmoidal Link Layer                                 #
    ####################################################################

#    class GSLinkLayer(LinkLayer):

    ####################################################################
    # Unit Layer Classes                                               #
    ####################################################################

    class UnitLayer():
        """Class to unify common ann unit attributes."""

        params = {}
        source = {}
        target = {}

        def __init__(self): pass

        def expect(self, data, source):

            if source['class'] == 'sigmoid': return \
                self.expectFromSLayer(data, source, self.weights(source))
            elif source['class'] == 'gauss': return \
                self.expectFromGLayer(data, source, self.weights(source))

            return False

        def getUpdates(self, data, model, source):

            return self.getParamUpdates(data, model, self.weights(source))

        def getDelta(self, inData, outDelta, source, target):

            return self.deltaFromBPROP(inData, outDelta,
                self.weights(source), self.weights(target))

        def getSamplesFromInput(self, data, source):

            if source['class'] == 'sigmoid': return self.getSamples(
                self.expectFromSLayer(data, source, self.weights(source)))
            elif source['class'] == 'gauss': return self.getSamples(
                self.expectFromGLayer(data, source, self.weights(source)))

            return False

        def weights(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source['W']
            elif 'target' in self.target and source['name'] == self.target['target']:
                return self.target['W'].T
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

        def links(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source
            elif 'target' in self.target and source['name'] == self.target['target']:
                return {'W': self.target['W'].T, 'A': self.target['A'].T}
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

        def adjacency(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source['A']
            elif 'target' in self.target and source['name'] == self.target['target']:
                return self.target['A'].T
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

    ####################################################################
    # Sigmoidal Unit Layer                                             #
    ####################################################################

    class UnitLayerSigmoid(UnitLayer):
        """Sigmoidal Unit Layer.

        Layer of units with sigmoidal activation function and binary distribution. """

        def initialize(self, data = None):
            """Initialize system parameters of sigmoid distributed units using data. """

            size = len(self.params['label'])
            shape = (1, size)

            self.params['bias'] = 0.5 * numpy.ones(shape)
            #self.params['bias'] = numpy.zeros(shape)

            return True

        def update(self, updates):
            """Update parameter of sigmoid units. """

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
            """Delete selection (list of ids) of units from parameter arrays. """

            layer['bias'] = layer['bias'][0, [select]]

            return True

        @staticmethod
        def check(layer):

            return 'bias' in layer

        def energy(self, data):
            """Return system energy of sigmoidal units as numpy array. """

            bias = self.params['bias']

            return - numpy.mean(data * bias, axis = 0)

        def expectFromSLayer(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a sigmoid input layer. """

            bias = self.params['bias']

            return nemoa.common.func.sigmoid(bias + numpy.dot(data, weights))

        def expectFromGLayer(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a gaussian input layer. """

            bias = self.params['bias']
            lvar = numpy.exp(source['lvar'])

            return nemoa.common.func.sigmoid(bias + numpy.dot(data / lvar, weights))

        def getParamUpdates(self, data, model, weights):
            """Return parameter updates of a sigmoidal output layer
            calculated from real data and modeled data. """

            size = len(self.params['label'])

            return {'bias': numpy.mean(data[1] - model[1], axis = 0).reshape((1, size))}

        def getUpdatesFromDelta(self, delta):

            size = len(self.params['label'])

            return {'bias': - numpy.mean(delta, axis = 0).reshape((1, size))}

        def deltaFromBPROP(self, data_in, delta_out, W_in, W_out):

            bias = self.params['bias']

            return numpy.dot(delta_out, W_out) * \
                nemoa.common.func.Dsigmoid((bias + numpy.dot(data_in, W_in)))

        @staticmethod
        def grad(x):
            """Return gradiant of standard logistic function. """

            numpy.seterr(over = 'ignore')

            return ((1.0 / (1.0 + numpy.exp(-x)))
                * (1.0 - 1.0 / (1.0 + numpy.exp(-x))))

        @staticmethod
        def getValues(data):
            """Return median of bernoulli distributed layer
            calculated from expected values. """

            return (data > 0.5).astype(float)

        @staticmethod
        def getSamples(data):
            """Return sample of bernoulli distributed layer
            calculated from expected value. """

            return (data > numpy.random.rand(
                data.shape[0], data.shape[1])).astype(float)

        def get(self, unit):

            id = self.params['label'].index(unit)
            cl = self.params['class']
            visible = self.params['visible']
            bias = self.params['bias'][0, id]

            return {'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias}

    ####################################################################
    # Gaussian Unit Layer                                              #
    ####################################################################

    class UnitLayerGauss(UnitLayer):
        """Units with linear activation function and gaussian distribution"""

        def initialize(self, data = None, vSigma = 0.4):
            """Initialize parameters of gauss distributed units. """

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
            """Update gaussian units. """

            self.params['bias'] += updates['bias']
            self.params['lvar'] += updates['lvar']

            return True

        def getParamUpdates(self, data, model, weights):
            """Return parameter updates of a gaussian output layer
            calculated from real data and modeled data. """

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

        def getUpdatesFromDelta(self, delta):
            # HINT: no update of lvar

            shape = (1, len(self.params['label']))

            return {
                'bias': - numpy.mean(delta, axis = 0).reshape(shape),
                'lvar': - numpy.zeros(shape = shape)}

        def overwrite(self, params):
            """Merge parameters of gaussian units. """

            for i, u in enumerate(params['label']):
                if u in self.params['label']:
                    l = self.params['label'].index(u)
                    self.params['bias'][0, l] = params['bias'][0, i]
                    self.params['lvar'][0, l] = params['lvar'][0, i]

            return True

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays. """

            layer['bias'] = layer['bias'][0, [select]]
            layer['lvar'] = layer['lvar'][0, [select]]

            return True

        def expectFromSLayer(self, data, source, weights):
            """Return expected values of a gaussian output layer
            calculated from a sigmoid input layer. """

            return self.params['bias'] + numpy.dot(data, weights)

        @staticmethod
        def grad(x):
            """Return gradient of activation function. """

            return 1.0

        @staticmethod
        def check(layer):

            return 'bias' in layer and 'lvar' in layer

        def energy(self, data):

            bias = self.params['bias']
            lvar = numpy.exp(self.params['lvar'])
            energy = - 0.5 * numpy.mean((data - bias) ** 2, axis = 0) / lvar

            return energy.reshape(bias.size)

        @staticmethod
        def getValues(data):
            """Return median of gauss distributed layer
            calculated from expected values."""

            return data

        def getSamples(self, data):
            """Return sample of gauss distributed layer
            calculated from expected values. """

            sigma = numpy.sqrt(numpy.exp(self.params['lvar']))

            return numpy.random.normal(data, sigma)

        def get(self, unit):

            id = self.params['label'].index(unit)

            cl = self.params['class']
            bias = self.params['bias'][0, id]
            lvar = self.params['lvar'][0, id]
            visible = self.params['visible']

            return {
                'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias, 'lvar': lvar }
