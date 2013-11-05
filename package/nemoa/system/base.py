#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa
import copy, numpy

class system:
    """Base class for systems."""

    _config = None
    _params = None
    _units = None
    _links = None

    # generic system configuration methods

    def __init__(self, *args, **kwargs):
        """Initialize system configuration and system parameter configuration."""
    
        # set default system configuration dictionary
        if hasattr(self.__class__, '_getSystemDefaultConfig') \
            and callable(getattr(self.__class__, '_getSystemDefaultConfig')):
            self._config = self._getSystemDefaultConfig()
        else:
            self._config = {}

        # merge with given configuration dictionary
        if 'config' in kwargs \
            and isinstance(kwargs['config'], dict):
            nemoa.common.dictMerge(kwargs['config'], self._config)

        # set default system parameter configuration dictionary
        self._params = {}
        if hasattr(self.__class__, '_initParamConfiguration') \
            and callable(getattr(self.__class__, '_initParamConfiguration')):
            self._initParamConfiguration()

    def configure(self, dataset = None, network = None, *args, **kwargs):
        """Configure system and subsystems to network and dataset."""
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            return True
        nemoa.log('info', "configure system '%s'" % (self.getName()))
        nemoa.setLog(indent = '+1')
        if not self.checkNetwork(network):
            nemoa.log('error', 'system could not be configured: network is not valid!')
            nemoa.setLog(indent = '-1')
            return False
        if not self.checkDataset(dataset):
            nemoa.log('error', 'system could not be configured: dataset is not valid!')
            nemoa.setLog(indent = '-1')
            return False
        retVal = self._configure(dataset = dataset, network = network, *args, **kwargs)
        nemoa.setLog(indent = '-1')
        return retVal

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
            ## 2Do
            ## IF the set command gets another package or class -> Error!
            self._config = copy.deepcopy(dict['config'])
        if 'params' in dict:
            self._params = copy.deepcopy(dict['params'])
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

    def getDataRepresentation(self, data, **kwargs):
        """Return system representation of data."""
        return self._getDataRepresentation(data, **kwargs)

    # generic parameter methods

    def initParams(self, dataset, *args, **kwargs):
        """Initialize system parameters using dataset instance."""
        if not nemoa.type.isDataset(dataset): # check dataset instance
            nemoa.log("error", "could not initilize system parameters: invalid 'dataset' instance given!")
            return False
        if 'samples' in self._config['params']: # using row filter
            data = dataset.getData(100000, rows = self._config['params']['samples'])
        else:
            data = dataset.getData(100000)
        return self._initParams(data) # initilize parameters

    def getParams(self, *args, **kwargs):
        """Return dictinary with all system parameters."""
        return copy.deepcopy(self._params)

    def setParams(self, params, update = True):
        """Set system parameters using from dictionary."""
        if not self._checkParams(params): # check parameter dictionary
            nemoa.log("error", "could not set system parameters: invalid 'params' dictionary given!")
            return False
        if update:
            self._setParams(params)
        else: # without update just overwrite local params
            self._params = copy.deepcopy(params)
        return True

    def resetParams(self, dataset):
        """Reset system parameters using dataset instance."""
        return self.initParams(dataset)

    def optimizeParams(self, *args, **kwargs):
        """Optimize system parameters using dataset and preferred algorithm."""
        return self._optimizeParams(*args, **kwargs)

    # generic unit methods

    def getUnits(self, *args, **kwargs):
        """Return labels of units in system."""
        return self._getUnitsFromSystem(*args, **kwargs)

    def getUnitInfo(self, label, *args, **kwargs):
        """Return dictionary with information about a specific unit."""
        return self._getUnitInformation(label)

    def getUnitEval(self, data, **kwargs):
        """Return dictionary with units and evaluation values."""
        return self._getUnitEval(data, **kwargs)

    def getUnitEvalInfo(self, *args, **kwargs):
        """Return information about unit evaluation functions."""
        return self._getUnitEvalInformation(*args, **kwargs)

    def setUnits(self, units = ([], ), update = False, **kwargs):
        """Set units and update system parameters."""
        if update:
            if not self._checkParams(self._params):
                nemoa.log("error", "could not update units: units have not yet been set!")
                return False
            backup = self.getParams()
            self._setUnits(units)
            self._linkUnits()
            self._initUnits()
            return self.setParams(backup)

        self._setUnits(units)
        self._linkUnits()
        self._initUnits()
        return True

    def setLinks(self, links = [], update = False, *args, **kwargs):
        """Set links using list with 2-tuples containing unit labels."""
        self._setLinks(links)
        self._linkLinks()
        self._initLinks()
        return True

    def unlinkUnit(self, unit, *args, **kwargs):
        """Unlink unit (if present)."""
        return self._unlinkUnit(unit)

    def deleteUnits(self, type, label):
        return self._deleteUnit(type, label)

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

    #
    # common network check functions
    #

    def _isNetworkMLPCompatible(self, network):
        """Check if the network is compatible to multi layer perceptrons."""
        layers = network.layers()
        if len(layers) < 3:
            nemoa.log('error', 'Multilayer networks need at least three layers!')
            return False
        firstLayer = layers[0]
        lastLayer = layers[-1]
        for layer in network.layers():
            layerAttrib = network.layer(layer)
            if not len(layerAttrib['nodes']):
                nemoa.log('error', 'Feedforward networks do not allow empty layers!')
                return False
            if layer in [firstLayer, lastLayer]:
                if not layerAttrib['visible']:
                    nemoa.log('error', 'The first and the last layer of a multilayer feedforward network have to be visible!')
                    return False
            else:
                if layerAttrib['visible']:
                    nemoa.log('error', 'The middle layers of a multilayer feedforward networks have to be hidden!')
                    return False
        return True

    def _isNetworkDBNCompatible(self, network):
        """Check if the network is compatible to deep beliefe networks."""
        layers = network.layers()
        return True
        

    #
    # common dataset check functions
    #

    def _isDatasetBinary(self, dataset):
        """Returns true if a given dataset contains binary data."""
        data = dataset.getData(1000)
        if not (data == data.astype(bool)).sum() == data.size:
            nemoa.log('error', 'The dataset does not contain binary data!')
            return False
        return True

    def _isDatasetGaussNormalized(self, dataset):
        """Returns true if a given dataset contains gauss normalized data."""
        data = dataset.getData(100000)
        if numpy.abs(data.mean()) > 0.05 \
            or numpy.abs(data.std() - 1) > 0.05:
            nemoa.log('error', 'The dataset does not contain (gauss) normalized data!')
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
