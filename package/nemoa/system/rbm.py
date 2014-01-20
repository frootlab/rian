#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# This python module contains various classes of restricted            #
# boltzmann machines aimed for data modeling and per layer pretraining #
# of multilayer feedforward artificial neuronal networks               #
########################################################################

import nemoa.system.ann, numpy

class rbm(nemoa.system.ann.ann):
    """Restricted Boltzmann Machine (RBM).

    Description:
        Restricted Boltzmann Machines are energy based undirected
        artificial neuronal networks with two layers: 'visible' and 'hidden'.
        The visible layer contains binary distributed sigmoidal units
        to model data. The hidden layer contains binary distributed
        sigmoidal units to model relations in the data.

    Reference:
        "A Practical Guide to Training Restricted Boltzmann Machines",
        Geoffrey E. Hinton, University of Toronto, 2010"""

    @staticmethod
    def default(key):
        """Return RBM default configuration as dictionary."""
        return {
            'params': {
                'samples': '*',
                'subnet': '*',
                'visible': 'auto',
                'hidden': 'auto',
                'visibleClass': 'sigmoid',
                'hiddenClass': 'sigmoid' },
            'init': {
                'checkDataset': True,
                'ignoreUnits': [],
                'wSigma': 0.5 },
            'optimize': {
                'checkDataset': True,
                'ignoreUnits': [],
                'iterations': 1,
                'minibatchSize': 100,
                'minibatchInterval': 10,
                'updates': 100000,
                'algorithm': 'CD',
                'updateSamplingSteps': 1,
                'updateSamplingIterations': 1,
                'updateRate': 0.1,
                'updateFactorWeights': 1.0,
                'updateFactorHbias': 0.1,
                'updateFactorVbias': 0.1,
                'corruptionAlgorithm': None,
                'corruptionFactor': 0.0,
                'useAdjacency': False,
                'inspect': True,
                'inspectFunction': 'performance',
                'inspectTimeInterval': 10.0 ,
                'estimateTime': True,
                'estimateTimeWait': 20.0 }}[key]

    # DATA

    # DATA EVALUATION

    def getMapping(self):
        v = self._params['units'][0]['name']
        h = self._params['units'][1]['name']
        return (v, h, v)

    def _checkDataset(self, dataset):
        """Check if dataset contains binary values."""
        if not self._isDatasetBinary(dataset):
            nemoa.log('error', """
                dataset \'%s\' is not valid:
                RBMs need binary data!""" % (dataset.getName()))
            return False
        return True

    def _getDataEvalEnergy(self, data, **kwargs):
        """Return system energy respective to data."""
        vEnergy = self.getUnitEnergy(data, ('visible',))
        hEnergy = self.getUnitEnergy(data, ('visible', 'hidden'))
        lEnergy = self._getLinkEvalEnergy(data)
        return numpy.sum(vEnergy) \
            + numpy.sum(hEnergy) \
            + numpy.sum(lEnergy)

    @staticmethod
    def _getUnitsFromNetwork(network):
        """Return tuple with lists of unit labels from network."""
        return [{
            'label': network.nodes(visible = True),
            'visible': True,
            'name': 'visible'
        }, {
            'label': network.nodes(visible = False),
            'visible': False,
            'name': 'hidden'
        }]

    # DATA TRANSFORMATION

    def _compress(self, data, **kwargs):
        """Return expectation values of hidden units."""
        return self.getUnitExpect(data, ('visible', 'hidden'))

    def mapData(self, data, transformation = 'visiblevalue', **kwargs):
        """Return system representation of data."""
        if transformation == 'visibleexpect': return self.getUnitExpect(
            data, ('visible', 'hidden', 'visible'))
        if transformation == 'visiblevalue': return self.getUnitValues(
            data, ('visible', 'hidden', 'visible'))
        if transformation == 'visiblesample': return self.getUnitSamples(
            data, ('visible', 'hidden', 'visible'))
        if transformation == 'hiddenexpect': return self.getUnitExpect(
            data, ('visible', 'hidden'))
        if transformation == 'hiddenvalue': return self.getUnitValues(
            data, ('visible', 'hidden'))
        if transformation == 'hiddensample': return self.getUnitSamples(
            data, ('visible', 'hidden'))
        return data

    def _getDataContrastiveDivergency(self, data):
        """Return reconstructed data using 1-step contrastive divergency sampling (CD-1)."""
        hData  = self.getUnitExpect(data, ('visible', 'hidden'))
        vModel = self.getUnitSamples(hData, ('hidden', 'visible'),
            expectLast = True)
        hModel = self.getUnitExpect(vModel, ('visible', 'hidden'))
        return data, hData, vModel, hModel

    def _getDataContrastiveDivergencyKstep(self, data, k = 1, m = 1):
        """Return mean value of reconstructed data using k-step contrastive divergency sampling (CD-k).
        
        Options:
            k: number of full Gibbs sampling steps
            m: number if iterations to calculate mean values
        """
        hData  = self.getUnitExpect(data, ('visible', 'hidden'))
        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in range(m):
            for j in range(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0:
                    hSample = self.getUnitSamples(hData, ('hidden', ))
                else:
                    hSample = self.getUnitSamples(hExpect, ('hidden', ))

                # calculate vExpect from hSample
                vExpect = self.getUnitExpect(hSample,
                    ('hidden', 'visible'))

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k:
                    hExpect = self.getUnitExpect(vExpect,
                        ('visible', 'hidden'))
                else:
                    hExpect = self.getUnitSamples(vExpect,
                        ('visible', 'hidden'), expectLast = True)

            vModel += vExpect / m
            hModel += hExpect / m
        return data, hData, vModel, hModel

    # RBM PARAMETER METHODS

    def _setUpdateRates(self, **config):
        """Initialize updates for system parameters."""
        if not 'optimize' in self._config: self._config['optimize'] = {}
        return (self._setVisibleUnitUpdateRates(**config)
            and self._setHiddenUnitUpdateRates(**config)
            and self._setLinkUpdateRates(**config))

    def _setParams(self, params):
        """Set system parameters from dictionary."""
        return (self._setVisibleUnitParams(params)
            and self._setHiddenUnitParams(params)
            and self._setLinkParams(params))

    def _getParams(self):
        """Return dictionary with all parameters."""
        return self._params.copy()

    def _optimizeParams(self, dataset, schedule):
        """Optimize system parameters."""

        config = self._config['optimize']
        init = self._config['init']

        # check dataset
        if (not 'checkDataset' in init
            or init['checkDataset'] == True) \
            and not self._checkDataset(dataset): return False

        # initialise inspector
        if config['inspect']:
            inspector = nemoa.system.base.inspector(self)
            testData = dataset.getData()
            inspector.setTestData(data = (testData, testData))

        # for each update step (epoch)
        for epoch in xrange(config['updates']):

            # get data (sample from minibatches)
            if epoch % config['minibatchInterval'] == 0:
                data = dataset.getData(config['minibatchSize'])

            # get system estimations (model)
            if config['algorithm'] == 'CD': sampleData = \
                self._getDataContrastiveDivergency(data)
            elif config['algorithm'] == 'CDk': sampleData = \
                self._getDataContrastiveDivergencyKstep(data,
                    k = config['updateSamplingSteps'],
                    m = config['updateSamplingIterations'])
            else: return nemoa.log('error', """could not optimize model:
                unknown optimization algorithm '%s'""" % (config['algorithm']))

            # update system params
            self._updateParams(*sampleData)
            
            # inspect
            inspector.trigger()

        return True

    def _updateParams(self, *args, **kwargs):
        """Update system parameters using reconstructed and sampling data."""

        # first calculate all updates (without affecting the calculations)
        if not 'visible' in self._config['optimize']['ignoreUnits']:
            updateVisibleUnits = self._getVisibleUnitUpdates(*args, **kwargs)
        if not 'hidden' in self._config['optimize']['ignoreUnits']:
            updateHiddenUnits = self._getHiddenUnitUpdates(*args, **kwargs)
        updateLinks = self._getLinkUpdates(*args, **kwargs)

        # and then update all unit and link parameters
        if not 'visible' in self._config['optimize']['ignoreUnits']:
            self.units['visible'].update(updateVisibleUnits)
        if not 'hidden' in self._config['optimize']['ignoreUnits']:
            self.units['hidden'].update(updateHiddenUnits)
        self._updateLinks(**updateLinks)
        return True

    # UNITS

    def _getUnitsFromConfig(self):
        """Return tuple with unit information created from config."""

        if isinstance(self._config['params']['visible'], int):
            vLabel = ['v:v%i' % (num) for num \
                in range(1, self._config['params']['visible'] + 1)]
        elif isinstance(self._config['params']['visible'], list):
            for node in self._config['params']['visible']:
                if not isinstance(node, str):
                    return None
            vLabel = self._config['params']['visible']
        else:
            vLabel = []
        if isinstance(self._config['params']['hidden'], int):
            hLabel = ['h:h%i' % (num) for num \
                in range(1, self._config['params']['hidden'] + 1)]
        elif isinstance(self._config['params']['hidden'], list):
            for node in self._config['params']['hidden']:
                if not isinstance(node, str):
                    return None
            hLabel = self._config['params']['hidden']
        else:
            hLabel = []

        return [{
            'id': 0,
            'name': 'visible',
            'visible': True,
            'label': vLabel,
        }, {
            'id': 1,
            'name': 'hidden',
            'visible': False,
            'label': hLabel
        }]

    def _getUnitsFromDataset(self, dataset):
        """Return tuple with lists of unit labels ([visible], [hidden]) using dataset for visible."""
        return (dataset.getColLabels(), self.units['hidden'].params['label'])

    def _getUnitEval(self, data, func = 'performance', info = False, **kwargs):
        """Return unit evaluation."""
        evalFuncs = {
            'energy': ['local energy', 'Energy'],
            'expect': ['expectation values', 'Expect'],
            'error': ['reconstruction error', 'Error'],
            'performance': ['performance', 'Performance'],
            'intperformance': ['self performance', 'IntPerformance'],
            'extperformance': ['foreign performance', 'ExtPerformance'],
            'relperformance': ['relative performance', 'RelativePerformance'],
            'relintperformance': ['relative self performance', 'RelativeIntPerformance'],
            'relextperformance': ['relative foreign performance', 'RelativeExtPerformance'] }
        if info:
            if not func in evalFuncs:
                return False
            return {
                'name': evalFuncs[func][0]}
        if not func in evalFuncs:
            nemoa.log("warning", """
                could not evaluate units:
                unknown unit evaluation function '%s'
                """ % (func))
            return False

        visibleUnitEval, hiddenUnitEval = eval(
            'self._getUnitEval' + evalFuncs[func][1] + '(data, **kwargs)')
        evalDict = {}
        if isinstance(visibleUnitEval, numpy.ndarray):
            for i, v in enumerate(self.units['visible'].params['label']):
                evalDict[v] = visibleUnitEval[i]
        if isinstance(hiddenUnitEval, numpy.ndarray):
            for j, h in enumerate(self.units['hidden'].params['label']):
                evalDict[h] = hiddenUnitEval[j]
        return evalDict

    def _getUnitEvalEnergy(self, data, **kwargs):
        """Return local energy of units."""
        return (self.getUnitEnergy(data, ('visible',)),
            self.getUnitEnergy(data, ('visible', 'hidden')))

    def _getUnitEvalError(self, data, block = [], k = 1, **kwargs):
        """Return euclidean reconstruction error of units.
        
        error := ||data - model||
        """
        return self.getUnitError(data, data,
            ('visible', 'hidden', 'visible'), block), None

    def _getUnitEvalIntPerformance(self, data, k = 1, **kwargs):
        """Return 'intrinsic performance' of units.

        'intrinsic performance' := relperf
            where model(v) is generated with: data(u not v) = mean(data(u))
        """
        vSize = len(self.units['visible'].params['label'])
        relIntApprox = numpy.empty(vSize)
        for v in range(vSize):
            block = range(vSize)
            block.pop(v)
            relIntApprox[v] = self._getUnitEvalPerformance(
                data, block = block, k = k)[0][v]
        return relIntApprox, None

    def _getUnitEvalExtPerformance(self, data, block = [], k = 1, **kwargs):
        """Return 'extrinsic performance' of units.
        
        'extrinsic performance' := relApprox
            where model(v) is generated with data(v) = mean(data(v))
        """
        relExtApprox = numpy.empty(len(self.units['visible'].params['label']))
        for v in range(len(self.units['visible'].params['label'])):
            relExtApprox[v] = self._getUnitEvalPerformance(
                data, block = block + [v], k = k)[0][v]
        return relExtApprox, None

    def _getUnitEvalRelativePerformance(self, data, **kwargs):
        """Return 'performance' of units.
        
        'performance' := 1 - error / ||data - mean(data)||
        """
        vErr = self._getUnitEvalError(data = data, **kwargs)[0]
        vNorm = numpy.sqrt(((data - numpy.mean(data, axis = 0)) ** 2).sum(axis = 0))
        return 1 - vErr  / vNorm, None

    def _getUnitEvalRelativeIntPerformance(self, data, k = 1, **kwargs):
        """Return 'intrinsic relative performance' of units
        
        'intrinsic relative performance' := relperf
            where model(v) is generated with data(u not v) = mean(data(u))
        """
        vSize = len(self.units['visible'].params['label'])
        relIntApprox = numpy.empty(vSize)
        for v in range(vSize):
            block = range(vSize)
            block.pop(v)
            relIntApprox[v] = self._getUnitEvalRelativePerformance(
                data = data, block = block, k = k)[0][v]
        return relIntApprox, None

    def _getUnitEvalRelativeExtPerfomance(self, data, block = [], k = 1, **kwargs):
        """Return "performance (extrinsic)" of units.

        extrelperf := relApprox where model(v) is generated with data(v) = mean(data(v))
        """
        relExtApprox = numpy.empty(len(self.units['visible'].params['label']))
        for v in range(len(self.units['visible'].params['label'])):
            relExtApprox[v] = self._getUnitEvalRelativePerformance(
                data = data, block = block + [v], k = k)[0][v]
        return relExtApprox, None

    def _unlinkUnit(self, unit):
        """Delete unit links in adjacency matrix."""
        if unit in self.units['visible'].params['label']:
            i = self.units['visible'].params['label'].index(unit)
            self._params['links'][(0, 1)]['A'][i,:] = False
            return True
        if unit in self.units['hidden'].params['label']:
            i = self.units['hidden'].params['label'].index(unit)
            self._params['links'][(0, 1)]['A'][:,i] = False
            return True
        return False

    # RBM VISIBLE UNIT METHODS

    def _getVisibleUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        v = len(self.units['visible'].params['label'])
        return { 'bias': (numpy.mean(vData - vModel, axis = 0).reshape((1, v))
            * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorVbias']) }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])

    # RBM HIDDEN UNIT METHODS

    def _getHiddenUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        return { 'bias': (
            numpy.mean(hData - hModel, axis = 0).reshape((1, len(self.units['hidden'].params['label'])))
            * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorHbias']) }

    def _setHiddenUnitParams(self, params):
        """Set parameters of hidden units using dictionary."""
        return self.units['hidden'].overwrite(params['units'][1])

    # RBM LINK METHODS

    def _getLinksFromConfig(self):
        """Return links from adjacency matrix."""
        links = []
        for i, v in enumerate(self.units['visible'].params['label']):
            for j, h in enumerate(self.units['hidden'].params['label']):
                if not 'A' in self._params or self._params['links'][(0, 1)]['A'][i, j]:
                    links.append((v, h))
        return links

    def _getLinksFromNetwork(self, network):
        """Return links from network instance."""
        return network.edges()

    def _setLinks(self, links = []):
        """Set links and create link adjacency matrix."""
        if not self._checkUnitParams(self._params):
            nemoa.log('error', """
                could not set links:
                units have not yet been set yet!
                """)
            return False

        # create adjacency matrix from links
        vList = self.units['visible'].params['label']
        hList = self.units['hidden'].params['label']
        A = numpy.empty([len(vList), len(hList)], dtype = bool)

        # 2DO!! This is very slow: we could try "for link in links" etc.
        for i, v in enumerate(vList):
            for j, h in enumerate(hList):
                A[i, j] = ((v, h) in links or (h, v) in links)

        # update link adjacency matrix
        if not 'links' in self._params:
            self._params['links'] = {}
        if not (0, 1) in self._params['links']:
            self._params['links'][(0, 1)] = {}
        self._params['links'][(0, 1)]['A'] = A
        self._params['links'][(0, 1)]['source'] = 'visible'
        self._params['links'][(0, 1)]['target'] = 'hidden'

        # reset link update
        return True

    def _getLinkParams(self, links = []):
        """Return link parameters."""
        if not links:
            links = self._getLinksFromConfig()

        # create dict with link params
        vList = self.units['visible'].params['label']
        hList = self.units['hidden'].params['label']
        linkParams = {}
        for link in links:
            if link[0] in vList and link[1] in hList:
                i = vList.index(link[0])
                j = hList.index(link[1])
                linkParams[link] = {
                    'A': self._params['links'][(0, 1)]['A'][i, j],
                    'W': self._params['links'][(0, 1)]['W'][i, j] }
            elif link[1] in vList and link[0] in hList:
                i = hList.index(link[0])
                j = vList.index(link[1])
                linkParams[link] = {
                    'A': self._params['links'][(0, 1)]['A'][i, j],
                    'W': self._params['links'][(0, 1)]['W'][i, j] }
            else:
                nemoa.log('warning', """
                    could not get parameters for link (%s → %s):
                    link could not be found!""" % (link[0], link[1]))
                continue
        return linkParams

    def _setLinkParams(self, params):
        """Set link parameters and update link matrices using dictionary."""
        for i, v in enumerate(self.units['visible'].params['label']):
            if not v in params['units'][0]['label']:
                continue
            k = params['units'][0]['label'].index(v)
            for j, h in enumerate(self.units['hidden'].params['label']):
                if not h in params['units'][1]['label']:
                    continue
                l = params['units'][1]['label'].index(h)
                self._params['links'][(0, 1)]['A'][i, j] = params['A'][k, l]
                self._params['links'][(0, 1)]['W'][i, j] = params['W'][k, l]
        return True

    def _removeLinks(self, links = []):
        """Remove links from adjacency matrix using list of links."""
        if not self._checkParams(self._params): # check params
            nemoa.log("error", """
                could not remove links:
                units have not been set yet!""")
            return False

        # search links and update list of current links
        curLinks = self._getLinksFromConfig() # get current links
        for link in links:
            found = False
            if (link[0], link[1]) in curLinks:
                del curLinks[curLinks.index((link[0], link[1]))]
                found = True
            if (link[1], link[0]) in curLinks:
                del curLinks[curLinks.index((link[1], link[0]))]
                found = True
            if not found:
                nemoa.log("warning", """
                    could not delete link (%s → %s):
                    link could not be found!
                    """ % (link[0], link[1]))
                continue

        # set modified list of current links
        return self._setLinks(curLinks)

    def _getLinkEval(self, data, func = 'energy', info = False, **kwargs):
        """Return link evaluation values."""
        evalFuncs = {
            'energy': ['local energy', 'Energy'],
            'adjacency': ['link adjacency', 'Adjacency'],
            'weight': ['link weight', 'Weight'] }
        if info:
            if not func in evalFuncs:
                return False
            return {
                'name': evalFuncs[func][0]}
        if not func in evalFuncs:
            nemoa.log("warning", """
                could not evaluate units:
                unknown link evaluation function '%s'
                """ % (func))
            return False

        linkEval = eval('self._getLinkEval' + evalFuncs[func][1] \
            + '(data, **kwargs)')
        evalDict = {}
        if isinstance(linkEval, numpy.ndarray):
            for i, v in enumerate(self.units['visible'].params['label']):
                for j, h in enumerate(self.units['hidden'].params['label']):
                    evalDict[(v,h)] = linkEval[i, j]
        return evalDict

    def _getLinkEvalWeight(self, data, **kwargs):
        """Return link weights of all links as numpy array."""
        return self._params['links'][(0, 1)]['W']

    def _getLinkEvalAdjacency(self, data, **kwargs):
        """Return link adjacency of all links as numpy array."""
        return self._params['links'][(0, 1)]['A']

    def _getLinkEvalEnergy(self, data):
        """Return link energy of all links as numpy array."""
        hData = self.units['hidden'].getValues(self.getUnitExpect(data, ('visible', 'hidden')))

        if self._config['optimize']['useAdjacency']:
            return -(self._params['links'][(0, 1)]['A'] * self._params['links'][(0, 1)]['W']
                * numpy.dot(data.T, hData) / data.shape[0])
        return -(self._params['links'][(0, 1)]['W'] * numpy.dot(data.T, hData) / data.shape[0])

    def _getLinkUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for links."""
        return { 'W': (numpy.dot(vData.T, hData) - numpy.dot(vModel.T, hModel))
            / float(vData.size) * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorWeights']}

    def _updateLinks(self, **updates):
        """Set updates for links."""
        self._params['links'][(0, 1)]['W'] += updates['W']
        return True

class grbm(rbm):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Description:
        Gaussian Restricted Boltzmann Machines are energy based undirected
        artificial neuronal networks with two layers: 'visible' and 'hidden'.
        The visible layer contains gauss distributed sigmoidal units
        to model data. The hidden layer contains binary distributed
        sigmoidal units to model relations in the data.

    Reference:
        "Improved Learning of Gaussian-Bernoulli Restricted Boltzmann Machines",
        KyungHyun Cho, Alexander Ilin and Tapani Raiko, ICANN 2011"""

    @staticmethod
    def default(key):
        """Return GRBM default configuration as dictionary."""
        return {
            'params': {
                'samples': '*',
                'subnet': '*',
                'visible': 'sigmoid',
                'hidden': 'sigmoid',
                'visibleClass': 'gauss',
                'hiddenClass': 'sigmoid' },
            'init': {
                'checkDataset': True,
                'ignoreUnits': [],
                'wSigma': 0.5 },
            'optimize': {
                'checkDataset': True,
                'ignoreUnits': [],
                'iterations': 1,
                'updates': 100000,
                'algorithm': 'CD',
                'updateSamplingSteps': 1,
                'updateSamplingIterations': 1,
                'updateRate': 0.01,
                'updateFactorWeights': 1.0,
                'updateFactorHbias': 0.1,
                'updateFactorVbias': 0.1,
                'updateFactorVlvar': 0.01,
                'minibatchSize': 100,
                'minibatchInterval': 10,
                'corruptionAlgorithm': None,
                'corruptionFactor': 0.0,
                'useAdjacency': False,
                'inspect': True,
                'inspectFunction': 'performance',
                'inspectTimeInterval': 20.0 ,
                'estimateTime': True,
                'estimateTimeWait': 20.0 }}[key]

    # GRBM data

    def _checkDataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        return self._isDatasetGaussNormalized(dataset)

    def _updateParams(self, *args, **kwargs):
        """Update system parameters using reconstructed and sampling data."""

        # first calculate all updates (without affecting the calculations)
        if not 'visible' in self._config['optimize']['ignoreUnits']:
            updateVisibleUnits = self._getVisibleUnitUpdates(*args, **kwargs)
        if not 'hidden' in self._config['optimize']['ignoreUnits']:
            updateHiddenUnits = self._getHiddenUnitUpdates(*args, **kwargs)
        updateLinks = self._getLinkUpdates(*args, **kwargs)

        # and then update all unit and link parameters
        if not 'visible' in self._config['optimize']['ignoreUnits']:
            self.units['visible'].update(updateVisibleUnits)
            #self.gaussUnits.update(self.units['visible'].params, updateVisibleUnits)
        if not 'hidden' in self._config['optimize']['ignoreUnits']:
            self.units['hidden'].update(updateHiddenUnits)
            #self.sigmoidUnits.update(self.units['hidden'].params, updateHiddenUnits)
        self._updateLinks(**updateLinks)
        return True

    # GRBM visible units

    def _getVisibleUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        v = len(self.units['visible'].params['label'])
        W = self._params['links'][(0, 1)]['W']
        vVar = numpy.exp(self.units['visible'].params['lvar'])
        vBias = self.units['visible'].params['bias']
        return {
            'bias': (numpy.mean(vData - vModel, axis = 0).reshape((1, v))
                / vVar * self._config['optimize']['updateRate']
                * self._config['optimize']['updateFactorVbias']),
            'lvar': ((numpy.mean(0.5 * (vData - vBias) ** 2 - vData
                * numpy.dot(hData, W.T), axis = 0) - numpy.mean(0.5
                * (vModel - vBias) ** 2 - vModel
                * numpy.dot(hModel, W.T), axis = 0)).reshape((1, v))
                / vVar * self._config['optimize']['updateRate']
                * self._config['optimize']['updateFactorVlvar']) }

    def _getVisibleUnitParams(self, label):
        """Return system parameters of one specific visible unit."""
        id = self.units['visible'].params['label'].index(label)
        return {
            'bias': self.units['visible'].params['bias'][0, id],
            'sdev': numpy.sqrt(numpy.exp(self.units['visible'].params['lvar'][0, id])) }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])

    # GRBM links

    def _getLinkEvalEnergy(self, data):
        """Return link energy of all links as numpy array."""
        hData = self.getUnitExpect(data, ('visible', 'hidden'))
        if self._config['optimize']['useAdjacency']:
            return -(self._params['links'][(0, 1)]['A']
                * self._params['links'][(0, 1)]['W'] * numpy.dot((data
                / numpy.exp(self.units['visible'].params['lvar'])).T, hData)
                / data.shape[0])
        return -(self._params['links'][(0, 1)]['W'] * numpy.dot((data
            / numpy.exp(self.units['visible'].params['lvar'])).T, hData)
            / data.shape[0])

    def _getLinkUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for links."""
        vVar = numpy.exp(self.units['visible'].params['lvar'])
        return { 'W': ((numpy.dot(vData.T, hData)
            - numpy.dot(vModel.T, hModel))
            / float(vData.size) * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorWeights']) / vVar.T}
