#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, copy, numpy, time

class system:
    """Base class for systems."""

    def __init__(self, *args, **kwargs):
        """Initialize system configuration and system parameter configuration."""
    
        # set configuration and update units and links
        self.setConfig(kwargs['config'] if 'config' in kwargs else {})

    def configure(self, dataset = None, network = None, *args, **kwargs):
        """Configure system and subsystems to network and dataset."""
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            return True
        nemoa.log('info', "configure system '%s'" % (self.getName()))
        nemoa.setLog(indent = '+1')
        if not self.checkNetwork(network):
            nemoa.log('error', """
                system could not be configured:
                network is not valid!""")
            nemoa.setLog(indent = '-1')
            return False
        if not self.checkDataset(dataset):
            nemoa.log('error', """
                system could not be configured:
                dataset is not valid!""")
            nemoa.setLog(indent = '-1')
            return False
        retVal = self._configure(dataset = dataset, network = network, *args, **kwargs)
        nemoa.setLog(indent = '-1')
        return retVal

    def setConfig(self, config):
        """Set configuration."""
        
        # create local configuration dictionary
        if not hasattr(self, '_config'):
            self._config = {'check': {}}
            for key in ['params', 'init', 'optimize']:
                if not key in self._config:
                    self._config[key] = self.default(key)
        
        # overwrite / merge local with given configuration
        nemoa.common.dictMerge(config, self._config)

        # create / update local unit and link dictionaries
        if not hasattr(self, '_params'):
            self._params = {}
        self.setUnits(self._getUnitsFromConfig())
        self.setLinks(self._getLinksFromConfig())

        self._config['check']['config'] = True
        return True

    def setUnits(self, units = None, initialize = True):
        """Set units and update system parameters."""
        if not 'units' in self._params:
            self._params['units'] = []
        if not hasattr(self, 'units'):
            self.units = {}
        if initialize:
            return self._setUnits(units) \
                and self._initUnits()
        return self._setUnits(units)

    def setLinks(self, links = None, initialize = True):
        """Set links using list with 2-tuples containing unit labels."""
        if not 'links' in self._params:
            self._params['links'] = {}
        if not hasattr(self, 'links'):
            self.links = {}
        if initialize:
            return self._setLinks(links) \
                and self._indexLinks() and self._initLinks()
        return self._indexLinks()

    def getName(self):
        """Return name of system."""
        return self._config['name']

    def _get(self, sec = None):
        """Return all system settings (config, params) as dictionary."""
        dict = {
            'config': copy.deepcopy(self._config),
            'params': copy.deepcopy(self._params) }
        if not sec:
            return dict
        if sec in dict:
            return dict[sec]
        return False

    def _set(self, **dict):
        """Set system settings (config, params) from dictionary."""
        if 'config' in dict:
            self._config = copy.deepcopy(dict['config'])
            ## 2Do
            ## IF the set command gets another package or class -> Error!
        if 'params' in dict:
            self._params = copy.deepcopy(dict['params'])
        self._updateUnitsAndLinks()
        return True

    def isEmpty(self):
        """Return true if system is a dummy."""
        return False

    def isConfigured(self):
        """Return configuration state of system."""
        return self._isConfigured()

    def getConfig(self):
        """Return system configuration as dictionary."""
        return self._config.copy()

    def setNetwork(self, *args, **kwargs):
        """Update units and links to network instance."""
        return self._setNetwork(*args, **kwargs)

    def checkNetwork(self, network, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isNetwork(network):
            return False
        if not (hasattr(self.__class__, '_checkNetwork') \
            and callable(getattr(self.__class__, '_checkNetwork'))):
            return True
        return self._checkNetwork(network)

    def setDataset(self, *args, **kwargs):
        """Update units and links to dataset instance."""
        return self._setDataset(*args, **kwargs)

    def checkDataset(self, dataset, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isDataset(dataset):
            return False
        if not (hasattr(self.__class__, '_checkDataset') \
            and callable(getattr(self.__class__, '_checkDataset'))):
            return True
        return self._checkDataset(dataset)

    # name

    def getName(self):
        """Return name of system."""
        return self._config['name'] if 'name' in self._config else ''

    def setName(self, name):
        """Set name of system."""
        if not isinstance(name, str):
            return False
        self._config['name'] = name
        return True

    # class

    def getClass(self):
        """Return class of system."""
        return self._config['class']

    # type

    def getType(self):
        """Return type of system."""
        return '%s.%s' % (self._config['package'], self._config['class'])

    # description

    def getDescription(self):
        """Return description of system."""
        return self.__doc__

    # generic data methods

    def getDataEval(self, data, **kwargs):
        """Return system specific data evaluation."""
        return self._getDataEval(data, **kwargs)

    def mapData(self, data, **kwargs):
        """Return system representation of data."""
        return self._mapData(data, **kwargs)

    # generic parameter methods

    def initParams(self, dataset = None):
        """Initialize system parameters.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Initialize all system parameters to dataset.
        """
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not initilize system parameters:
                invalid dataset instance given!""")
            return False
        return self._initParams(dataset)

    def getParams(self, *args, **kwargs):
        """Return dictinary with all system parameters."""
        return copy.deepcopy(self._params)

    def setParams(self, params, update = True):
        """Set system parameters using from dictionary."""
        if not self._checkParams(params): # check parameter dictionary
            nemoa.log("error", """
                could not set system parameters:
                invalid 'params' dictionary given!""")
            return False
        if update:
            self._setParams(params)
        else: # without update just overwrite local params
            self._params = copy.deepcopy(params)
        return True

    def resetParams(self, dataset):
        """Reset system parameters using dataset instance."""
        return self.initParams(dataset)

    def optimizeParams(self, dataset, schedule):
        """Optimize system parameters using data and given schedule."""

        # check schedule
        if 'params' in schedule \
            and not self.getType() in schedule['params']:
            nemoa.log('error', """
                could not optimize model:
                optimization schedule '%s' does not include '%s'
                """ % (schedule['name'], self.getType()))
            return False

        # update local optimization schedule
        config = self.default('optimize')
        nemoa.common.dictMerge(self._config['optimize'], config)
        nemoa.common.dictMerge(schedule['params'][self.getType()] \
            if 'params' in schedule else {}, config)
        self._config['optimize'] = config

        # check dataset
        if (not 'checkDataset' in config
            or config['checkDataset'] == True) \
            and not self._checkDataset(dataset):
            return False

        # optimize system parameters
        return self._optimizeParams(dataset, schedule)

    # generic unit methods

    def getUnits(self, *args, **kwargs):
        """Return labels of units in system."""
        return self._getUnits(*args, **kwargs)

    def getUnitInfo(self, *args, **kwargs):
        """Return dictionary with information about a specific unit."""
        return self._getUnitInformation(*args, **kwargs)

    def getUnitEval(self, data, **kwargs):
        """Return dictionary with units and evaluation values."""
        return self._getUnitEval(data, **kwargs)

    def getUnitEvalInfo(self, *args, **kwargs):
        """Return information about unit evaluation functions."""
        return self._getUnitEvalInformation(*args, **kwargs)

    def unlinkUnit(self, unit, *args, **kwargs):
        """Unlink unit (if present)."""
        return self._unlinkUnit(unit)

    def removeUnits(self, type, label):
        return self._removeUnit(type, label)

    def getLinkEval(self, data, **kwargs):
        """Return dictionary with links and evaluation values."""
        return self._getLinkEval(data, **kwargs)

    # generic link methods

    def getLinks(self, *args, **kwargs):
        """Return list with 2-tuples containing unit labels."""
        return self._getLinksFromConfig()

    def removeLinks(self, links = [], *args, **kwargs):
        """Remove links from system using list with 2-tuples containing unit labels."""
        return self._removeLinks(links)

    def removeLinksByThreshold(self, method = None, threshold = None, *args, **kwargs):
        """Remove links from system using a threshold for link parameters."""
        return self._removeLinksByThreshold(method, threshold)

    def getLinkParams(self, links = [], *args, **kwargs):
        """Return parameters of links."""
        return self._getLinkParams(links)

    ####################################################################
    # Common network tests
    ####################################################################

    def _isNetworkMLPCompatible(self, network = None):
        """Check if a network is compatible to multilayer perceptrons.

        Keyword Arguments:
            network -- nemoa network instance

        Description:
            Return True if the following conditions are satisfied:
            (1) The network contains at least three layers
            (2) All layers of the network are not empty
            (3) The first and last layer of the network are visible,
                all middle layers of the network are hidden
        """
        if not nemoa.type.isNetwork(network):
            nemoa.log('error', """
                could not test network:
                invalid network instance given!""")
            return False
        if len(network.layers()) < 3:
            nemoa.log('error', """
                Multilayer networks need at least three layers!""")
            return False
        for layer in network.layers():
            if not len(network.layer(layer)['nodes']) > 0:
                nemoa.log('error', """
                    Feedforward networks do not allow empty layers!""")
                return False
            if not network.layer(layer)['visible'] \
                == (layer in [network.layers()[0], network.layers()[-1]]):
                nemoa.log('error', """
                    The first and the last layer
                    of a multilayer feedforward network have to be visible,
                    middle layers have to be hidden!""")
                return False
        return True

    def _isNetworkDBNCompatible(self, network = None):
        """Check if a network is compatible to deep beliefe networks.

        Keyword Arguments:
            network -- nemoa network instance

        Description:
            Return True if the following conditions are satisfied:
            (1) The network is MPL compatible
            (2) The network contains an odd number of layers
            (3) The hidden layers are symmetric to the central layer
                related to their number of nodes
        """
        if not nemoa.type.isNetwork(network):
            nemoa.log('error', """
                could not test network:
                invalid network instance given!""")
            return False
        if not self._isNetworkMLPCompatible(network):
            return False
        if not len(network.layers()) % 2 == 1:
            nemoa.log('error', """
                DBN / Autoencoder networks expect
                an odd number of layers!""")
            return False
        layers = network.layers()
        size = len(layers)
        for id in range(1, (size - 1) / 2):
            if not len(network.layer(layers[id])['nodes']) \
                == len(network.layer(layers[-id-1])['nodes']):
                nemoa.log('error', """
                    DBN / Autoencoder networks expect
                    a symmetric number of hidden nodes,
                    related tp their central layer!""")
                return False
        return True

    ####################################################################
    # Common dataset tests
    ####################################################################

    def _isDatasetBinary(self, dataset = None):
        """Check if a dataset contains only binary data.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Return True if a given dataset contains only binary data.
        """
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not test dataset:
                invalid dataset instance given!""")
            return False
        data = dataset.getData(1000)
        if not (data == data.astype(bool)).sum() == data.size:
            nemoa.log('error', """
                The dataset does not contain binary data!""")
            return False
        return True

    def _isDatasetGaussNormalized(self, dataset = None):
        """Check if a dataset contains gauss normalized data.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Return True if the following conditions are satisfied:
            (1) The mean value of 100k random samples
                of the dataset is < 0.05
            (2) The standard deviation 100k random samples
                of the dataset is < 1.05
        """
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', """
                could not test dataset:
                invalid dataset instance given!""")
            return False
        data = dataset.getData(100000)
        mean = data.mean()
        sdev = data.std()
        if numpy.abs(mean) >= 0.05:
            nemoa.log('error', """
                The dataset does not contain gauss normalized data:
                The mean value is %.3f!""" % (mean))
            return False
        if data.std() >= 1.05:
            nemoa.log('error', """
                The dataset does not contain gauss normalized data:
                The standard deviation is %.3f!""" % (sdev))
            return False
        return True

class empty(system):

    def __init__(self, *args, **kwargs):
        self._config = {
            'package': 'base',
            'class': 'empty',
            'description': 'dummy system',
            'name': 'empty' }

    def isEmpty(self, *args, **kwargs):
        """Return true if system is just a dummy."""
        return True

    def configure(self, *args, **kwargs):
        return True

    def setConfig(self, *args, **kwargs):
        return True

    def setNetwork(self, *args, **kwargs):
        return True

    def setDataset(self, *args, **kwargs):
        return True

    def _getUnitsFromNetwork(self, *args, **kwargs):
        return True

    def _getLinksFromNetwork(self, *args, **kwargs):
        return True

    def setUnits(self, *args, **kwargs):
        return True

    def setLinks(self, *args, **kwargs):
        return True

    def initParams(self, *args, **kwargs):
        return True

class inspector:

    __inspect = True
    __estimate = True
    __data = None
    __config = None
    __system = None
    __state = {}
    __store = []

    def __init__(self, system = None):
        self.__configure(system)

    def __configure(self, system):
        """Configure inspector to given nemoa.system instance."""
        if not nemoa.type.isSystem(system):
            nemoa.log('warning', """
                could not configure inspector:
                system is not valid!""")
            return False
        if not hasattr(system, '_config'):
            nemoa.log('warning', """
                could not configure inspector:
                system contains no configuration!""")
            return False
        if not 'optimize' in system._config:
            nemoa.log('warning', """
                could not configure inspector:
                system contains no configuration for optimization!""")
            return False
        # link system
        self.__system = system
        self.__inspect = system._config['optimize']['inspect'] \
            if 'inspect' in system._config['optimize'] \
            else True
        self.__estimate = system._config['optimize']['estimateTime'] \
            if 'estimateTime' in system._config['optimize'] \
            else True
        
    def setTestData(self, data):
        """Set numpy array with destdata."""
        self.__data = data

    def reset(self):
        """Reset inspection."""
        self.__state = {}
        self.__store = []

    def appendToStore(self, **kwargs):
        self.__store.append(kwargs)
        return True

    def getPreviousFromStore(self):
        return self.__store[-2] if len(self.__store) > 1 else {}

    def getLastFromStore(self):
        return self.__store[-1] if len(self.__store) > 0 else {}

    def difference(self):
        if not 'inspection' in self.__state:
            return 0.0
        if self.__state['inspection'] == None:
            return 0.0
        if self.__state['inspection'].shape[0] < 2:
            return 0.0
        return self.__state['inspection'][-1, 1] - \
            self.__state['inspection'][-2, 1]

    def trigger(self):
        """Update epoch and time and calculate """

        config = self.__system._config['optimize']
        epochTime = time.time()

        if self.__state == {}:
            self.__state = {
                'startTime': epochTime,
                'epoch': 0,
                'inspection': None}
            if self.__inspect:
                self.__state['inspectTime'] = epochTime
            if self.__estimate:
                self.__state['estimateStarted'] = False
                self.__state['estimateEnded'] = False
        self.__state['epoch'] += 1

        # estimate time needed to finish current optimization schedule
        if self.__estimate and not self.__state['estimateEnded']:
            if not self.__state['estimateStarted']:
                nemoa.log('info', """
                    estimating time for calculation
                    of %i updates ...""" % (config['updates']))
                self.__state['estimateStarted'] = True
            if (epochTime - self.__state['startTime']) \
                > config['estimateTimeWait']:
                estim = ((epochTime - self.__state['startTime']) \
                    / (self.__state['epoch'] + 1)
                    * config['updates'] * config['iterations'])
                estimStr = time.strftime('%H:%M',
                    time.localtime(time.time() + estim))
                nemoa.log('info', 'estimation: %ds (finishing time: %s)'
                    % (estim, estimStr))
                self.__state['estimateEnded'] = True

        # iterative evaluate model in a given time interval
        if self.__inspect:
            if self.__data == None:
                nemoa.log('warning', """
                    monitoring the process of optimization is not possible:
                    testdata is needed!""")
                self.__inspect = False
            elif self.__state['epoch'] == config['updates']:
                value = self.__system.getDataEval(
                    data = self.__data, func = config['inspectFunction'])
                measure = config['inspectFunction'].title()
                nemoa.log('info', 'final: %s = %.3f' % (measure, value))
            elif ((epochTime - self.__state['inspectTime']) \
                > config['inspectTimeInterval']) \
                and not (self.__estimate \
                and self.__state['estimateStarted'] \
                and not self.__state['estimateEnded']):
                value = self.__system.getDataEval(
                    data = self.__data, func = config['inspectFunction'])
                progress = float(self.__state['epoch']) \
                    / float(config['updates']) * 100.0
                measure = config['inspectFunction'].title()
                nemoa.log('info', """finished %.1f%%: %s = %0.4f""" \
                    % (progress, measure, value))
                self.__state['inspectTime'] = epochTime
                if self.__state['inspection'] == None:
                    self.__state['inspection'] = \
                        numpy.array([[progress, value]])
                else:
                    self.__state['inspection'] = \
                        numpy.vstack((self.__state['inspection'], \
                        numpy.array([[progress, value]])))

        return True
