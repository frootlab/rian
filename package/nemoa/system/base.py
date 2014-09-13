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
                    self._config[key] = self._default(key)

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

    def _isEmpty(self):
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
            if valid: groups += (group['label'], )
        return groups

    def setUnits(self, units = None, initialize = True):
        """Set units and update system parameters."""
        if not 'units' in self._params: self._params['units'] = []
        if not hasattr(self, 'units'): self.units = {}
        if initialize: return self._setUnits(units) and self._initUnits()
        return self._setUnits(units)

    def getUnitInfo(self, *args, **kwargs):
        """Return dictionary with information about a specific unit."""
        return self._getUnitInformation(*args, **kwargs)

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
            if valid: groups += (group['name'], )
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
        if not 'links' in self._params: self._params['links'] = {}
        if not hasattr(self, 'links'): self.links = {}
        if initialize: return self._setLinks(links) \
            and self._indexLinks() and self._initLinks()
        return self._indexLinks()

    def getLinks(self, *args, **kwargs):
        """Return list with 2-tuples containing unit labels."""
        return self._getLinksFromConfig()

    def removeLinks(self, links = [], *args, **kwargs):
        """Remove links from system using list with 2-tuples containing unit labels."""
        return self._removeLinks(links)

    def getLink(self, link):
        srcUnit = link[0]
        tgtUnit = link[1]
        srcGrp  = self.getGroupOfUnit(srcUnit)
        tgtGrp  = self.getGroupOfUnit(tgtUnit)
        if not srcGrp in self._links \
            or not tgtGrp in self._links[srcGrp]['target']: return None
        linkGrp = self._links[srcGrp]['target'][tgtGrp]
        srcID   = self.units[srcGrp].params['label'].index(srcUnit)
        tgtID   = self.units[tgtGrp].params['label'].index(tgtUnit)
        weight  = linkGrp['W'][srcID, tgtID]
        norm    = float(numpy.sum(linkGrp['A'])) / numpy.sum(numpy.abs(linkGrp['W']))
        return {
            'adjacency': linkGrp['A'][srcID, tgtID],
            'weight':    weight,
            'normal':    norm * weight}

    #def getLinkParams(self, links = [], *args, **kwargs):
        #"""Return parameters of links."""
        #return self._getLinkParams(links)

    def _get(self, sec = None):
        """Return all system settings (config, params) as dictionary."""
        dict = {
            'config': copy.deepcopy(self._config),
            'params': copy.deepcopy(self._params) }
        if not sec: return dict
        if sec in dict: return dict[sec]
        return False

    def _set(self, **dict):
        """Set system settings (config, params) from dictionary."""
        ## 2do!: if another package or class -> Error!

        if 'config' in dict: self._config = copy.deepcopy(dict['config'])
        if 'params' in dict: self._params = copy.deepcopy(dict['params'])
        return self._updateUnitsAndLinks()

    ####################################################################
    # System parameter modification                                    #
    ####################################################################

    def initParams(self, dataset = None):
        """Initialize system parameters.

        Keyword Arguments:
            dataset -- nemoa dataset instance

        Description:
            Initialize all system parameters to dataset."""
        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            """could not initilize system parameters:
            invalid dataset instance given!""")
        return self._initParams(dataset)

    def getParams(self, *args, **kwargs):
        """Return dictinary with all system parameters."""
        return copy.deepcopy(self._params)

    def setParams(self, params, update = True):
        """Set system parameters using from dictionary."""
        if not self._checkParams(params): return nemoa.log('error',
            """could not set system parameters:
            invalid 'params' dictionary given!""")
        if update: self._setParams(params)
        else: self._params = copy.deepcopy(params)
        return True

    def resetParams(self, dataset):
        """Reset system parameters using dataset instance."""
        return self.initParams(dataset)

    def optimizeParams(self, dataset, schedule):
        """Optimize system parameters using data and given schedule."""

        # check if optimization schedule exists for current system
        # and merge default, existing and given schedule
        if not 'params' in schedule:
            config = self._default('optimize')
            nemoa.common.dictMerge(self._config['optimize'], config)
            self._config['optimize'] = config
        elif not self.getType() in schedule['params']: return nemoa.log(
            'error', """could not optimize model:
            optimization schedule '%s' does not include system '%s'
            """ % (schedule['name'], self.getType()))
        else:
            config = self._default('optimize')
            nemoa.common.dictMerge(self._config['optimize'], config)
            nemoa.common.dictMerge(schedule['params'][self.getType()], config)
            self._config['optimize'] = config

        ################################################################
        # System independent optimization settings                     #
        ################################################################

        # check dataset
        if (not 'checkDataset' in config or config['checkDataset'] == True) \
            and not self._checkDataset(dataset): return False

        # initialize inspector
        inspector = nemoa.system.base.inspector(self)
        if 'inspect' in config and not config['inspect'] == False:
            inspector.setTestData(self._getTestData(dataset))

        # optimize system parameters
        algorithm = config['algorithm'].title()
        nemoa.log('note', "optimize '%s' (%s) using algorithm '%s'" % \
            (self.name(), self.getType(), algorithm))
        nemoa.setLog(indent = '+1')
        retVal = self._optParams(dataset, schedule, inspector)
        nemoa.setLog(indent = '-1')

        return retVal

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
        if not nemoa.type.isNetwork(network): return nemoa.log('error',
            'could not test network: invalid network instance given!')
        if len(network.layers()) < 3: return nemoa.log('error',
            'Multilayer networks need at least three layers!')
        for layer in network.layers():
            if not len(network.layer(layer)['nodes']) > 0: return nemoa.log(
                'error', 'Feedforward networks do not allow empty layers!')
            if not network.layer(layer)['visible'] \
                == (layer in [network.layers()[0], network.layers()[-1]]):
                return nemoa.log('error', """The first and the last layer
                    of a multilayer feedforward network have to be visible,
                    middle layers have to be hidden!""")
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
        if numpy.abs(mean) >= maxMean: return nemoa.log('error', """
            The dataset does not contain gauss normalized data:
            The mean value is %.3f!""" % (mean))

        sdev = data.std()
        if sdev >= maxSdev: return nemoa.log('error', """
            The dataset does not contain gauss normalized data:
            The standard deviation is %.3f!""" % (sdev))

        return True

    ####################################################################
    # System Evaluation                                                #
    ####################################################################

    def eval(self, data, *args, **kwargs):
        if len(args) == 0:
            return self.evalSystem(data, **kwargs)
        if args[0] == 'units':
            return self.evalUnits(data, *args[1:], **kwargs)
        if args[0] == 'links':
            return self.evalLinks(data, *args[1:], **kwargs)
        if args[0] == 'relations':
            return self.evalRelations(data, *args[1:], **kwargs)
        if args[0] in self._getSystemEvalMethods().keys():
            return self.evalSystem(data, *args, **kwargs)
        return nemoa.log('warning',
            "could not evaluate system: unknown method '%s'" % (args[0]))

    ####################################################################
    # Evaluate                                                         #
    ####################################################################

    @staticmethod
    def getDataSum(data, norm = 'S'):
        """Return sum of data.

        Keyword Arguments:
            data -- numpy array containing data
            norm -- data mean norm
                'S': Sum of Values
                'SE', 'L1': Sum of Errors / L1 Norm
                'SSE': Sum of Squared Errors
                'RSSE': Root Sum of Squared Errors
                default: 'S' """

        norm = norm.upper()

        # Sum of Values (S)
        if norm in ['S']: return numpy.sum(data, axis = 0)
        # Sum of Errors (SE) / L1-Norm (L1)
        if norm in ['SE', 'L1']: return numpy.sum(numpy.abs(data), axis = 0)
        # Sum of Squared Errors (SSE)
        if norm in ['SSE']: return numpy.sum(data ** 2, axis = 0)
        # Root Sum of Squared Errors (RSSE)
        if norm in ['RSSE']: return numpy.sqrt(numpy.sum(data ** 2, axis = 0))

        return nemoa.log('error', "unknown data sum norm '%s'" % (norm))

    @staticmethod
    def getDataMean(data, norm = 'M'):
        """Return mean of data.

        Keyword Arguments:
            data -- numpy array containing data
            norm -- data mean norm
                'M': Arithmetic Mean of Values
                'ME': Mean of Errors
                'MSE': Mean of Squared Errors
                'RMSE', 'L2': Root Mean of Squared Errors / L2 Norm
                default: 'M' """

        norm = norm.upper()

        # Mean of Values (M)
        if norm in ['M']: return numpy.mean(data, axis = 0)
        # Mean of Errors (ME)
        if norm in ['ME']: return numpy.mean(numpy.abs(data), axis = 0)
        # Mean of Squared Errors (MSE)
        if norm in ['MSE']: return numpy.mean(data ** 2, axis = 0)
        # Root Mean of Squared Errors (RMSE) / L2-Norm (L2)
        if norm in ['RMSE', 'L2']: return numpy.sqrt(numpy.mean(data ** 2, axis = 0))

        return nemoa.log('error', "unknown data mean norm '%s'" % (norm))

    @staticmethod
    def getDataDeviation(data, norm = 'SD'):
        """Return deviation of data.

        Keyword Arguments:
            data -- numpy array containing data
            norm -- data deviation norm
                'SD': Standard Deviation of Values
                'SDE': Standard Deviation of Errors
                'SDSE': Standard Deviation of Squared Errors
                default: 'SD' """

        norm = norm.upper()

        # Standard Deviation of Data (SD)
        if norm in ['SD']: return numpy.std(data, axis = 0)
        # Standard Deviation of Errors (SDE)
        if norm in ['SDE']: return numpy.std(numpy.abs(data), axis = 0)
        # Standard Deviation of Squared Errors (SDSE)
        if norm in ['SDSE']: return numpy.std(data ** 2, axis = 0)

        return nemoa.log('error', "unknown data deviation norm '%s'" % (deviation))

    def _assertUnitTuple(self, units = None):
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
        else: return nemoa.log('error', """could not evaluate unit relations:
            parameter units has invalid format!""")

        return units

    ####################################################################
    # Data Transformation                                              #
    ####################################################################

    def mapData(self, data, mapping = None, transform = 'expect'):
        """Return system representation of data.

        Keyword Arguments:
            mapping -- tuple of strings describing the mapping function
            transform -- mapping algorithm"""

        if mapping == None: mapping = self.getMapping()
        if transform == 'expect': return self.evalUnitExpect(data, mapping)
        if transform == 'value':  return self.evalUnitValues(data, mapping)
        if transform == 'sample': return self.evalUnitSamples(data, mapping)
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
            about('units', 'error')
                Returns information about the "error" measurement
                function of the systems units."""

        # create information dictionary
        about = nemoa.common.dictMerge({
            'name': self.name(),
            'description': self.__doc__,
            'class': self._config['class'],
            'type': self.getType(),
            'units': self._getUnitEvalMethods(),
            'links': self._getLinkEvalMethods(),
            'relations': self._getRelationEvalMethods()
        }, self._getSystemEvalMethods())

        retDict = about
        path = ['system']
        for arg in args:
            if not isinstance(retDict, dict): return retDict
            if not arg in retDict.keys(): return nemoa.log(
                'warning', "%s has no property '%s'" % (' → '.join(path), arg))
            path.append(arg)
            retDict = retDict[arg]
        if not isinstance(retDict, dict): return retDict
        return {key: retDict[key] for key in retDict.keys()}

    def name(self):
        """Return name of system."""
        return self._config['name'] #if 'name' in self._config else ''

    def getType(self):
        """Return sytem type."""
        return '%s.%s' % (self._config['package'], self._config['class'])

class empty(system):

    def __init__(self, *args, **kwargs):
        self._config = {
            'package': 'base',
            'class': 'empty',
            'description': 'dummy system',
            'name': 'empty' }

    def _isEmpty(self, *args, **kwargs): return True
    def configure(self, *args, **kwargs): return True
    def setConfig(self, *args, **kwargs): return True
    def setNetwork(self, *args, **kwargs): return True
    def setDataset(self, *args, **kwargs): return True
    def _getUnitsFromNetwork(self, *args, **kwargs): return True
    def _getLinksFromNetwork(self, *args, **kwargs): return True
    def setUnits(self, *args, **kwargs): return True
    def setLinks(self, *args, **kwargs): return True
    def initParams(self, *args, **kwargs): return True

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
        if not nemoa.type.isSystem(system): return nemoa.log('warning',
            'could not configure inspector: system is not valid!')
        if not hasattr(system, '_config'): return nemoa.log('warning',
            'could not configure inspector: system contains no configuration!')
        if not 'optimize' in system._config: return nemoa.log('warning',
            'could not configure inspector: system contains no configuration for optimization!')

        # link system
        self.__system = system
        self.__inspect = system._config['optimize']['inspect'] \
            if 'inspect' in system._config['optimize'] \
            else True
        self.__estimate = system._config['optimize']['inspectEstimateTime'] \
            if 'inspectEstimateTime' in system._config['optimize'] \
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
        if len(self.__store) < id: return nemoa.log('error',
            'could not write to store, wrong index!')
        self.__store[id] = kwargs
        return True

    def readFromStore(self, id = -1):
        return self.__store[id] if len(self.__store) >= abs(id) else {}

    def difference(self):
        if not 'inspection' in self.__state: return 0.0
        if self.__state['inspection'] == None: return 0.0
        if self.__state['inspection'].shape[0] < 2: return 0.0
        return self.__state['inspection'][-1, 1] - \
            self.__state['inspection'][-2, 1]

    def trigger(self):
        """Update epoch and time and calculate """

        cfg = self.__system._config['optimize']
        epochTime = time.time()

        if self.__state == {}: self.__initState()

        self.__state['epoch'] += 1

        # check keyboard input
        self.__triggerKeyEvent()

        # estimate time needed to finish current optimization schedule
        if self.__estimate and not self.__state['estimateEnded']:
            if not self.__state['estimateStarted']:
                nemoa.log("""
                    estimating time for calculation
                    of %i updates ...""" % (cfg['updates']))
                self.__state['estimateStarted'] = True
            if (epochTime - self.__state['startTime']) \
                > cfg['inspectEstimateTimeWait']:
                estim = ((epochTime - self.__state['startTime']) \
                    / (self.__state['epoch'] + 1)
                    * cfg['updates'] * cfg['iterations'])
                estimStr = time.strftime('%H:%M',
                    time.localtime(time.time() + estim))
                nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                    % (estim, estimStr))
                self.__state['estimateEnded'] = True

        # evaluate model (in a given time interval)
        if self.__inspect: self.__triggerEval()

        if self.__state['abort']: return 'abort'

        return True

    def __initState(self):

        epochTime = time.time()

        nemoa.log('note', "press 'q' if you want to abort the optimization")
        self.__state = {
            'startTime': epochTime,
            'epoch': 0,
            'inspection': None,
            'abort': False}
        if self.__inspect: self.__state['inspectTime'] = epochTime
        if self.__estimate:
            self.__state['estimateStarted'] = False
            self.__state['estimateEnded'] = False

        return True

    def __triggerKeyEvent(self):
        """Check Keyboard."""

        c = nemoa.common.getch()
        if isinstance(c, str):
            if c == 'q':
                nemoa.log('note', '... aborting optimization')
                self.__system._config['optimize']['updates'] = \
                    self.__state['epoch']
                self.__state['abort'] = True

        return True

    def __triggerEval(self):
        """Evaluate Model."""

        cfg = self.__system._config['optimize']
        epochTime = time.time()

        if self.__data == None:
            nemoa.log('warning', """
                monitoring the process of optimization is not possible:
                testdata is needed!""")
            self.__inspect = False
            return False

        if self.__state['epoch'] == cfg['updates']:
            func  = cfg['inspectFunction']
            prop  = self.__system.about(func)
            value = self.__system.eval(data = self.__data, func = func)
            out   = 'final: %s = ' + prop['format']
            return nemoa.log('note', out % (prop['name'], value))

        if ((epochTime - self.__state['inspectTime']) \
            > cfg['inspectTimeInterval']) \
            and not (self.__estimate \
            and self.__state['estimateStarted'] \
            and not self.__state['estimateEnded']):
            func  = cfg['inspectFunction']
            prop  = self.__system.about(func)
            value = self.__system.eval(data = self.__data, func = func)
            progr = float(self.__state['epoch']) / float(cfg['updates']) * 100.0

            # update time of last evaluation
            self.__state['inspectTime'] = epochTime

            # add evaluation to array
            if self.__state['inspection'] == None:
                self.__state['inspection'] = numpy.array([[progr, value]])
            else: self.__state['inspection'] = \
                numpy.vstack((self.__state['inspection'], \
                numpy.array([[progr, value]])))

            out = 'finished %.1f%%: %s = ' + prop['format']
            return nemoa.log('note', out % (progr, prop['name'], value))

        return False
