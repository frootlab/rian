# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine class networks.

Various classes of restricted boltzmann machines aimed for data modeling
and per layer pretraining of multilayer feedforward artificial neural
networks
"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.ann
import numpy

class rbm(nemoa.system.ann.ann):
    """Restricted Boltzmann Machine (RBM).

    Restricted Boltzmann Machines (1) are energy based undirected
    artificial neuronal networks with two layers with visible and
    hidden units. The visible layer contains binary distributed
    sigmoidal units to model data. The hidden layer contains binary
    distributed sigmoidal units to model relations in the data.

    Reference:
        (1) "A Practical Guide to Training Restricted Boltzmann
            Machines", Geoffrey E. Hinton, University of Toronto, 2010
    """

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
            'modSaEnable': True,
            'modSaInitTemperature': 1.0,
            'modSaAnnealingFactor': 1.0,
            'modSaAnnealingCycles': 1,
            'modKlEnable': True,
            'modKlRate': 0.0,
            'modKlExpect': 0.5,
            'selectivityFactor': 0.0,
            'selectivitySize': 0.5,
            'modCorruptionEnable': True,
            'modCorruptionType': 'mask',
            'modCorruptionFactor': 0.5,
            'useAdjacency': False,
            'trackerObjFunction': 'error',
            'trackerEvalTimeInterval': 10.0 ,
            'trackerEstimateTime': True,
            'trackerEstimateTimeWait': 20.0 }}[key]

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
        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')
        if not dataset._isBinary(): return nemoa.log('error',
            "dataset '%s' is not valid: RBMs expect binary data."
            % (dataset.name()))
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

    def _optParams(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        cfg = self._config['optimize']

        if cfg['modCorruptionEnable']: nemoa.log(
            'note', """using data corruption for denoising with
            noise model '%s (%.2f)'""" % (
            cfg['modCorruptionType'], cfg['modCorruptionFactor']))
        if cfg['modKlEnable']: nemoa.log('note',
            """using Kullback-Leibler penalty for sparse coding
            with expectation value %.2f""" % (cfg['modKlExpect']))
        if cfg['modVmraEnable']: nemoa.log('note',
            """using variance maximizing rate adaption
            with length %i""" % (cfg['modVmraLength']))
        if cfg['modSaEnable']: nemoa.log('note',
            """using simulated annealing  with initial temperature %.2f
            and annealing factor %.2f""" % (cfg['modSaInitTemperature'],
            cfg['modSaAnnealingFactor']))

        if cfg['algorithm'].lower() == 'cd': return \
            self._optCd(dataset, schedule, tracker)
        return nemoa.log('error', """could not optimize model:
            unknown optimization algorithm '%s'""" % (algorithm))

    def _optCd(self, dataset, schedule, tracker):
        """Optimize system parameters with Contrastive Divergency."""

        cfg  = self._config['optimize']

        while tracker.update():

            # get data (sample from minibatches)
            if tracker.get('epoch') % cfg['minibatchInterval'] == 0:
                data = self._optGetData(dataset)

            self._optCdUpdate(data, tracker) # Update system parameters

        return True

    def _optVmraUpdate(self, tracker):
        store = tracker.read('vmra')
        var = numpy.var(self._params['links'][(0, 1)]['W'])
        if not 'wVar' in store: wVar = numpy.array([var])
        else: wVar = numpy.append([var], store['wVar'])

        cfg = self._config['optimize']
        length = cfg['modVmraLength']
        if wVar.shape[0] > length:

            wVar = wVar[:length]
            A = numpy.array([numpy.arange(0, length),
                numpy.ones(length)])
            grad = - numpy.linalg.lstsq(A.T, wVar)[0][0]
            delw = cfg['modVmraFactor'] * grad

            cfg['updateRate'] = min(max(delw,
                cfg['modVmraMinRate']), cfg['modVmraMaxRate'])

        tracker.write('vmra', wVar = wVar)
        return True

    def _optCdSampling(self, data):
        """Contrastive divergency sampling.

        Args:
            data:
            (k steps, m iterations)

        Returns:
            tuple (vData, hData, vModel, hModel)
            containing numpy arrays:
                vData: input data of visible units
                hData: expected values of hidden units for vData
                vModel: sampled values of visible units after k sampling
                    steps calculated as mean values over m iterations.
                hModel: expected values of hidden units for vModel
        """

        cfg = self._config['optimize']

        k = cfg['updateCdkSteps']
        m = cfg['updateCdkIterations']

        hData = self._evalUnitExpect(data, ('visible', 'hidden'))
        if k == 1 and m == 1:
            vModel = self._evalUnitSamples(hData, ('hidden', 'visible'),
                expectLast = True)
            hModel = self._evalUnitExpect(vModel, ('visible', 'hidden'))
            return data, hData, vModel, hModel

        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in range(m):
            for j in range(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0: hSample = self._evalUnitSamples(
                    hData, ('hidden', ))
                else: hSample = self._evalUnitSamples(hExpect, (
                    'hidden', ))

                # calculate vExpect from hSample
                vExpect = self._evalUnitExpect(hSample, ('hidden',
                    'visible'))

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k: hExpect = self._evalUnitExpect(vExpect,
                    ('visible', 'hidden'))
                else: hExpect = self._evalUnitSamples(vExpect,
                    ('visible', 'hidden'), expectLast = True)

            vModel += vExpect / m
            hModel += hExpect / m

        return data, hData, vModel, hModel

    def _optCdUpdate(self, data, tracker):
        """Update system parameters."""

        config = self._config['optimize']
        ignore = config['ignoreUnits']

        # (optional) Variance maximizing rate adaption
        if config['modVmraEnable']:
            if tracker.get('epoch') % config['modVmraInterval'] == 0 \
                and tracker.get('epoch') > config['modVmraWait']:
                self._optVmraUpdate(tracker)

        # get system estimations (model)
        dTuple = self._optCdSampling(data)

        # Calculate contrastive divergency updates
        # (without affecting the calculations)
        if not 'visible' in ignore: deltaV = self._optCdDeltaV(*dTuple)
        if not 'hidden' in ignore: deltaH = self._optCdDeltaH(*dTuple)
        if not 'links' in ignore: deltaL = self._optCdDeltaL(*dTuple)

        # Contrastive Divergency update
        if not 'visible' in ignore: self.units['visible'].update(deltaV)
        if not 'hidden' in ignore: self.units['hidden'].update(deltaH)
        if not 'links' in ignore: self._updateLinks(**deltaL)

        # (optional) Kullback-Leibler penalty update for sparsity
        if config['modKlEnable']:
            if not 'hidden' in ignore: self.units['hidden'].update(
                self._optKlDeltaH(*dTuple))

        # (optional) Simulated Annealing update to avoid underfitting
        if config['modSaEnable']:
            if not 'visible' in ignore: self.units['visible'].update(
                self._optSaDeltaV(tracker))
            if not 'hidden' in ignore: self.units['hidden'].update(
                self._optSaDeltaH(tracker))
            if not 'links' in ignore: self._updateLinks(
                **self._optSaDeltaL(tracker))

        return True

    def _optCdDeltaV(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of visible units.

        Returns:
            Dictionary with numpy arrays containing visible unit
            parameter gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        r = cfg['updateRate'] * cfg['updateFactorVbias'] # update rate
        v = len(self.units['visible'].params['label'])
        diff = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return { 'bias': r * diff }

    def _optCdDeltaH(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        h = len(self.units['hidden'].params['label'])
        r = cfg['updateRate'] * cfg['updateFactorHbias'] # update rate
        diff = numpy.mean(hData - hModel, axis = 0).reshape((1, h))

        return { 'bias': r * diff }

    def _optCdDeltaL(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of links.

        Returns:
            Dictionary with numpy arrays containing link parameter
            gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)
        r = cfg['updateRate'] * cfg['updateFactorWeights'] # update rate

        return { 'W': r * (D - M) }

    def _optKlDeltaH(self, vData, hData, vModel, hModel):
        """Kullback-Leibler penalty gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by Kullback-Leibler penalty,
            which uses l1-norm cross entropy.
        """

        cfg = self._config['optimize']

        p = cfg['modKlExpect'] # target expectation value
        q = numpy.mean(hData, axis = 0) # expectation value over samples
        r = max(cfg['updateRate'], cfg['modKlRate']) # update rate

        return { 'bias': r * (p - q) }

    def _optSaDeltaH(self, tracker):
        cfg = self._config['optimize']
        #cfg['modSaInitTemperature'], cfg['modSaAnnealingFactor']

        #dBias = numpy.zeros([1, hData.shape[1]])

        #return { 'bias': dBias }
        return {}

    def _optSaDeltaV(self, tracker):
        cfg = self._config['optimize']
        #cfg['modSaInitTemperature'], cfg['modSaAnnealingFactor']

        #dBias = numpy.zeros([1, vData.shape[1]])

        #return { 'bias': dBias }
        return {}

    def _optSaDeltaL(self, tracker):
        cfg = self._config['optimize']
        params = tracker.read('sa')
        if params:
            initRate = params['initRate']
        else:
            initRate = cfg['updateRate']
            tracker.write('sa', initRate = initRate)

        shape = self._params['links'][(0, 1)]['W'].shape
        r = initRate ** 2 / cfg['updateRate'] * cfg['updateFactorWeights']
        temperature = self._optSaTemperature(tracker)
        if temperature == 0.0: return {}
        sigma = r * temperature
        W = numpy.random.normal(0.0, sigma, shape)

        return { 'W': W }

    def _optSaTemperature(self, tracker):
        """Calculate temperature for simulated annealing."""
        config = self._config['optimize']

        init      = float(config['modSaInitTemperature'])
        annealing = float(config['modSaAnnealingFactor'])
        cycles    = float(config['modSaAnnealingCycles'])
        updates   = int(float(config['updates']) / cycles)
        epoch     = float(tracker.get('epoch') % updates)
        heat      = init * (1.0 - epoch / float(updates)) ** annealing

        if heat < config['modSaMinTemperature']: return 0.0
        return heat

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
            'id': 0, 'name': 'visible',
            'visible': True, 'label': vLabel,
        }, {
            'id': 1, 'name': 'hidden',
            'visible': False, 'label': hLabel
        }]

    def _getUnitsFromDataset(self, dataset):
        """Return tuple with lists of unit labels ([visible], [hidden]) using dataset for visible."""
        return (dataset.getColLabels(), self.units['hidden'].params['label'])

    #2Do: generalize to ann
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

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])

    def _setHiddenUnitParams(self, params):
        """Set parameters of hidden units using dictionary."""
        return self.units['hidden'].overwrite(params['units'][1])

    def _getLinksFromConfig(self):
        """Return links from adjacency matrix."""
        links = []
        for i, v in enumerate(self.units['visible'].params['label']):
            for j, h in enumerate(self.units['hidden'].params['label']):
                if not 'A' in self._params \
                    or self._params['links'][(0, 1)]['A'][i, j]:
                    links.append((v, h))
        return links

    def _getLinksFromNetwork(self, network):
        """Return links from network instance."""
        return network.edges()

    def _setLinks(self, links = []):
        """Set links and create link adjacency matrix."""
        if not self._checkUnitParams(self._params):
            return nemoa.log('error', """could not set links:
                units have not yet been set yet!""")

        # create adjacency matrix from links
        vList = self.units['visible'].params['label']
        hList = self.units['hidden'].params['label']
        A = numpy.empty([len(vList), len(hList)], dtype = bool)

        #2Do: This is very slow: we could try "for link in links" etc.
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

        return True

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
                nemoa.log('warning', """could not delete link (%s → %s):
                    link could not be found!""" % (link[0], link[1]))
                continue

        return self._setLinks(curLinks)

    def _updateLinks(self, **updates):
        """Set updates for links."""
        if 'W' in updates:
            self._params['links'][(0, 1)]['W'] += updates['W']
        if 'A' in updates:
            self._params['links'][(0, 1)]['A'] = updates['A']
        return True

class grbm(rbm):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Gaussian Restricted Boltzmann Machines are energy based
    undirected artificial neuronal networks with two layers: visible
    and hidden. The visible layer contains gauss distributed
    gaussian units to model data. The hidden layer contains binary
    distributed sigmoidal units to model relations in the data.

    Reference:
        "Improved Learning of Gaussian-Bernoulli Restricted Boltzmann
        Machines", KyungHyun Cho, Alexander Ilin and Tapani Raiko,
        ICANN 2011
    """

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
            'modCorruptionEnable': False,
            'modCorruptionType': 'none', # do not use corruption
            'modCorruptionFactor': 0.0, # no corruption of data
            'modSaEnable': True, # use simulated annealing
            'modSaInitTemperature': 1.0,
            'modSaAnnealingFactor': 1.0,
            'modSaAnnealingCycles': 1,
            'modKlEnable': True, # use Kullback-Leibler penalty
            'modKlRate': 0.0, # sparsity update
            'modKlExpect': 0.5, # aimed value for l2-norm penalty
            'selectivityFactor': 0.0, # no selectivity update
            'selectivitySize': 0.5, # aimed value for l2-norm penalty
            'useAdjacency': False, # do not use selective weight updates
            'trackerObjFunction': 'error', # objective function
            'trackerEvalTimeInterval': 20.0, # time interval for calculation the inspection function
            'trackerEstimateTime': True, # initally estimate time for whole optimization process
            'trackerEstimateTimeWait': 20.0 # time intervall used for time estimation
        }}[key]

    def _checkDataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')
        if not dataset._isGaussNormalized(): return nemoa.log('error',
            """dataset '%s' is not valid: GRBMs expect
            standard normal distributed data.""" % (dataset.name()))
        return True

    def _optCdDeltaV(self, vData, hData, vModel, hModel, **kwargs):
        """Return cd gradient based updates for visible units.

        Constrastive divergency gradient of visible unit parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.
        """

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

    def _optCdDeltaL(self, vData, hData, vModel, hModel, **kwargs):
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
            'sdev': numpy.sqrt(numpy.exp(
                self.units['visible'].params['lvar'][0, id])) }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        return self.units['visible'].overwrite(params['units'][0])
