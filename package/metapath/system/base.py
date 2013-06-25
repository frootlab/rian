# -*- coding: utf-8 -*-
import metapath.common as mp
import copy

class system:

    _config = None
    _params = None

    # generic system configuration methods

    def __init__(self, *args, **kwargs):
        """
        Initialize and configure system.
        """
        self._params = {}
        self._config = {}
        self.configure(*args, **kwargs)

    def configure(self, *args, **kwargs):
        """
        Configure system and subsystems to network and dataset.
        """
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            mp.log('info', 'System does not need to be configured')
            return True
        return self._configure(*args, **kwargs)

    def getName(self):
        """
        Return name of system
        """
        return self._config['name']

    def _get(self, sec = None):
        """
        Return all system settings (config, params) as dictionary.
        """
        dict = {
            'config': copy.deepcopy(self._config),
            'params': copy.deepcopy(self._params) }
        if not sec:
            return dict
        if sec in dict:
            return dict[sec]
        return False

    def _set(self, **dict):
        """
        Set system settings (config, params) from dictionary.
        """
        if 'config' in dict:
            ## 2Do
            ## IF the set command gets another package or class -> Error!
            self._config = copy.deepcopy(dict['config'])
        if 'params' in dict:
            self._params = copy.deepcopy(dict['params'])
        return True

    def isEmpty(self):
        """
        Return true if system is a dummy
        """
        return False

    def isConfigured(self):
        """
        Return configuration state of system
        """
        return self._isConfigured()

    def getConfig(self):
        """
        Return system configuration as dictionary.
        """
        return self._config.copy()

    def setNetwork(self, *args, **kwargs):
        """
        Update units and links to network instance.
        """
        return self._setNetwork(*args, **kwargs)

    def setDataset(self, *args, **kwargs):
        """
        Update units and links to dataset instance.
        """
        return self._setDataset(*args, **kwargs)

    def getName(self):
        """
        Return name of system
        """
        return self._config['name'] if 'name' in self._config else ''

    def setName(self, name):
        """
        Set name of system
        """
        if not isinstance(name, str):
            return False
        self._config['name'] = name
        return True

    def getClass(self):
        """
        Return class of system
        """
        return self._config['class']
    
    def getType(self):
        """
        Return type of system
        """
        return '%s.%s' % (self._config['package'], self._config['class'])

    def getDescription(self):
        """
        Return description of system
        """
        return self.__doc__

    # generic data methods

    def getDataEval(self, data, **kwargs):
        """
        Return system specific data evaluation.
        """
        return self._getDataEval(data, **kwargs)

    def getDataRepresentation(self, data, **kwargs):
        """
        Return system representation of data.
        """
        return self._getDataRepresentation(data, **kwargs)

    # generic parameter methods

    def initParams(self, dataset, *args, **kwargs):
        """
        Initialize system parameters using dataset instance.
        """
        if not mp.isDataset(dataset): # check dataset instance
            mp.log("error", "could not initilize system parameters: invalid 'dataset' instance given!")
            return False
        if 'samples' in self._config['params']: # using row filter
            data = dataset.getData(100000, rows = self._config['params']['samples'])
        else:
            data = dataset.getData(100000)
        return self._initParams(data) # initilize parameters

    def getParams(self, *args, **kwargs):
        """
        Return dictinary with all system parameters.
        """
        return copy.deepcopy(self._params)

    def setParams(self, params, update = True):
        """
        Set system parameters using from dictionary.
        """
        if not self._checkParams(params): # check parameter dictionary
            mp.log("error", "could not set system parameters: invalid 'params' dictionary given!")
            return False
        if update:
            self._setParams(params)
        else: # without update just overwrite local params
            self._params = copy.deepcopy(params)
        return True

    def resetParams(self, dataset):
        """
        Reset system parameters using dataset instance.
        """
        return self.initParams(dataset)

    def optimizeParams(self, *args, **kwargs):
        """
        Optimize System parameters using dataset and preferred algorithm.
        """
        return self._optimizeParams(*args, **kwargs)

    # generic unit methods

    def getUnits(self, *args, **kwargs):
        """
        Return labels of units in system.
        """
        return self._getUnitsFromSystem(*args, **kwargs)

    def getUnitInfo(self, label, *args, **kwargs):
        """
        Return dictionary with information about a specific unit.
        """
        return self._getUnitInformation(label)

    def getUnitEval(self, data, **kwargs):
        """
        Return dictionary with units and evaluation values.
        """
        return self._getUnitEval(data, **kwargs)

    def getUnitEvalInfo(self, *args, **kwargs):
        """
        Return information about unit evaluation functions.
        """
        return self._getUnitEvalInformation(*args, **kwargs)

    def setUnits(self, units = [], update = False, *args, **kwargs):
        """
        Set units and update system parameters.
        """
        if update:
            if not self._checkParams(self._params):
                mp.log("error", "could not update units: units have not yet been set!")
                return False
            backup = self.getParams()
            self._setUnits(units)
            self._initParams()
            return self.setParams(backup)

        self._setUnits(units)
        self._initParams()
        return True

    def unlinkUnit(self, unit, *args, **kwargs):
        """
        Unlink unit (if present).
        """
        return self._unlinkUnit(unit)

    def getLinkEval(self, data, **kwargs):
        """
        Return dictionary with links and evaluation values.
        """
        return self._getLinkEval(data, **kwargs)

    # generic link methods

    def getLinks(self, *args, **kwargs):
        """
        Return list with 2-tuples containing unit labels.
        """
        return self._getLinksFromConfig()

    def setLinks(self, links = [], update = False, *args, **kwargs):
        """
        Set links using list with 2-tuples containing unit labels.
        """
        return self._setLinks(links)

    def removeLinks(self, links = [], *args, **kwargs):
        """
        Remove links from system using list with 2-tuples containing unit labels.
        """
        return self._removeLinks(links)

    def removeLinksByThreshold(self, method = None, threshold = None, *args, **kwargs):
        """
        Remove links from system using a threshold for link parameters.
        """
        return self._removeLinksByThreshold(method, threshold)

    def getLinkParams(self, links = [], *args, **kwargs):
        """
        Return parameters of links.
        """
        return self._getLinkParams(links)

class empty(system):

    def __init__(self, *args, **kwargs):
        self._config = {
            'package': 'base',
            'class': 'empty',
            'description': 'dummy system',
            'name': 'empty' }

    def isEmpty(self, *args, **kwargs):
        """
        Return true if system is just a dummy
        """
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
