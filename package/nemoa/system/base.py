#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, copy, numpy, time

class system:
    """Base class for graphical models."""

    ####################################################################
    # System configuration                                             #
    ####################################################################

    def __init__(self, *args, **kwargs):
        """Initialize system configuration and system parameter configuration."""
    
        # set configuration and update units and links
        self.setConfig(kwargs['config'] if 'config' in kwargs else {})

    def configure(self, dataset = None, network = None, *args, **kwargs):
        """Configure system and subsystems to network and dataset."""
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            return True
        nemoa.log("configure system '%s'" % (self.name()))
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
        retVal = self._configure(dataset = dataset, network = network,
            *args, **kwargs)
        nemoa.setLog(indent = '-1')
        return retVal

    def setName(self, name):
        """Set name of system."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def getConfig(self):
        """Return system configuration as dictionary."""
        return self._config.copy()

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
        if not hasattr(self, '_params'): self._params = {}
        self.setUnits(self._getUnitsFromConfig())
        self.setLinks(self._getLinksFromConfig())

        self._config['check']['config'] = True
        return True

    def isConfigured(self):
        """Return configuration state of system."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    def setNetwork(self, *args, **kwargs):
        """Update units and links to network instance."""
        return self._setNetwork(*args, **kwargs)

    def updateNetwork(self, network):
        """update params in network."""
        if not nemoa.type.isNetwork(network): return False
        G = network.graph
        for u, v, d in G.edges(data = True):
            params = self.getLink((u, v))
            if not params: params = self.getLink((v, u))
            if not params: continue
            nemoa.common.dictMerge(params, G[u][v]['params'])
            G[u][v]['weight'] = params['weight']
        return True

    def checkNetwork(self, network, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isNetwork(network): return False
        if not (hasattr(self.__class__, '_checkNetwork') \
            and callable(getattr(self.__class__, '_checkNetwork'))):
            return True
        return self._checkNetwork(network)

    def setDataset(self, *args, **kwargs):
        """Update units and links to dataset instance."""
        return self._setDataset(*args, **kwargs)

    def checkDataset(self, dataset, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isDataset(dataset): return False
        if not (hasattr(self.__class__, '_checkDataset') \
            and callable(getattr(self.__class__, '_checkDataset'))):
            return True
        return self._checkDataset(dataset)

    def isEmpty(self):
        """Return true if system is a dummy."""
        return False

    ####################################################################
    # Units                                                            #
    ####################################################################

    def getUnits(self, **kwargs):
        """Return tuple with lists of units that match a given property.

        Examples:
            return visible units: getUnits(visible = True)"""

        filter = []
        for key in kwargs.keys():
            if key == 'group':
                key = 'name'
                kwargs['name'] = kwargs['group']
            if key in self._params['units'][0].keys():
                filter.append((key, kwargs[key]))
        groups = ()
        for group in self._params['units']:
            valid = True
            for key, val in filter:
                if not group[key] == val:
                    valid = False
                    break
            if valid:
                groups += (group['label'], )
        return groups

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

    def getUnitInfo(self, *args, **kwargs):
        """Return dictionary with information about a specific unit."""
        return self._getUnitInformation(*args, **kwargs)

    def getUnitEval(self, *args, **kwargs):
        """Return dictionary with units and evaluation values."""
        return self._getUnitEval(*args, **kwargs)

    def unlinkUnit(self, unit):
        """Unlink unit (if present)."""
        return self._unlinkUnit(unit)

    def removeUnits(self, type, label):
        """Remove unit."""
        return self._removeUnit(type, label)

    ####################################################################
    # Unit groups                                                      #
    ####################################################################

    def getGroups(self, **kwargs):
        """Return tuple with groups that match a given property.

        Examples:
            return visible groups:
                getGroups(visible = True)
            search for group 'MyGroup':
                getGroups(name = 'MyGroup')"""

        filter = []
        for key in kwargs.keys():
            if key in self._params['units'][0].keys():
                filter.append((key, kwargs[key]))
        groups = ()
        for group in self._params['units']:
            valid = True
            for key, val in filter:
                if not group[key] == val:
                    valid = False
                    break
            if valid:
                groups += (group['name'], )
        return groups

    def getGroupOfUnit(self, unit):
        """Return name of unit group of given unit."""
        for id in range(len(self._params['units'])):
            if unit in self._params['units'][id]['label']:
                return self._params['units'][id]['name']
        return None

    ####################################################################
    # Links                                                            #
    ####################################################################

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

    def getLinks(self, *args, **kwargs):
        """Return list with 2-tuples containing unit labels."""
        return self._getLinksFromConfig()

    def removeLinks(self, links = [], *args, **kwargs):
        """Remove links from system using list with 2-tuples containing unit labels."""
        return self._removeLinks(links)

    #def removeLinksByThreshold(self, method = None, threshold = None, *args, **kwargs):
        #"""Remove links from system using a threshold for link parameters."""
        #return self._removeLinksByThreshold(method, threshold)

    def getLink(self, link):
        srcUnit = link[0]
        tgtUnit = link[1]
        srcGrp  = self.getGroupOfUnit(srcUnit)
        tgtGrp  = self.getGroupOfUnit(tgtUnit)
        if not srcGrp in self._links \
            or not tgtGrp in self._links[srcGrp]['target']:
            return None
        linkGrp = self._links[srcGrp]['target'][tgtGrp]
        srcID   = self.units[srcGrp].params['label'].index(srcUnit)
        tgtID   = self.units[tgtGrp].params['label'].index(tgtUnit)
        return {
            'adjacency': linkGrp['A'][srcID, tgtID],
            'weight': linkGrp['W'][srcID, tgtID]}

    def getLinkParams(self, links = [], *args, **kwargs):
        """Return parameters of links."""
        return self._getLinkParams(links)

    def getLinkEval(self, data, **kwargs):
        """Return dictionary with links and evaluation values."""
        return self._getLinkEval(data, **kwargs)
        
    
    
    
        
        
        
        
        


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

    ####################################################################
    # System parameter modification                                    #
    ####################################################################

    def initParams(self, dataset = None):
        """Initialize system parameters.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Initialize all system parameters to dataset."""
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
            nemoa.log('error', """
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

    ####################################################################
    # Common network tests                                             #
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
                all middle layers of the network are hidden"""
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
                nemoa.log('error',
                    'Feedforward networks do not allow empty layers!')
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
                related to their number of nodes"""
        if not nemoa.type.isNetwork(network): return nemoa.log('error',
            'could not test network: invalid network instance given!')
        if not self._isNetworkMLPCompatible(network): return False
        if not len(network.layers()) % 2 == 1: return nemoa.log('error',
            'DBN / Autoencoder networks expect an odd number of layers!')

        layers = network.layers()
        size = len(layers)
        for id in range(1, (size - 1) / 2):
            symmetric = len(network.layer(layers[id])['nodes']) \
                == len(network.layer(layers[-id-1])['nodes'])
            if not symmetric: return nemoa.log('error',
                """DBN / Autoencoder networks expect a symmetric
                number of hidden nodes, related to their central layer!""")
        return True

    ####################################################################
    # Common dataset tests                                             #
    ####################################################################

    def _isDatasetBinary(self, dataset = None):
        """Test if a dataset contains only binary data.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Return True if a given dataset contains only binary data."""

        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')

        data = dataset.getData()

        binary = ((data == data.astype(bool)).sum() == data.size)

        if not binary: return nemoa.log('error',
            'The dataset does not contain binary data!')

        return True

    def _isDatasetGaussNormalized(self, dataset = None):
        """Test if a dataset contains gauss normalized data.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Return True if the following conditions are satisfied:
            (1) The absolute mean value of a given number of random samples
                of the dataset is below a given maximum (default 0.05)
            (2) The standard deviation of a given number of random samples
                of the dataset is below a given maximum (default 1.05)"""

        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')

        size    = 100000 # number of samples
        maxMean = 0.05   # allowed maximum for absolute mean value
        maxSdev = 1.05   # allowed maximum for standard deviation

        data = dataset.getData(size)

        mean = data.mean()
        if numpy.abs(mean) >= maxMean: return  nemoa.log('error', """
            The dataset does not contain gauss normalized data:
            The mean value is %.3f!""" % (mean))

        sdev = data.std()
        if sdev >= maxSdev: return nemoa.log('error', """
            The dataset does not contain gauss normalized data:
            The standard deviation is %.3f!""" % (sdev))

        return True

    ####################################################################
    # Evaluate                                                         #
    ####################################################################

    def getDataEval(self, data, **kwargs):
        """Return system specific data evaluation."""
        return self._getDataEval(data, **kwargs)

    def assertUnitTuple(self, units = None):
        """Return tuple with lists of valid input and output units."""

        mapping = self.getMapping()
        if units == None: return (self.getUnits(group = mapping[0])[0], \
            self.getUnits(group = mapping[-1])[0])
        if isinstance(units[0], str):
            units[0] = self.getUnits(group = units[0])[0]
        elif isinstance(units[0], list): pass
        if isinstance(units[1], str):
            units[1] = self.getUnits(group = units[1])[0]
        elif isinstance(units[1], list): pass

        elif isinstance(units[0], list) and isinstance(units[1], list):
            #2do: test if units are valid
            pass
        else:
            nemoa.log('error', """could not evaluate unit relations:
                parameter units has invalid format!""")
            return None    

        return units
    
    def getUnitRelation(self, dataset, stat = 10000, units = None,
        relation = 'correlation()', format = 'array', **kwargs):

        # get mapping, data and units
        mapping = self.getMapping()
        data    = dataset.getData(cols = (mapping[0], mapping[-1]))
        units   = self.assertUnitTuple(units)

        # get method and method specific parameters
        method, ukwargs = nemoa.common.strSplitParams(relation)
        params = nemoa.common.dictMerge(ukwargs, kwargs)

        # get relation as numpy array
        if method == 'correlation': M = self.getUnitCorrelation(\
            units = units, data = data, **params)
        elif method == 'causality': M = self.getUnitCausality(\
            units = units, data = data, mapping = mapping, **params)
        elif method == 'propagation': M = self.getUnitPropagation(\
            units = units, data = data, mapping = mapping, **params)
        else: return nemoa.log('error',
            "could not evaluate unit relations: unknown relation '%s'" % (method))

        # transform matrix
        if 'transform' in params:
            if 'C' in params['transform']:
                C = self.getUnitCorrelationMatrix(units = units, data = data)
            try:
                T = eval(params['transform'])
                M = T
            except: nemoa.log('error',
                "could not transform unit relation matrix: invalid syntax!")

        # create formated output
        if format == 'array': return M
        if format == 'dict': return nemoa.common.dictFromArray(M, units)

    def getUnitCorrelation(self, units = None, data = None, **kwargs):
        """Return correlation matrix as numpy array.

        Keyword arguments:
            units -- list of strings with valid unitIDs"""

        # create data and calulate correlation matrix
        if units == None: units = self.assertUnitTuple(units)

        M = numpy.corrcoef(numpy.hstack(data).T)
        uList = units[0] + units[1]

        # create output matrix
        C = numpy.zeros(shape = (len(units[0]), len(units[1])))
        for i, u1 in enumerate(units[0]):
            k = uList.index(u1)
            for j, u2 in enumerate(units[1]):
                l = uList.index(u2)
                C[i, j] = M[k, l]

        return C

    def getUnitCausality(self, units, data = None, mapping = None,
        modify = 'knockout', eval = 'error', **kwargs):
        """Return numpy array with data manipulation results.

        Keyword Arguments:
            y -- list with labels of manipulated units on y axis of matrix
            x -- list with labels of effected units on x axis of matrix+
            modify -- type of manipulation
            measure -- name of measurement function
            data -- numpy array with data to test

        Description:
            Manipulate unit values and measure effect on other units,
            respective to given data"""

        # prepare causality matrix
        if units == None: units = self.assertUnitTuple(units)
        K = numpy.zeros((len(units[0]), len(units[1])))

        # calculate unit values without modification
        methodName = self.about('units', 'method', eval, 'name')
        nemoa.log(
            'calculate %s effect on %s' % (modify, methodName))
        tStart = time.time()
        default = self.getUnitEval(eval = eval, \
            data = data, mapping = mapping)
        estimation = (time.time() - tStart) * len(units[0])
        nemoa.log(
            'estimated duration: %.1fs' % (estimation))

        srcUnits = self.getUnits(group = mapping[0])[0]

        modi = {}
        for i, srcUnit in enumerate(units[0]):

            # modify unit and calculate unit values
            if modify == 'knockout':
                id = srcUnits.index(srcUnit)
                modi = self.getUnitEval(eval = eval,
                    data = data, mapping = mapping, block = [id])
            #2DO: fix unlink
            #elif modify == 'unlink':
                #links = self.getLinks()
                #self.unlinkUnit(kUnit)
                #uUnlink = self.getUnitEval(func = measure, data = data)
                #self.system.setLinks(links)
            else: return nemoa.log('error', """could not create causality matrix:
                unknown data manipulation function '%s'!""" % (modify))

            # store difference in causality matrix
            for j, tgtUnit in enumerate(units[1]):
                if srcUnit == tgtUnit:
                    continue
                K[i,j] = modi[tgtUnit] - default[tgtUnit]

        return K

    def getUnitPropagation(self, units, data = None, mapping = None,
        modify = 'knockout', eval = 'values', **kwargs):
        """Return data propagation matrix as numpy array."""
        
        # create empty array
        M = numpy.empty(shape = (len(units[0]), len(units[1])))
        meanData = data[0].mean(axis = 0).reshape((1, len(units[0])))
        for i, inUnit in enumerate(units[0]):
            posData = meanData.copy()
            posData[0, i] += 0.5
            negData = meanData.copy()
            negData[0, i] -= 0.5
            for o, outUnit in enumerate(units[1]):
                M[i, o] = self.getUnitEval(eval = 'expect',
                    data = posData, mapping = mapping)[outUnit] \
                    - self.getUnitEval(eval = 'expect',
                    data = negData, mapping = mapping)[outUnit]

        return M

    ####################################################################
    # Data Transformation                                              #
    ####################################################################

    def mapData(self, data, mapping = None, transform = 'expect'):
        """Return system representation of data.

        Keyword Arguments:
            mapping -- tuple of strings describing the mapping function
            transform -- mapping algorithm"""

        if mapping == None: mapping = self.getMapping()
        if transform == 'expect': return self.getUnitExpect(data, mapping)
        if transform == 'value':  return self.getUnitValues(data, mapping)
        if transform == 'sample': return self.getUnitSamples(data, mapping)
        return nemoa.log('error', """could not map data:
            unknown mapping algorithm '%s'""" % (transform))

    ####################################################################
    # Metadata of System                                               #
    ####################################################################

    def about(self, *args):
        """Return generic information about various parts of the system.
        
        Arguments:
            *args -- tuple of strings, containing a breadcrump trail to
                a specific information about the system

        Examples:
            about('units', 'measure', 'error')
                Returns information about the "error" measurement
                function of the systems units."""
        if args[0] in ['units', 'links']:
            if args[1] == 'method':
                if args[0] == 'units': methods = self.getUnitMethods()
                if args[0] == 'links': methods = self.getLinkMethods()
                if not args[2] in methods.keys(): return None
                if not args[3] in methods[args[2]].keys(): return None
                return methods[args[2]][args[3]]
        if args[0] == 'name': return self.name()
        if args[0] == 'class': return self.getClass()
        if args[0] == 'type': return self.getType()
        if args[0] == 'description': return getDescription()
        return None

    def name(self):
        """Return name of system."""
        return self._config['name'] #if 'name' in self._config else ''

    def getClass(self):
        """Return class of system."""
        return self._config['class']

    def getType(self):
        """Return type of system."""
        return '%s.%s' % (self._config['package'], self._config['class'])

    def getDescription(self):
        """Return description of system."""
        return self.__doc__

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

    def writeToStore(self, id = -1, append = False, **kwargs):
        if len(self.__store) == (abs(id) - 1) or append == True:
            self.__store.append(kwargs)
            return True
        if len(self.__store) < id:
            nemoa.log('error', """
                could not write to store, wrong index!""")
            return False
        self.__store[id] = kwargs
        return True

    def readFromStore(self, id = -1):
        return self.__store[id] if len(self.__store) >= abs(id) else {}

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
                nemoa.log("""
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
                nemoa.log('estimation: %ds (finishing time: %s)'
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
                nemoa.log('final: %s = %.3f' % (measure, value))
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
                nemoa.log("""finished %.1f%%: %s = %0.4f""" \
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
