#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# This python module contains various classes of restricted            #
# boltzmann machines aimed for data modeling and per layer pretraining #
# of multilayer feedforward artificial neural networks                 #
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
    def _default(key): return {
        'params': {
            'samples': '*',
            'subnet': '*',
            'visible': 'auto',
            'hidden': 'auto',
            'visibleClass': 'sigmoid',
            'hiddenClass': 'sigmoid' },
        'init': {
            'checkDataset': False,
            'ignoreUnits': [],
            'wSigma': 0.5 },
        'optimize': {
            'checkDataset': False,
            'ignoreUnits': [],
            'iterations': 1,
            'minibatchSize': 100,
            'minibatchInterval': 10,
            'updates': 100000,
            'algorithm': 'vrcd',
            'updateCdkSteps': 1,
            'updateCdkIterations': 1,
            'updateRate': 0.1,
            'updateFactorWeights': 1.0,
            'updateFactorHbias': 0.1,
            'updateFactorVbias': 0.1,
            'sparsityRate': 0.0,
            'sparsityExpect': 0.5,
            'selectivityFactor': 0.0,
            'selectivitySize': 0.5,
            'corruptionType': None,
            'corruptionFactor': 0.5,
            'useAdjacency': False,
            'inspect': True,
            'inspectFunction': 'accuracy',
            'inspectTimeInterval': 10.0 ,
            'estimateTime': True,
            'estimateTimeWait': 20.0 }}[key]

    # DATA

    # DATA EVALUATION

    def getMapping(self):
        v = self._params['units'][0]['name']
        h = self._params['units'][1]['name']
        return (v, h, v)

    def _getTestData(self, dataset):
        """Return tuple with default test data."""
        data = dataset.getData()
        return (data, data)

    def _checkDataset(self, dataset):
        """Check if dataset contains binary values."""
        if not self._isDatasetBinary(dataset):
            nemoa.log('error', """
                dataset \'%s\' is not valid:
                RBMs need binary data!""" % (dataset.name()))
            return False
        return True

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

    def _optParams(self, dataset, schedule, inspector):
        """Optimize system parameters."""

        cfg = self._config['optimize']
        algorithm = cfg['algorithm'].lower()

        if cfg['sparsityRate'] > 0.0: nemoa.log('note', """
            using l1-norm penalty term for sparse coding
            with expectation value %.2f""" % (cfg['sparsityExpect']))
        if cfg['selectivityFactor'] > 0.0: nemoa.log('note', """
            using l2-norm penalty term for selective coding
            with expectation value %.2f""" % (cfg['selectivitySize']))
        if isinstance(cfg['corruptionType'], str) \
            and not cfg['corruptionType'].lower() == 'none': nemoa.log(
            'note', """using data corruption for denoising with
            noise model '%s (%.2f)'""" % (
            cfg['corruptionType'], cfg['corruptionFactor']))

        if algorithm == 'cd':
            return self.optimizeCd(dataset, schedule, inspector)
        elif algorithm == 'cdk':
            return self.optimizeCdk(dataset, schedule, inspector)
        elif algorithm == 'vrcd':
            return self.optimizeVrcd(dataset, schedule, inspector)
        elif algorithm == 'vrcdk':
            return self.optimizeVrcdk(dataset, schedule, inspector)
        return nemoa.log('error', """could not optimize model:
            unknown optimization algorithm '%s'""" % (algorithm))

    def optimizeCdk(self, dataset, schedule, inspector):
        """Optimize system parameters."""

        cfg  = self._config['optimize']
        corr = (cfg['corruptionType'], cfg['corruptionFactor'])
        size = cfg['minibatchSize']
        k = cfg['updateCdkSteps']
        m = cfg['updateCdkIterations']

        # for each update step (epoch)
        for epoch in xrange(cfg['updates']):

            # get data (sample from minibatches)
            if epoch % cfg['minibatchInterval'] == 0: data = \
                dataset.getData(size = size, corruption = corr)
            # get system estimations (model)
            dTuple = self.getCdkSamples(data)
            # Update system params
            self._updateParams(*dTuple)
            # Trigger inspector (getch, calc inspect function etc)
            event = inspector.trigger()
            if event:
                if event == 'abort': break

        return True

    def optimizeCd(self, dataset, schedule, inspector):
        """Optimize system parameters."""

        cfg  = self._config['optimize']
        corr = (cfg['corruptionType'], cfg['corruptionFactor'])
        size = cfg['minibatchSize']

        # for each update step (epoch)
        for epoch in xrange(cfg['updates']):

            # get data (sample from minibatches)
            if epoch % cfg['minibatchInterval'] == 0: data = \
                dataset.getData(size = size, corruption = corr)
            # get system estimations (model)
            dTuple = self.getCdSamples(data)
            # Update system params
            self._updateParams(*dTuple)
            # Trigger inspector (getch, calc inspect function etc)
            event = inspector.trigger()
            if event:
                if event == 'abort': break

        return True

    def optimizeVrcd(self, dataset, schedule, inspector):
        """Optimize parameters using variance resiliant constrastive divergency."""

        cfg  = self._config['optimize']
        corr = (cfg['corruptionType'], cfg['corruptionFactor'])
        size = cfg['minibatchSize']

        # initialise store with weight variance
        wVar = numpy.array([numpy.var(
            self._params['links'][(0, 1)]['W'])])
        inspector.writeToStore(wVar = wVar)

        lenght = cfg['updateVrcdLenght']
        A = numpy.array([numpy.arange(0, lenght), numpy.ones(lenght)])

        # initialise update rate
        cfg['updateRate'] = cfg['updateVrcdInitRate']

        # for each update step (epoch)
        for epoch in xrange(cfg['updates']):

            # get data (sample from minibatches)
            if epoch % cfg['minibatchInterval'] == 0: data = \
                dataset.getData(size = size, corruption = corr)

            # get system estimations (model)
            dTuple = self.getCdSamples(data)

            # adapt update rate
            if epoch % cfg['updateVrcdInterval'] == 0 \
                and epoch > cfg['updateVrcdWait']:
                wVar = numpy.append([numpy.var(
                    self._params['links'][(0, 1)]['W'])],
                    inspector.readFromStore()['wVar'])
                if wVar.shape[0] > lenght:
                    wVar = wVar[:lenght]
                    grad = - numpy.linalg.lstsq(A.T, wVar)[0][0]
                    delw = cfg['updateVrcdFactor'] * grad
                    rMin = cfg['updateVrcdMin']
                    rMax = cfg['updateVrcdMax']

                    cfg['updateRate'] = min(max(delw, rMin), rMax)

                inspector.writeToStore(wVar = wVar)

            # Update system params
            self._updateParams(*dTuple)

            # Trigger inspector (getch, calc inspect function etc)
            event = inspector.trigger()
            if event:
                if event == 'abort': break

        return True

    def optimizeVrcdk(self, dataset, schedule, inspector):
        """Optimize parameters using variance resiliant constrastive divergency."""

        cfg  = self._config['optimize']
        corr = (cfg['corruptionType'], cfg['corruptionFactor'])
        size = cfg['minibatchSize']

        k = cfg['updateCdkSteps']
        m = cfg['updateCdkIterations']

        # initialise store with weight variance
        wVar = numpy.array([numpy.var(
            self._params['links'][(0, 1)]['W'])])
        inspector.writeToStore(wVar = wVar)

        lenght = cfg['updateVrcdLenght']
        A = numpy.array([numpy.arange(0, lenght), numpy.ones(lenght)])

        # initialise update rate
        cfg['updateRate'] = cfg['updateVrcdInitRate']

        # for each update step (epoch)
        for epoch in xrange(cfg['updates']):

            # get data (sample from minibatches)
            if epoch % cfg['minibatchInterval'] == 0: data = \
                dataset.getData(size = size, corruption = corr)

            # get system estimations (model)
            dTuple = self.getCdkSamples(data)

            # adapt update rate
            if epoch % cfg['updateVrcdInterval'] == 0 \
                and epoch > cfg['updateVrcdWait'] - lenght:
                wVar = numpy.append([numpy.var(
                    self._params['links'][(0, 1)]['W'])],
                    inspector.readFromStore()['wVar'])
                if wVar.shape[0] > lenght:
                    wVar = wVar[:lenght]
                    grad = numpy.linalg.lstsq(A.T, wVar)[0][0]
                    delw = cfg['updateVrcdFactor'] * numpy.abs(grad)
                    cfg['updateRate'] = numpy.max(delw, cfg['updateVrcdMin'])

                inspector.writeToStore(wVar = wVar)

            # Update system params
            self._updateParams(*dTuple)

            # Trigger inspector (getch, calc inspect function etc)
            event = inspector.trigger()
            if event:
                if event == 'abort': break

        return True

    def optimizeRcdk(self, dataset, schedule, inspector):
        """Optimize parameters using resiliant k step constrastive divergency."""

        cfg  = self._config['optimize']
        corr = (cfg['corruptionType'], cfg['corruptionFactor'])
        size = cfg['minibatchSize']

        k = cfg['updateCdkSteps']
        m = cfg['updateCdkIterations']

        # initialise store with weight variance
        W = self._params['links'][(0, 1)]['W']
        wVar = numpy.array([numpy.var(W)])
        inspector.writeToStore(wVar = wVar)

        lenght = cfg['updateVrcdLenght']
        A = numpy.array([numpy.arange(0, lenght), numpy.ones(lenght)])

        # initialise update rate
        cfg['updateRate'] = cfg['updateVrcdInitRate']

        # for each update step (epoch)
        for epoch in xrange(cfg['updates']):

            # get data (sample from minibatches)
            if epoch % cfg['minibatchInterval'] == 0: data = \
                dataset.getData(size = size, corruption = corr)

            # get system estimations (model)
            dTuple = self.getCdkSamples(data)

            # adapt update rate
            if epoch % cfg['updateVrcdInterval'] == 0 \
                and epoch > cfg['updateVrcdWait'] - lenght:
                wVar = numpy.append([numpy.var(
                    self._params['links'][(0, 1)]['W'])],
                    inspector.readFromStore()['wVar'])
                if wVar.shape[0] > lenght:
                    wVar = wVar[:lenght]
                    grad = numpy.linalg.lstsq(A.T, wVar)[0][0]
                    delw = cfg['updateVrcdFactor'] * numpy.abs(grad)
                    cfg['updateRate'] = numpy.max(delw, cfg['updateVrcdMin'])

                inspector.writeToStore(wVar = wVar)

            # Update system params
            self._updateParams(*dTuple)

            # Trigger inspector (getch, calc inspect function etc)
            event = inspector.trigger()
            if event:
                if event == 'abort': break

        return True

    ####################################################################
    # Contrastive Divergency                                           #
    ####################################################################

    def getCdSamples(self, data):
        """Return reconstructed data using 1-step contrastive divergency sampling (CD-1)."""
        hData  = self.evalUnitExpect(data, ('visible', 'hidden'))
        vModel = self.evalUnitSamples(hData, ('hidden', 'visible'),
            expectLast = True)
        hModel = self.evalUnitExpect(vModel, ('visible', 'hidden'))
        return data, hData, vModel, hModel

    def getCdkSamples(self, data):
        """Return mean value of reconstructed data using k-step contrastive divergency sampling (CD-k).

        Options:
            k: number of full Gibbs sampling steps
            m: number if iterations to calculate mean values """

        cfg = self._config['optimize']

        k = cfg['updateCdkSteps']
        m = cfg['updateCdkIterations']

        hData  = self.getUnitExpect(data, ('visible', 'hidden'))
        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in range(m):
            for j in range(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0: hSample = self.evalUnitSamples(hData, ('hidden', ))
                else: hSample = self.evalUnitSamples(hExpect, ('hidden', ))

                # calculate vExpect from hSample
                vExpect = self.evalUnitExpect(hSample, ('hidden', 'visible'))

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k: hExpect = self.evalUnitExpect(vExpect, ('visible', 'hidden'))
                else: hExpect = self.evalUnitSamples(vExpect, ('visible', 'hidden'), expectLast = True)

            vModel += vExpect / m
            hModel += hExpect / m

        return data, hData, vModel, hModel

    def _updateParams(self, *dTuple):
        """Update system parameters using reconstructed and sampling data."""

        cfg = self._config['optimize']
        ignore = cfg['ignoreUnits']

        # calculate updates (without affecting the calculations)
        if not 'visible' in ignore: deltaV = self._getUpdateCdVisible(*dTuple)
        if not 'hidden' in ignore: deltaH = self._getUpdateCdHidden(*dTuple)
        if not 'links' in ignore: deltaL = self._getUpdateCdLinks(*dTuple)

        # update parameters
        if not 'visible' in ignore: self.units['visible'].update(deltaV)
        if not 'hidden' in ignore: self.units['hidden'].update(deltaH)
        if not 'links' in ignore: self._updateLinks(**deltaL)

        # calculate sparsity, and selectivity updates
        if cfg['sparsityRate'] > 0.0:
            if not 'hidden' in ignore: self.units['hidden'].update(
                self._getUpdateKlHidden(*dTuple))
        if cfg['selectivityFactor'] > 0.0:
            if not 'hidden' in ignore: self.units['hidden'].update(
                self._getUpdateKlHidden(*dTuple))

        return True

    def _getUpdateCdVisible(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for visible units.

        Description:
            constrastive divergency gradient of hidden units parameters """

        cfg = self._config['optimize']

        r = cfg['updateRate'] * cfg['updateFactorVbias'] # update rate
        v = len(self.units['visible'].params['label'])
        diff = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return { 'bias': r * diff }

    def _getUpdateCdHidden(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for hidden units.

        Description:
            constrastive divergency gradient of hidden units parameters """

        cfg = self._config['optimize']

        h = len(self.units['hidden'].params['label'])
        r = cfg['updateRate'] * cfg['updateFactorHbias'] # update rate
        diff = numpy.mean(hData - hModel, axis = 0).reshape((1, h))

        return { 'bias': r * diff }

    def _getUpdateCdLinks(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for links.

        Description:
            constrastive divergency gradient of link parameters """

        cfg = self._config['optimize']

        r = cfg['updateRate'] * cfg['updateFactorWeights'] # update rate
        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)

        return { 'W': r * (D - M) }

    def _getUpdateKlHidden(self, vData, hData, vModel, hModel):
        """Return sparsity updates for hidden units.

        Description:
            Kullback-Leibler penalty (cross entropy) gradient
            of hidden unit parameters. """

        cfg = self._config['optimize']

        p = cfg['sparsityExpect'] # target expectation value for units
        q = numpy.mean(hData, axis = 0) # expectation value (over samples)
        r = cfg['sparsityRate'] # update rate

        #units = (self.getUnits()[0], self.getUnits()[0])
        #data  = (vData, vData)

        #p = 0.1 + numpy.array(numpy.zeros(q.shape[0])).reshape(q.shape)
        #p = 0.5 * numpy.array(range(q.shape[0])).reshape(q.shape) / float(q.shape[0] - 1)
        #p = 0.5 * numpy.array([0.0, 1.0, 1.0]).reshape(q.shape)
        #p[0] = 0.5
        #p[1] = 0.5

        r = max(cfg['updateRate'], r)

        #2do!
        #print 'distribution accuracy', 1.0 - 2.0 * numpy.mean(numpy.abs(q - p))

        dBias = - r * (q - p)

        return { 'bias': dBias }

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
        else: vLabel = []
        if isinstance(self._config['params']['hidden'], int):
            hLabel = ['h:h%i' % (num) for num \
                in range(1, self._config['params']['hidden'] + 1)]
        elif isinstance(self._config['params']['hidden'], list):
            for node in self._config['params']['hidden']:
                if not isinstance(node, str):
                    return None
            hLabel = self._config['params']['hidden']
        else: hLabel = []

        return [{
            'id': 0, 'name': 'visible', 'visible': True, 'label': vLabel,
        }, {
            'id': 1, 'name': 'hidden', 'visible': False, 'label': hLabel
        }]

    def _getUnitsFromDataset(self, dataset):
        """Return tuple with lists of unit labels ([visible], [hidden]) using dataset for visible."""
        return (dataset.getColLabels(), self.units['hidden'].params['label'])

#    def _getUnitEvalEnergy(self, data, **kwargs):
#        """Return local energy of units."""
#        return (self.getUnitEnergy(data, ('visible',)),
#            self.getUnitEnergy(data, ('visible', 'hidden')))

#    def _getUnitEvalError(self, data, block = [], k = 1, **kwargs):
#        """Return euclidean reconstruction error of units.
#
#        error := ||data - model||"""
#        return self.getUnitError(data, data,
#            ('visible', 'hidden', 'visible'), block), None

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

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])

    # RBM HIDDEN UNIT METHODS

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
            nemoa.log('error', 'could not set links: units have not yet been set yet!')
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
        if not 'links' in self._params: self._params['links'] = {}
        if not (0, 1) in self._params['links']:
            self._params['links'][(0, 1)] = {}
        self._params['links'][(0, 1)]['A'] = A
        self._params['links'][(0, 1)]['source'] = 'visible'
        self._params['links'][(0, 1)]['target'] = 'hidden'

        # reset link update
        return True

    #def _getLinkParams(self, links = []):
        #"""Return link parameters."""
        #if not links:
            #links = self._getLinksFromConfig()

        ## create dict with link params
        #vList = self.units['visible'].params['label']
        #hList = self.units['hidden'].params['label']
        #linkParams = {}
        #for link in links:
            #if link[0] in vList and link[1] in hList:
                #i = vList.index(link[0])
                #j = hList.index(link[1])
                #linkParams[link] = {
                    #'A': self._params['links'][(0, 1)]['A'][i, j],
                    #'W': self._params['links'][(0, 1)]['W'][i, j] }
            #elif link[1] in vList and link[0] in hList:
                #i = hList.index(link[0])
                #j = vList.index(link[1])
                #linkParams[link] = {
                    #'A': self._params['links'][(0, 1)]['A'][i, j],
                    #'W': self._params['links'][(0, 1)]['W'][i, j] }
            #else:
                #nemoa.log('warning', """
                    #could not get parameters for link (%s → %s):
                    #link could not be found!""" % (link[0], link[1]))
                #continue
        #return linkParams

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
            nemoa.log('error', """
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
                nemoa.log('warning', """
                    could not delete link (%s → %s):
                    link could not be found!
                    """ % (link[0], link[1]))
                continue

        # set modified list of current links
        return self._setLinks(curLinks)

    #def _getLinkEval(self, data, func = 'energy', info = False, **kwargs):
        #"""Return link evaluation values."""
        #evalFuncs = {
            #'energy': ['local energy', 'Energy'],
            #'adjacency': ['link adjacency', 'Adjacency'],
            #'weight': ['link weight', 'Weight'] }
        #if info:
            #if not func in evalFuncs:
                #return False
            #return {
                #'name': evalFuncs[func][0]}
        #if not func in evalFuncs:
            #nemoa.log('warning', """
                #could not evaluate units:
                #unknown link evaluation function '%s'
                #""" % (func))
            #return False

        #linkEval = eval('self._getLinkEval' + evalFuncs[func][1] \
            #+ '(data, **kwargs)')
        #evalDict = {}
        #if isinstance(linkEval, numpy.ndarray):
            #for i, v in enumerate(self.units['visible'].params['label']):
                #for j, h in enumerate(self.units['hidden'].params['label']):
                    #evalDict[(v,h)] = linkEval[i, j]
        #return evalDict

    #def _getLinkEvalWeight(self, data, **kwargs):
        #"""Return link weights of all links as numpy array."""
        #return self._params['links'][(0, 1)]['W']

    #def _getLinkEvalAdjacency(self, data, **kwargs):
        #"""Return link adjacency of all links as numpy array."""
        #return self._params['links'][(0, 1)]['A']

    def _updateLinks(self, **updates):
        """Set updates for links."""
        self._params['links'][(0, 1)]['W'] += updates['W']
        return True

class grbm(rbm):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Description:
        Gaussian Restricted Boltzmann Machines are energy based
        undirected artificial neuronal networks with two layers: visible
        and hidden. The visible layer contains gauss distributed
        gaussian units to model data. The hidden layer contains binary
        distributed sigmoidal units to model relations in the data.

    Reference:
        "Improved Learning of Gaussian-Bernoulli Restricted Boltzmann
        Machines", KyungHyun Cho, Alexander Ilin and Tapani Raiko,
        ICANN 2011 """

    @staticmethod
    def _default(key): return {
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
            'checkDataset': True, # check if data is gauss normalized
            'ignoreUnits': [], # do not ignore units on update (needed for stacked updates)
            'iterations': 1, # number of repeating the whole update process
            'updates': 100000, # number of update steps / epochs
            'algorithm': 'cd', # algorithm used for updates
            'updateCdkSteps': 1, # number of gibbs steps in cdk sampling
            'updateCdkIterations': 1, # number of iterations in cdk sampling
            'updateRate': 0.001, # update rate (depends in algorithm)
            'updateFactorWeights': 1.0, # factor for weight updates (related to update rate)
            'updateFactorHbias': 0.1, # factor for hidden unit bias updates (related to update rate)
            'updateFactorVbias': 0.1, # factor for visible unit bias updates (related to update rate)
            'updateFactorVlvar': 0.01, # factor for visible unit logarithmic variance updates (related to update rate)
            'minibatchSize': 500, # number of samples used to calculate updates
            'minibatchInterval': 1, # number of updates the same minibatch is used
            'corruptionType': 'none', # do not use corruption
            'corruptionFactor': 0.0, # no corruption of data
            'sparsityRate': 0.0, # sparsity update update
            'sparsityExpect': 0.5, # aimed value for l2-norm penalty
            'selectivityFactor': 0.0, # no selectivity update
            'selectivitySize': 0.5, # aimed value for l2-norm penalty
            'useAdjacency': False, # do not use selective weight updates
            'inspect': True, # inspect optimization process
            'inspectFunction': 'accuracy', # inspection function
            'inspectTimeInterval': 20.0, # time interval for calculation the inspection function
            'estimateTime': True, # initally estimate time for whole optimization process
            'estimateTimeWait': 20.0 # time intervall used for time estimation
        }}[key]

    # GRBM data

    def _checkDataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        return self._isDatasetGaussNormalized(dataset)

    # GRBM visible units

    def _getUpdateCdVisible(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for visible units.

        Description:
            Constrastive divergency gradient of visible unit parameters
            using an modified energy function for faster convergence.
            See reference for modified Energy function."""

        cfg = self._config['optimize']

        v = len(self.units['visible'].params['label'])
        W = self._params['links'][(0, 1)]['W']
        var = numpy.exp(self.units['visible'].params['lvar'])
        b = self.units['visible'].params['bias']
        r1 = cfg['updateRate'] * cfg['updateFactorVbias']
        r2 = cfg['updateRate'] * cfg['updateFactorVlvar']
        d = numpy.mean(0.5 * (vData - b) ** 2 \
            - vData * numpy.dot(hData, W.T), axis = 0).reshape((1, v))
        m = numpy.mean(0.5 * (vModel - b) ** 2 \
            - vModel * numpy.dot(hModel, W.T), axis = 0).reshape((1, v))
        diff = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return {
            'bias': r1 * diff / var,
            'lvar': r2 * (d - m) / var }

    def _getUpdateCdLinks(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for links.

        Description:
            constrastive divergency gradient of link parameters
            using an modified energy function for faster convergence.
            See reference for modified Energy function."""

        cfg = self._config['optimize']
        var = numpy.exp(self.units['visible'].params['lvar']).T # variance of visible units
        r = cfg['updateRate'] * cfg['updateFactorWeights'] # update rate
        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)

        return { 'W': r * (D - M) / var }

    def _getVisibleUnitParams(self, label):
        """Return system parameters of one specific visible unit."""
        id = self.units['visible'].params['label'].index(label)
        return {
            'bias': self.units['visible'].params['bias'][0, id],
            'sdev': numpy.sqrt(numpy.exp(self.units['visible'].params['lvar'][0, id])) }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])
