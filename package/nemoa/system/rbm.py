#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Module contains various types of restricted boltzmann machines
# aimed for standalone modeling and pretraining artificial neuronal networks
#

import nemoa, numpy, time
import nemoa.system.ann

class rbm(nemoa.system.ann.ann):
    """Restricted Boltzmann Machine (RBM).

    Description:
        Restricted Boltzmann Machine with binary sigmoidal visible units
        and binary sigmoidal hidden units.
        Input: binary data, Output: transformed binary data

    Reference:
        "A Practical Guide to Training Restricted Boltzmann Machines",
        Geoffrey E. Hinton, University of Toronto, 2010
    """

    # CONFIGURATION

    def _getSystemDefaultConfig(self):
        """Return RBM default configuration as dictionary."""
        return {
            'params': {
                'samples': '*',
                'subnet': '*',
                'visible': 'auto',
                'hidden': 'auto' },
            'init': {
                'ignoreUnits': [],
                'weightSigma': 0.1 },
            'optimize': {
                'iterations': 1,
                'iterationReset': False,
                'iterationLiftLinks': False,
                'minibatchSize': 1000,
                'minibatchInterval': 10,
                'updates': 20000,
                'updateAlgorithm': 'CD',
                'updateSamplingSteps': 1,
                'updateSamplingIterations': 1,
                'ignoreUnits': [],
                'updateRate': 0.1,
                'updateFactorWeights': 1.0,
                'updateFactorHbias': 0.1,
                'updateFactorVbias': 0.1,
                'useAdjacency': False,
                'inspect': True,
                'inspectFunction': 'performance',
                'inspectInterval': 2000,
                'estimateTime': True,
                'estimateTimeWait': 5.0 }}

    def _configure(self, config = None, network = None, dataset = None, update = False, **kwargs):
        """Configure RBM to network and dataset."""
        if not 'check' in self._config:
            self._config['check'] = {
                'config': False, 'network': False, 'dataset': False}
        if not config == None:
            self._setConfig(config)
        if not network == None:
            self._setNetwork(network, update)
        if not dataset == None:
            self._setDataset(dataset)
        return self._isConfigured()

    def _initParamConfiguration(self):
        self.setUnits(self._getUnitsFromConfig())
        self.setLinks(self._getLinksFromConfig())

    def _setConfig(self, config, *args, **kwargs):
        """Set configuration from dictionary."""
        nemoa.common.dictMerge(self._getSystemDefaultConfig(), self._config)
        nemoa.common.dictMerge(config, self._config)
        self.setUnits(self._getUnitsFromConfig())
        self.setLinks(self._getLinksFromConfig())
        self._config['check']['config'] = True
        return True

    def _setNetwork(self, network, update = False, *args, **kwargs):
        """Update units and links to network instance."""
        if not nemoa.type.isNetwork(network):
            nemoa.log("error", "could not configure system: network instance is not valid!")
            return False
        self.setUnits(self._getUnitsFromNetwork(network), update)
        self.setLinks(self._getLinksFromNetwork(network))

        self._config['check']['network'] = True
        return True

    def _setDataset(self, dataset, *args, **kwargs):
        """Update units and links to dataset instance."""
        if not nemoa.type.isDataset(dataset):
            nemoa.log("error", "could not configure system: dataset object is not valid!")
            return False
        if self._getUnitsFromDataset(dataset) != self._getUnitsFromSystem():
            units = self._getUnitsFromDataset(dataset)
            links = self.getLinks()
            self.setUnits(units, update = True)
            self.setLinks(links, update = True)

        self._config['check']['dataset'] = True
        return True

    def _isConfigured(self):
        """Return configuration state of RBM."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    # DATA

    # DATA EVALUATION

    def _checkDataset(self, dataset):
        """Check if dataset contains binary values."""
        if not self._isDatasetBinary(dataset):
            nemoa.log('error', 'dataset \'%s\' is not valid: RBMs need binary data!' \
                % (dataset.getName()))
            return False
        return True

    def _getDataEval(self, data, func = 'energy', **kwargs):
        """Return data evaluation respective to system parameters."""
        if func == 'energy':
            return self._getDataEvalEnergy(data, **kwargs)
        if func == 'performance':
            return self._getDataEvalPerformance(data, **kwargs)
        if func == 'error':
            return self._getDataEvalError(data, **kwargs)
        return False

    def _getDataEvalEnergy(self, data, **kwargs):
        """Return system energy respective to data."""
        vEnergy = self._getVisibleUnitEvalEnergy(data)
        hEnergy = self._getHiddenUnitEvalEnergy(data)
        lEnergy = self._getLinkEvalEnergy(data)
        return numpy.sum(vEnergy) + numpy.sum(hEnergy) + numpy.sum(lEnergy)

    def _getDataEvalPerformance(self, data, **kwargs):
        """Return system performance respective to data."""
        return numpy.mean(self._getUnitEvalPerformance(data, **kwargs)[0])

    def _getDataEvalError(self, data, **kwargs):
        """Return system error respective to data."""
        return numpy.sum(self._getUnitEvalError(data, **kwargs)[0])

    # DATA TRANSFORMATION

    def _compress(self, data, **kwargs):
        """Return expectation values of hidden units."""
        return self._getDataFromHiddenExpect(data)

    def _getDataRepresentation(self, data, transformation = 'visiblevalue', **kwargs):
        """Return system representation of data."""
        if transformation == 'visibleexpect':
            return self._getDataFromVisibleExpect(data)
        if transformation == 'visiblevalue':
            return self._getDataFromVisibleValue(data)
        if transformation == 'visiblesample':
            return self._getDataFromVisibleSample(data)
        if transformation == 'hiddenexpect':
            return self._getDataFromHiddenExpect(data)
        if transformation == 'hiddenvalue':
            return self._getDataFromHiddenValue(data)
        if transformation == 'hiddensample':
            return self._getDataFromHiddenSample(data)
        return data

    def _getDataFromVisibleExpect(self, data, k = 1, **kwargs):
        """Return expected values of visible units after k steps."""
        vExpect = numpy.copy(data)
        for i in range(k):
            vExpect = self._getVisibleUnitExpect(self._getHiddenUnitExpect(vExpect))
        return vExpect

    def _getDataFromVisibleValue(self, data, k = 1, **kwargs):
        """Return reconstructed values of visible units after k steps."""
        vValue = numpy.copy(data)
        for i in range(k):
            vValue = self._getVisibleUnitValue(
                self._getVisibleUnitExpect(
                    self._getHiddenUnitValue(
                        self._getHiddenUnitExpect(vValue)
                    )
                )
            )
        return vValue

    def _getDataFromVisibleSample(self, data, k = 1, **kwargs):
        """Return sampled values of visible units after k steps.
        
        Parameters:
            data: data of visible units
            k: number of full Gibbs sampling steps, default "0"
        """
        vValue = numpy.copy(data)
        for i in range(k):
            vValue = self._getVisibleUnitSample(
                self._getVisibleUnitExpect(
                    self._getHiddenUnitSample(
                        self._getHiddenUnitExpect(vValue)
                    )
                )
            )
        return vValue

    def _getDataFromHiddenExpect(self, data, k = 0, **kwargs):
        """Return expected values of hidden units.

        Parameters:
            data: data of visible units
            k: number of full Gibbs sampling steps, default "0"
        """
        hExpect = self._getHiddenUnitExpect(numpy.copy(data))
        for i in range(k):
            hExpect = self._getHiddenUnitExpect(
                self._getVisibleUnitExpect(hExpect)
            )
        return hExpect

    def _getDataFromHiddenValue(self, data, k = 0, **kwargs):
        """Return reconstructed values of hidden units.

        Parameters:
            data: data of visible units
            k: number of full Gibbs sampling steps, default "0"
        """
        hValue = self._getHiddenUnitValue(self._getHiddenUnitExpect(numpy.copy(data)))
        for i in range(k):
            hValue = self._getHiddenUnitValue(
                self._getHiddenUnitExpect(
                    self._getVisibleUnitValue(
                        self._getVisibleUnitExpect(hValue)
                    )
                )
            )
        return hValue

    def _getDataFromHiddenSample(self, data, k = 1, **kwargs):
        """Return sampled values of hidden units.

        Parameters:
            data: data of visible units
            k: number of full Gibbs sampling steps, default "0"
        """
        vValue = numpy.copy(data)
        for i in range(k - 1):
            vValue = self._getVisibleUnitSample(
                self._getVisibleUnitExpect(
                    self._getHiddenUnitSample(
                        self._getHiddenUnitExpect(vValue)
                    )
                )
            )
        return vValue

    def _getDataContrastiveDivergency(self, data):
        """Return reconstructed data using 1-step contrastive divergency sampling (CD-1)."""
        hData = self._getHiddenUnitExpect(data)
        vModel = self._getVisibleUnitExpect(
            self._getHiddenUnitSample(hData)
        )
        hModel = self._getHiddenUnitExpect(vModel)
        return data, hData, vModel, hModel

    def _getDataContrastiveDivergencyKstep(self, data, k = 1, m = 1):
        """Return mean value of reconstructed data using k-step contrastive divergency sampling (CD-k).
        
        Options:
            k: number of full Gibbs sampling steps
            m: number if iterations to calculate mean values
        """
        hData  = self._getHiddenUnitExpect(data)
        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in range(m):
            for j in range(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0:
                    hSample = self._getHiddenUnitSample(hData)
                else:
                    hSample = self._getHiddenUnitSample(hExpect)

                # calculate vExpect from hSample
                vExpect = self._getVisibleUnitExpect(hSample)

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k:
                    hExpect = self._getHiddenUnitExpect(vExpect)
                else:
                    vSample = self._getVisibleUnitSample(vExpect)
                    hExpect = self._getHiddenUnitExpect(vSample)
            vModel += vExpect / m
            hModel += hExpect / m
        return data, hData, vModel, hModel

    # RBM PARAMETER METHODS

    def _initParams(self, data = None):
        """Initialize RBM parameters using data.
        If no data is given system parameters are just created
        """
        return (self._initUnits(data)
            and self._initLinkParams(data))

    #def _initUnitParams(self, data = None):
        #"""Initialize RBM unit parameters using data.
        #If no data is given unit parameters are just created
        #"""
        #self._initUnits(data)
        #print 'test'
        #quit()
        #if self._config['init']['initVisible']:
            #return (self._initVisibleUnitParams(data)
                #and self._initHiddenUnitParams(data))
        #return self._initHiddenUnitParams(data)

    def _setUpdateRates(self, **config):
        """Initialize updates for system parameters."""
        if not 'optimize' in self._config:
            self._config['optimize'] = {}
        return (self._setVisibleUnitUpdateRates(**config)
            and self._setHiddenUnitUpdateRates(**config)
            and self._setLinkUpdateRates(**config))

    def _checkUnitParams(self, params):
        """Check if system parameter dictionary is valid."""
        return (self._checkVisibleUnitParams(params)
            and self._checkHiddenUnitParams(params))

    def _checkParams(self, params):
        """Check if system parameter dictionary is valid."""
        return (self._checkUnitParams(params)
            and self._checkLinkParams(params))

    def _setParams(self, params):
        """Set system parameters from dictionary."""
        return (self._setVisibleUnitParams(params)
            and self._setHiddenUnitParams(params)
            and self._setLinkParams(params))

    def _getParams(self):
        """Return dictionary with all parameters."""
        return self._params.copy()

    def _optimizeParams(self, dataset, **kwargs):
        """Optimize system parameters."""

        # check for 'params' and update configuration
        if 'params' in kwargs:
            if not self.getType() in kwargs['params']:
                nemoa.log('error', """
                    could not optimize model:
                    schedule '%s' does not include '%s'
                    """ % (kwargs['name'], self.getType()))
                return False
            nemoa.common.dictMerge(kwargs['params'][self.getType()],
                self._config['optimize'])

        # check dataset
        if not self._checkDataset(dataset):
            return False

        # time estimation
        if self._config['optimize']['estimateTime']:
            estimTime = True
            startTime = time.time()
            nemoa.log('info', """
                estimating time for calculation
                of %i updates ...""" % \
                (self._config['optimize']['updates']))
        else:
            estimTime = False
            startTime = time.time()

        # create bunch of test data if optimization should be inspected
        if self._config['optimize']['inspect']:
            testData = dataset.getData()

        # copy optimization configuration
        config = self._config['optimize'].copy()

        # optimization
        for iteration in xrange(config['iterations']):

            # reset params before every itaration
            if config['iterationReset']:
                self.resetParams(dataset)

            # for each update step (epoch)
            for epoch in xrange(config['updates']):

                # estimate time for calculation
                if estimTime and (time.time() - startTime) > config['estimateTimeWait']:
                    estim = ((time.time() - startTime) / (epoch + 1)
                        * config['updates'] * config['iterations'])
                    estimStr = time.strftime('%H:%M',
                        time.localtime(time.time() + estim))
                    nemoa.log('info', 'estimation: %.1fs (finishing time: %s)'
                        % (estim, estimStr))
                    estimTime = False

                # get data (sample from minibatches)
                if epoch % config['minibatchInterval'] == 0:
                    data = dataset.getData(config['minibatchSize'])

                # inspect optimization
                if config['inspect'] and epoch % config['inspectInterval'] == 0 and not estimTime:
                    value = self._getDataEval(
                        data = testData,
                        func = config['inspectFunction'])
                    progress = float(epoch) / float(config['updates']) * 100.0
                    measure = config['inspectFunction'].title()
                    nemoa.log('info', 'finished %.1f%%: %s = %.2f' % (progress, measure, value))

                # get system estimations (model)
                if config['updateAlgorithm'] == 'CD':
                    sampleData = self._getDataContrastiveDivergency(data)
                elif config['updateAlgorithm'] == 'CDk':
                    sampleData = self._getDataContrastiveDivergencyKstep(data,
                        k = config['updateSamplingSteps'],
                        m = config['updateSamplingIterations'])
                else:
                    nemoa.log('error', "could not optimize model: unknown optimization algorithm '%s'" %
                        (config['updateAlgorithm']))
                    return False

                # update system params
                self._updateParams(*sampleData)

            # optionaly lift edges after every iteration
            if config['iterationLiftLinks']:
                if '_' in config['iterationLiftLinks']:
                    liftingParams = config['iterationLiftLinks'].split('_')
                    method = liftingParams[0].lower()
                    if method == 'maxcutoff':
                        maxcutoff = float(liftingParams[1])
                        threshold = maxcutoff * (float(iteration + 1) / float(config['iterations']))
                    else:
                        threshold = float(liftingParams[1])

                    self._removeLinksByThreshold(
                        method = method,
                        threshold = threshold)
                else:
                    self._removeLinksByThreshold(
                        method = config['iterationLiftLinks'].lower())

        # final information
        if config['inspect']:
            value = self._getDataEval(data = testData, func = config['inspectFunction'])
            measure = config['inspectFunction'].title()
            nemoa.log('info', 'final: %s = %.2f' % (measure, value))

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
            self._updateVisibleUnits(**updateVisibleUnits)
        if not 'hidden' in self._config['optimize']['ignoreUnits']:
            self._updateHiddenUnits(**updateHiddenUnits)
        self._updateLinks(**updateLinks)
        return True

    # UNITS

    def _getUnitsFromConfig(self):
        """Return tuple with lists of unit labels ([visible], [hidden])."""
        return (self._getVisibleUnitsFromConfig(), self._getHiddenUnitsFromConfig())

    def _getUnitsFromNetwork(self, network):
        """Return tuple with lists of unit labels ([visible], [hidden]) using network."""
        return (network.nodes(visible = True), network.nodes(visible = False))

    def _getUnitsFromDataset(self, dataset):
        """Return tuple with lists of unit labels ([visible], [hidden]) using dataset for visible."""
        return (dataset.getColLabels(), self._params['units'][1]['label'])

    def _getUnitsFromSystem(self, type = None):
        """Return tuple with lists of unit labels ([visible], [hidden])."""
        if type == 'visible':
            return self._params['units'][0]['label']
        if type == 'hidden':
            return self._params['units'][1]['label']
        return (self._params['units'][0]['label'], self._params['units'][1]['label'])

    def _setUnits(self, units):
        """Set visible and hidden units."""
        self._params['units'] = [{
            'label': units[0],
            'visible': True,
            'name': 'visible',
            'class': 'bernoulli'
        }, {
            'label': units[1],
            'visible': False,
            'name': 'hidden',
            'class': 'bernoulli'
        }]
        return True

    def _getUnitInformation(self, label):
        """Return dictionary with information about a unit."""
        if self._isVisibleUnit(label):
            return self._getVisibleUnitInformation(label)
        if self._isHiddenUnit(label):
            return self._getHiddenUnitInformation(label)
        return False

    def _getUnitParams(self, label):
        """Return dictionary with parameters of one specific unit."""
        if self._isVisibleUnit(label):
            return self._getVisibleUnitParams(label)
        if self._isHiddenUnit(label):
            return self._getHiddenUnitParams(label)
        return False

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
            nemoa.log("warning", "could not evaluate units: unknown unit evaluation function '" + func + "'")
            return False

        visibleUnitEval, hiddenUnitEval = eval(
            'self._getUnitEval' + evalFuncs[func][1] + '(data, **kwargs)')
        evalDict = {}
        if isinstance(visibleUnitEval, numpy.ndarray):
            for i, v in enumerate(self._params['units'][0]['label']):
                evalDict[v] = visibleUnitEval[i]
        if isinstance(hiddenUnitEval, numpy.ndarray):
            for j, h in enumerate(self._params['units'][1]['label']):
                evalDict[h] = hiddenUnitEval[j]
        return evalDict

    def _getUnitEvalInformation(self, func):
        """Return information about unit evaluation."""
        return self._getUnitEval(None, func = func, info = True)

    def _getUnitEvalEnergy(self, data, **kwargs):
        """Return local energy of units."""
        return (self._getVisibleUnitEvalEnergy(data),
            self._getHiddenUnitEvalEnergy(data))

    def _getUnitEvalExpect(self, data, k = 1, m = 10, **kwargs):
        """Return mean values of reconstructed units."""
        vData, hData, vModel, hModel \
            = self.sampleContrastiveDivergencyKstep(data, k = k, m = m)
        return numpy.mean(vModel, axis = 0), numpy.mean(hModel, axis = 0)

    def _getUnitEvalError(self, data, block = [], k = 1, **kwargs):
        """Return euclidean reconstruction error of units.
        
        error := ||data - model||
        """
        if not block == []:
            dataCopy = numpy.copy(data)
            for i in block:
                dataCopy[:,i] = numpy.mean(dataCopy[:,i])
            model = self._getDataFromVisibleExpect(dataCopy, k = k)
        else:
            model = self._getDataFromVisibleExpect(data, k = k)
        return numpy.sqrt(((data - model) ** 2).sum(axis = 0)), None

    def _getUnitEvalPerformance(self, data, **kwargs):
        """Return 'absolute data approximation' of units.
        
        'absolute data approximation' := 1 - error / ||data||
        """
        vErr = self._getUnitEvalError(data, **kwargs)[0]
        vNorm = numpy.sqrt((data ** 2).sum(axis = 0))
        return 1 - vErr / vNorm, None

    def _getUnitEvalIntPerformance(self, data, k = 1, **kwargs):
        """Return 'intrinsic performance' of units.
        
        'intrinsic performance' := relperf
            where model(v) is generated with: data(u not v) = mean(data(u))
        """
        vSize = len(self._params['units'][0]['label'])
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
        relExtApprox = numpy.empty(len(self._params['units'][0]['label']))
        for v in range(len(self._params['units'][0]['label'])):
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
        vSize = len(self._params['units'][0]['label'])
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
        relExtApprox = numpy.empty(len(self._params['units'][0]['label']))
        for v in range(len(self._params['units'][0]['label'])):
            relExtApprox[v] = self._getUnitEvalRelativePerformance(
                data = data, block = block + [v], k = k)[0][v]
        return relExtApprox, None

    def _unlinkUnit(self, unit):
        """Delete unit links in adjacency matrix."""
        if unit in self._params['units'][0]['label']:
            i = self._params['units'][0]['label'].index(unit)
            self._params['links'][(0, 1)]['A'][i,:] = False
            return True
        if unit in self._params['units'][1]['label']:
            i = self._params['units'][1]['label'].index(unit)
            self._params['links'][(0, 1)]['A'][:,i] = False
            return True
        return False

    # RBM VISIBLE UNIT METHODS

    def _getVisibleUnitInformation(self, label):
        """Return informaton about one visible unit."""
        return {
            'type': 'visible',
            'id': self._params['units'][0]['label'].index(label),
            'distribution': self._getVisibleUnitDistribution(label), 
            'params': self._getVisibleUnitParams(label)}

    def _getVisibleUnitDistribution(self, label):
        """Return the distribution of visible units."""
        return 'bernoulli'

    #def _initVisibleUnitParams(self, data = None):
        #"""Initialize system parameters of all visible units using data."""
        #v = len(self._params['units'][0]['label'])
        #if data == None:
            #self._params['units'][0]['bias'] = numpy.zeros([1, v])
        #else:
            #self._params['units'][0]['bias'] = numpy.mean(data, axis = 0).reshape(1, v)
        #return True

    def _checkVisibleUnitParams(self, params):
        """Check if system parameter dictionary is valid respective to visible units."""
        return 'units' in params and isinstance(params['units'], list) \
            and len(params['units']) > 0 and 'label' in params['units'][0] \
            and 'bias' in params['units'][0]

    def _isVisibleUnit(self, label):
        """Return true if label is a visible units label."""
        return label in self._params['units'][0]['label']

    def _getVisibleUnitsFromConfig(self):
        """Return list of visible unit labels using configuration."""
        if isinstance(self._config['params']['visible'], int):
            return ['v:v%i' % (num) for num in range(1, self._config['params']['visible'] + 1)]
        if isinstance(self._config['params']['visible'], list):
            for node in self._config['params']['visible']:
                if not isinstance(node, str):
                    return []
            return self._config['params']['visible']
        return []

    def _getVisibleUnitExpect(self, hValue):
        """Return the expected values of all visible units using the values of the hidden units."""
        if self._config['optimize']['useAdjacency']:
            return self._sigmoid(self._params['units'][0]['bias'] +
                numpy.dot(hValue, (self._params['links'][(0, 1)]['W'] * self._params['links'][(0, 1)]['A']).T))
        else:
            return self._sigmoid(self._params['units'][0]['bias']
                + numpy.dot(hValue, self._params['links'][(0, 1)]['W'].T))

    def _getVisibleUnitValue(self, vExpect):
        """Return reconstructed values of visible units as numpy array.

        Arguments:
            vExpect -- Expectation values for visible units.
        """
        return (vExpect > 0.5).astype(float)

    def _getVisibleUnitSample(self, vExpect):
        """Return gauss distributed samples for visible units as numpy array.

        Arguments:
            vExpect -- Expectation values for visible units.
        """
        return (vExpect > numpy.random.rand(vExpect.shape[0], vExpect.shape[1])).astype(float)

    def _getVisibleUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        v = len(self._params['units'][0]['label'])
        return { 'bias': (numpy.mean(vData - vModel, axis = 0).reshape((1, v))
            * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorVbias']) }

    def _updateVisibleUnits(self, **updates):
        """Set updates for visible units."""
        self._params['units'][0]['bias'] += updates['bias']
        return True

    def _getVisibleUnitParams(self, label):
        """Return system parameters of one specific visible unit."""
        id = self._params['units'][0]['label'].index(label)
        return { 'bias': self._params['units'][0]['bias'][0, id] }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        for i, v in enumerate(self._params['units'][0]['label']):
            if not v in params['units'][0]['label']:
                continue
            k = params['units'][0]['label'].index(v)
            self._params['units'][0]['bias'][0, i] = params['units'][0]['bias'][0, k]
        return True

    def _getVisibleUnitEvalEnergy(self, data):
        """Return local energy for all visible units as numpy array."""
        return -np.mean(data * self._params['units'][0]['bias'], axis = 0)

    # RBM HIDDEN UNIT METHODS

    #def _initHiddenUnitParams(self, data = None):
        #"""Initialize system parameters of all hidden units using data."""
        
        #self._params['units'][1]['bias'] = 0.5 * numpy.ones((1, len(self._params['units'][1]['label'])))
        #return True

    def _isHiddenUnit(self, label):
        """Return true if label is a hidden units label."""
        return label in self._params['units'][1]['label']

    def _getHiddenUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        return { 'bias': (
            numpy.mean(hData - hModel, axis = 0).reshape((1, len(self._params['units'][1]['label'])))
            * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorHbias']) }

    def _updateHiddenUnits(self, **updates):
        """Set updates for hidden units."""
        self._params['units'][1]['bias'] += updates['bias']
        return True

    def _getHiddenUnitsFromConfig(self):
        """Return list of hidden unit labels using configuration."""
        if isinstance(self._config['params']['hidden'], int):
            return ['h:h%i' % (num) for num in range(1, self._config['params']['hidden'] + 1)]
        if isinstance(self._config['params']['hidden'], list):
            for node in self._config['params']['hidden']:
                if not isinstance(node, str):
                    return []
            return self._config['params']['hidden']
        return []

    def _getHiddenUnitInformation(self, label):
        """Return information about a hidden unit."""
        return {
            'type': 'hidden',
            'id': self._params['units'][1]['label'].index(label),
            'distribution': self._getHiddenUnitDistribution(label),
            'params': self._getHiddenUnitParams(label) }

    def _getHiddenUnitDistribution(self, label):
        """Return distribution of hidden units."""
        return 'bernoulli'

    def _getHiddenUnitParams(self, label):
        """Return parameters of a specific hidden unit."""
        id = self._params['units'][1]['label'].index(label)
        return { 'bias': self._params['units'][1]['bias'][0, id] }

    def _getHiddenUnitExpect(self, vValue):
        """Return maximum likelihood values of hidden units from given visible units."""
        if self._config['optimize']['useAdjacency']:
            return self._sigmoid(self._params['units'][1]['bias'] +
                numpy.dot(vValue, self._params['links'][(0, 1)]['W'] * self._params['links'][(0, 1)]['A']))
        else:
            return self._sigmoid(self._params['units'][1]['bias'] +
                numpy.dot(vValue, self._params['links'][(0, 1)]['W']))

    def _getHiddenUnitValue(self, hExpect):
        """Return reconstructed values of hidden units using their expectation values."""
        return (hExpect > 0.5).astype(float)

    def _getHiddenUnitSample(self, hExpect):
        """Return the reconstructed values of all hidden units using their expectation values."""
        return (hExpect > numpy.random.rand(hExpect.shape[0], hExpect.shape[1])).astype(float)

    def _setHiddenUnitParams(self, params):
        """Set parameters of hidden units using dictionary."""
        for j, h in enumerate(self._params['units'][1]['label']):
            if not h in params['units'][1]['label']:
                continue
            l = params['units'][1]['label'].index(h)
            self._params['units'][1]['bias'][0, j] = params['units'][1]['bias'][0, l]
        return True

    def _checkHiddenUnitParams(self, params):
        """Check if system parameter dictionary is valid respective to hidden units."""
        return ('units' in params and 'label' in params['units'][1]
            and 'bias' in params['units'][1])

    def _getHiddenUnitEvalEnergy(self, data):
        """Return system energy for all hidden units as numpy array."""
        hData = self._getHiddenUnitValue(self._getHiddenUnitExpect(data))
        return -np.mean(hData * self._params['units'][1]['bias'], axis = 0)

    # RBM LINK METHODS

    def _getLinksFromConfig(self):
        """Return links from adjacency matrix."""
        links = []
        for i, v in enumerate(self._params['units'][0]['label']):
            for j, h in enumerate(self._params['units'][1]['label']):
                if not 'A' in self._params or self._params['links'][(0, 1)]['A'][i, j]:
                    links.append((v, h))
        return links

    def _getLinksFromNetwork(self, network):
        """Return links from network instance."""
        return network.edges()

    def _setLinks(self, links = []):
        """Set links and create link adjacency matrix."""
        if not self._checkUnitParams(self._params): # check params
            nemoa.log("error", "could not set links: units have not yet been set yet!")
            return False

        # create adjacency matrix from links
        vList = self._params['units'][0]['label']
        hList = self._params['units'][1]['label']
        A = numpy.empty([len(vList), len(hList)], dtype = bool)
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

    def _initLinkParams(self, data = None):
        """Initialize system parameteres of all links using data."""
        v = len(self._params['units'][0]['label'])
        h = len(self._params['units'][1]['label'])
        if data == None:
            self._params['links'][(0, 1)]['A'] = numpy.ones([v, h], dtype = bool)
            self._params['links'][(0, 1)]['W'] = numpy.zeros([v, h], dtype = float)
        else:
            #2DO: this can be done much better
            sigma = (self._config['init']['weightSigma']
                * numpy.std(data, axis = 0).reshape(1, v).T) + 0.00001
            #########
            self._params['links'][(0, 1)]['W'] = (self._params['links'][(0, 1)]['A']
                * numpy.random.normal(numpy.zeros((v, h)), sigma))
        return True

    def _getLinkParams(self, links = []):
        """Return link parameters."""
        if not links:
            links = self._getLinksFromConfig()

        # create dict with link params
        vList = self._params['units'][0]['label']
        hList = self._params['units'][1]['label']
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
        for i, v in enumerate(self._params['units'][0]['label']):
            if not v in params['units'][0]['label']:
                continue
            k = params['units'][0]['label'].index(v)
            for j, h in enumerate(self._params['units'][1]['label']):
                if not h in params['units'][1]['label']:
                    continue
                l = params['units'][1]['label'].index(h)
                self._params['links'][(0, 1)]['A'][i, j] = params['A'][k, l]
                self._params['links'][(0, 1)]['W'][i, j] = params['W'][k, l]
        return True

    def _checkLinkParams(self, params):
        """Check if system parameter dictionary is valid respective to links."""
        return ('A' in params and 'W' in params)

    def _removeLinks(self, links = []):
        """Remove links from adjacency matrix using list of links."""
        if not self._checkParams(self._params): # check params
            nemoa.log("error", "could not remove links: units have not yet been set yet!")
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
                nemoa.log("warning", 'could not delete link (%s → %s): link could not be found!' % (link[0], link[1]))
                continue

        # set modified list of current links
        return self._setLinks(curLinks)

    def _removeLinksByThreshold(self, method = None, threshold = None):
        """Remove links from adjacency matrix using threshold for parameters."""
        if not self._checkParams(self._params): # check params
            nemoa.log("error", "could not delete links: units have not yet been set yet!")
            return False
        if not method: # check method
            return False

        curLinks = self._getLinksFromConfig() # get current links

        # delete links by absolute weight threshold
        count = 0
        countAll = len(curLinks)
        if method in ['cutoff', 'maxcutoff']:
            linkParams = self._getLinkParams()
            newLinks = []
            for link in linkParams:
                if numpy.abs(linkParams[link]['W']) >= threshold:
                    continue
                found = False
                if (link[0], link[1]) in curLinks:
                    del curLinks[curLinks.index((link[0], link[1]))]
                    found = True
                if (link[1], link[0]) in curLinks:
                    del curLinks[curLinks.index((link[1], link[0]))]
                    found = True
                if found:
                    count += 1
                    nemoa.log('logfile', 'delete link (%s → %s): weight < %.2f' % (link[0], link[1], threshold))

        if count == 0:
            return False

        # inform
        nemoa.log('console', 'deleted %i of %i links. (see logfile)' % (count, countAll))

        # set modified list of current links
        if self._setLinks(curLinks):
            return count

        # some error happened
        nemoa.log('warning', 'could not set links! (see logfile)')
        return False

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
            nemoa.log("warning", "could not evaluate units: unknown link evaluation function '" + func + "'")
            return False

        linkEval = eval('self._getLinkEval' + evalFuncs[func][1] + '(data, **kwargs)')
        evalDict = {}
        if isinstance(linkEval, numpy.ndarray):
            for i, v in enumerate(self._params['units'][0]['label']):
                for j, h in enumerate(self._params['units'][1]['label']):
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
        hData = self._getHiddenUnitValue(self._getHiddenUnitExpect(data))
        if self._config['optimize']['useAdjacency']:
            return -(self._params['links'][(0, 1)]['A'] * self._params['links'][(0, 1)]['W']
                * numpy.dot(data.T, hData) / data.shape[0])
        return -(self._params['links'][(0, 1)]['W'] * numpy.dot(data.T, hData) / data.shape[0])

    def _getLinkUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for links."""
        return { 'W': (numpy.dot(vData.T, hData) - numpy.dot(vModel.T, hModel))
            / vData.shape[0] * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorWeights']}

    def _updateLinks(self, **updates):
        """Set updates for links."""
        self._params['links'][(0, 1)]['W'] += updates['W']
        return True

class grbm(rbm):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Description:
        Restricted Boltzmann Machine with continous gaussian visible units
        and binary sigmoidal hidden units
        Input: gauss normalized data, Output: transformed binary data

    Reference:
        "Improved Learning of Gaussian-Bernoulli Restricted Boltzmann Machines",
        KyungHyun Cho, Alexander Ilin and Tapani Raiko, ICANN 2011
    """

    def _getSystemDefaultConfig(self):
        """Return GRBM default configuration as dictionary."""
        return {
            'params': {
                'samples': '*',
                'subnet': '*',
                'visible': 'auto',
                'hidden': 'auto' },
            'init': {
                'ignoreUnits': [],
                'vSigma': 0.4,
                'weightSigma': 0.02 },
            'optimize': {
                'iterations': 1,
                'iterationReset': False,
                'iterationLiftLinks': False,
                'updates': 100000,
                'updateAlgorithm': 'CD',
                'updateSamplingSteps': 1,
                'updateSamplingIterations': 1,
                'ignoreUnits': [],
                'updateRate': 0.005,
                'updateFactorWeights': 1.0,
                'updateFactorHbias': 0.1,
                'updateFactorVbias': 0.1,
                'updateFactorVlvar': 0.01,
                'minibatchSize': 1000,
                'minibatchInterval': 10,
                'useAdjacency': False,
                'inspect': True,
                'inspectFunction': 'performance',
                'inspectInterval': 1000,
                'estimateTime': True,
                'estimateTimeWait': 5.0 }}

    # GRBM data

    def _checkDataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        return self._isDatasetGaussNormalized(dataset)

    # GRBM units
    def _setUnits(self, units):
        """Set visible and hidden units."""
        self._params['units'] = [{
            'label': units[0],
            'visible': True,
            'name': 'visible',
            'class': 'gauss'
        }, {
            'label': units[1],
            'visible': False,
            'name': 'hidden',
            'class': 'bernoulli'
        }]
        return True

    # GRBM visible units

    def _getVisibleUnitDistribution(self, label):
        """Return distribution of visible units."""
        return 'gauss'

    #def _initVisibleUnitParams(self, data = None):
        #"""Initialize system parameters of all visible units using data."""
        #return self._initGaussUnits(layerID = 0, data = data)

    def _getVisibleUnitUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for visible units."""
        v = len(self._params['units'][0]['label'])
        W = self._params['links'][(0, 1)]['W']
        vVar = numpy.exp(self._params['units'][0]['lvar'])
        vBias = self._params['units'][0]['bias']
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

    def _updateVisibleUnits(self, **updates):
        """Set updates for visible units."""
        self._params['units'][0]['bias'] += updates['bias']
        self._params['units'][0]['lvar'] += updates['lvar']
        return True

    def _getVisibleUnitParams(self, label):
        """Return system parameters of one specific visible unit."""
        id = self._params['units'][0]['label'].index(label)
        return {
            'bias': self._params['units'][0]['bias'][0, id],
            'sdev': numpy.sqrt(numpy.exp(self._params['units'][0]['lvar'][0, id])) }

    def _setVisibleUnitParams(self, params):
        """Set parameters of visible units using dictionary."""
        for i, v in enumerate(self._params['units'][0]['label']):
            if not v in params['units'][0]['label']:
                continue
            k = params['units'][0]['label'].index(v)
            self._params['units'][0]['bias'][0, i] = params['units'][0]['bias'][0, k]
            self._params['units'][0]['lvar'][0, i] = params['units'][0]['lvar'][0, k]
        return True

    def _checkVisibleUnitParams(self, params):
        """Check if system parameter dictionary is valid respective to visible units."""
        return 'units' in params and isinstance(params['units'], list) \
            and len(params['units']) > 0 and 'label' in params['units'][0] \
            and 'bias' in params['units'][0] and 'lvar' in params['units'][0] 

    def _getVisibleUnitExpect(self, hValue):
        """Return expectation values of visible units as numpy array.

        Arguments:
        hValue -- Values of hidden units.
        """
        if self._config['optimize']['useAdjacency']:
            return self._params['units'][0]['bias'] + numpy.dot(hValue, (self._params['links'][(0, 1)]['W'] * self._params['links'][(0, 1)]['A']).T)
        else:
            return self._params['units'][0]['bias'] + numpy.dot(hValue, self._params['links'][(0, 1)]['W'].T)

    def _getVisibleUnitValue(self, vExpect):
        """
        Return reconstructed values of visible units as numpy array.

        Arguments:
        vExpect -- Expectation values for visible units.
        """
        return vExpect

    def _getVisibleUnitSample(self, vExpect):
        """
        Return gauss distributed samples for visible units as numpy array.

        Arguments:
        vExpect -- Expectation values for visible units.
        """
        return numpy.random.normal(vExpect, numpy.sqrt(numpy.exp(self._params['units'][0]['lvar'])))

    def _getVisibleUnitEvalEnergy(self, data):
        """
        Return local energy for all visible units as numpy array.
        """
        return -np.mean((data - self._params['units'][0]['bias']) ** 2
            / numpy.exp(self._params['units'][0]['lvar']), axis = 0) / 2

    # GRBM hidden units

    def _getHiddenUnitExpect(self, vValue):
        """
        Return the expected values of all hidden units using the values of the visible units.
        """
        vVar = numpy.exp(self._params['units'][0]['lvar'])
        if self._config['optimize']['useAdjacency']:
            return self._sigmoid(self._params['units'][1]['bias'] +
                numpy.dot(vValue / vVar, self._params['links'][(0, 1)]['W'] * self._params['links'][(0, 1)]['A']))
        else:
            return self._sigmoid(self._params['units'][1]['bias'] +
                numpy.dot(vValue / vVar, self._params['links'][(0, 1)]['W']))

    # GRBM links

    def _getLinkEvalEnergy(self, data):
        """Return link energy of all links as numpy array."""
        hData = self._getHiddenUnitExpect(data)
        if self._config['optimize']['useAdjacency']:
            return -(self._params['links'][(0, 1)]['A'] * self._params['links'][(0, 1)]['W'] * numpy.dot((data
                / numpy.exp(self._params['units'][0]['lvar'])).T, hData) / data.shape[0])
        return -(self._params['links'][(0, 1)]['W'] * numpy.dot((data
            / numpy.exp(self._params['units'][0]['lvar'])).T, hData) / data.shape[0])

    def _getLinkUpdates(self, vData, hData, vModel, hModel, **kwargs):
        """Return updates for links."""
        vVar = numpy.exp(self._params['units'][0]['lvar'])
        return { 'W': ((numpy.dot(vData.T, hData) - numpy.dot(vModel.T, hModel))
            / vData.shape[0] / vVar.T * self._config['optimize']['updateRate']
            * self._config['optimize']['updateFactorWeights']) }

#class crbm(rbm):
    #"""Continous Restricted Boltzmann Machine (CRBM).

    #Description:
        #Restricted Boltzmann Machine with continous linear visible units
        #and binary sigmoidal hidden units
        #Input: linear normalized data, Output: transformed binary data
    
    #Reference:
    
    #"""

    ##
    ## todo!
    ##

    #pass
