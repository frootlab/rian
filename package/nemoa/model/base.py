#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, copy, time, os

class model:
    """Base class for graphical models."""
    
    dataset = None
    network = None
    system  = None

    ####################################################################
    # Model configuration                                              #
    ####################################################################

    def __init__(self, config = {}, dataset = None, network = None, system = None, **kwargs):
        """Initialize model and configure dataset, network and system.

        Keyword Arguments:
            dataset -- dataset instance
            network -- network instance
            system  -- system instance
        """

        # initialize private scope class attributes
        self.__config = {}

        # update model name
        self.setName(kwargs['name'] if 'name' in kwargs else None)
        nemoa.log("""
            linking dataset, network and system instances to model""")

        self.dataset = dataset
        self.network = network
        self.system  = system

        if not self.isEmpty() and self.__checkModel():
            self.updateConfig()

    def __setConfig(self, config):
        """Set configuration from dictionary."""
        self.__config = config.copy()
        return True

    def __getConfig(self):
        """Return configuration as dictionary."""
        return self.__config.copy()

    def exportDataToFile(self, *args, **kwargs):
        """Export data to file."""
        return self.dataset.exportDataToFile(*args, **kwargs)

    def importConfigFromDict(self, dict):
        """Import numpy configuration from dictionary."""
        # copy dataset, network and system configuration
        keys = ['config', 'dataset', 'network', 'system']
        for key in keys:
            if not key in dict: return nemoa.log('error', """
                could not import configuration:
                given dictionary does not contain '%s' information!
                """ % (key))
        return {key: dict[key].copy() for key in keys}

    def __checkModel(self, allowNone = False):
        if (allowNone and self.dataset == None) \
            or not nemoa.type.isDataset(self.dataset):
            return False
        if (allowNone and self.network == None) \
            or not nemoa.type.isNetwork(self.network):
            return False
        if (allowNone and self.system == None) \
            or not nemoa.type.isSystem(self.system):
            return False
        return True

    def updateConfig(self):
        """Update model configuration."""

        # set version of model
        self.__config['version'] = nemoa.version()

        # set name of model
        if not 'name' in self.__config or not self.__config['name']:
            if not self.network.name():
                self.setName('%s-%s' % (
                    self.dataset.name(), self.system.name()))
            else:
                self.setName('%s-%s-%s' % (
                    self.dataset.name(), self.network.name(),
                    self.system.name()))
        return True

    def configure(self):
        """Configure model."""
        nemoa.log('configure model \'%s\'' % (self.name()))
        nemoa.setLog(indent = '+1')
        if not 'check' in self.__config:
            self.__config['check'] = {'dataset': False,
                'network': False, 'System': False}
        self.__config['check']['dataset'] = \
            self.dataset.configure(network = self.network)
        if not self.__config['check']['dataset']:
            nemoa.log('error', """could not configure model: dataset
                could not be configured!""")
            nemoa.setLog(indent = '-1')
            return False
        self.__config['check']['network'] = \
            self.network.configure(dataset = self.dataset,
                system = self.system)
        if not self.__config['check']['network']:
            nemoa.log('error', """could not configure model: network
                could not be configured!""")
            nemoa.setLog(indent = '-1')
            return False
        self.__config['check']['system'] = \
            self.system.configure(network = self.network,
                dataset = self.dataset)
        if not self.__config['check']['system']:
            nemoa.log('error', """could not configure model: system
                could not be configured!""")
            nemoa.setLog(indent = '-1')
            return False
        nemoa.setLog(indent = '-1')
        return True

    def __isConfigured(self):
        """Return True if model is allready configured."""
        return 'check' in self.__config \
            and self.__config['check']['dataset'] \
            and self.__config['check']['network'] \
            and self.__config['check']['system']

    ####################################################################
    # Model parameter modification methods                             #
    ####################################################################

    def initialize(self):
        """Initialize model parameters and return self."""

        #2DO: just check if system is configured

        # check if model is empty and can not be initialized
        if (self.dataset == None or self.system == None) \
            and self.isEmpty():
            return self

        # check if model is configured
        if not self.__isConfigured():
            nemoa.log('error', """could not initialize model parameters:
                model is not yet configured!""")
            return False

        # check dataset
        if not nemoa.type.isDataset(self.dataset):
            nemoa.log('error', """could not initialize model parameters:
                dataset is not yet configured!""")
            return False

        # check system
        if not nemoa.type.isSystem(self.system):
            nemoa.log('error', """could not initialize model parameters:
                system is not yet configured!""")
            return False
        elif self.system.isEmpty():
            return False

        # initialize system parameters
        self.system.initParams(self.dataset)
        
        # update network
        self.system.updateNetwork(self.network)

        return self

    def optimize(self, schedule = None, **kwargs):
        """Optimize system parameters."""

        #2DO: just check if system is initialized

        nemoa.log('optimize model')
        nemoa.setLog(indent = '+1')

        # check if model is empty
        if self.isEmpty():
            nemoa.log('warning', """
                empty models can not be optimized!""")
            nemoa.setLog(indent = '-1')
            return self

        # check if model is configured
        if not self.__isConfigured():
            nemoa.log('error', """
                could not optimize model:
                model is not yet configured!""")
            nemoa.setLog(indent = '-1')
            return False

        # get optimization schedule
        schedule = nemoa.workspace.getConfig(
            type = 'schedule', config = schedule,
            merge = ['params', self.system.name()],
            **kwargs)
        if not schedule:
            nemoa.log('error', """
                could not optimize system parameters:
                optimization schedule is not valid!""")
            nemoa.setLog(indent = '-1')
            return self
        
        # optimization of system parameters
        nemoa.log("""
            starting optimization schedule: '%s'
            """ % (schedule['name']))
        nemoa.setLog(indent = '+1')

        # 2DO: find better solution for multistage optimization
        if 'stage' in schedule and len(schedule['stage']) > 0:
            for stage, params in enumerate(config['stage']):
                self.system.optimizeParams(self.dataset, **params)
        elif 'params' in schedule:
            self.system.optimizeParams(
                dataset = self.dataset, schedule = schedule)

        nemoa.setLog(indent = '-1')

        # update network
        self.system.updateNetwork(self.network)

        nemoa.setLog(indent = '-1')
        return self

    ####################################################################
    # Model interface to dataset instance                              #
    ####################################################################

    def __setDataset(self, dataset):
        """Set dataset."""
        self.dataset = dataset
        return True

    def __getDataset(self):
        """Return link to dataset instance."""
        return self.dataset

    def __confDataset(self, dataset = None, network = None, **kwargs):
        """Configure model.dataset to given dataset and network.

        Keyword Arguments:
            dataset -- dataset instance
            network -- network instance
        """
        dataset = self.dataset
        network = self.network

        # link dataset instance
        if nemoa.type.isDataset(dataset):
            self.dataset = dataset

        # check if dataset instance is valid
        if not nemoa.type.isDataset(self.dataset):
            nemoa.log('error',
            'could not configure dataset: no dataset instance available!')
            return False

        # check if dataset is empty
        if self.dataset.isEmpty():
            return True

        # prepare params
        if not network and not self.network:
            nemoa.log('error',
            'could not configure dataset: no network instance available!')
            return False

        return self.dataset.configure(network = network \
            if not network == None else self.network)

    ####################################################################
    # Model interface to network instance                              #
    ####################################################################

    def __setNetwork(self, network):
        """Set network."""
        self.network = network
        return True

    def __getNetwork(self):
        """Return link to network instance."""
        return self.network

    def __confNetwork(self, dataset = None, network = None, system = None, **kwargs):
        """Configure model.network to given network, dataset and system.

        Keyword Arguments:
            dataset -- dataset instance
            network -- network instance
        """

        # link network instance
        if nemoa.type.isNetwork(network):
            self.network = network

        # check if network instance is valid
        if not nemoa.type.isNetwork(self.network):
            nemoa.log('error', """
                could not configure network:
                no network instance available!""")
            return False

        # check if network instance is empty
        if self.network.isEmpty(): return True

        # check if dataset instance is available
        if self.dataset == None and dataset == None:
            nemoa.log('error', """
                could not configure network:
                no dataset instance available!""")
            return False
 
         # check if system instance is available
        if self.system == None and system == None:
            nemoa.log('error', """
                could not configure network:
                no system was given!""")
            return False

        # configure network 
        return self.network.configure(
            dataset = dataset if not dataset == None else self.dataset,
            system = system if not system == None else self.system)

    ####################################################################
    # Model interface to system instance                               #
    ####################################################################

    def __setSystem(self, system):
        """Set system."""
        self.system = system
        return True

    def __getSystem(self):
        """Return link to system instance."""
        return self.system

    ####################################################################
    # Scalar model evaluation functions                                #
    ####################################################################

    def performance(self):
        """Return euclidean data reconstruction performance of system."""
        dataIn = self.system.getMapping()[0]
        dataOut = self.system.getMapping()[-1]
        data = self.dataset.getData(cols = (dataIn, dataOut))
        return self.system.getPerformance(data)

    def error(self):
        """Return data reconstruction error of system."""
        dataIn = self.system.getMapping()[0]
        dataOut = self.system.getMapping()[-1]
        data = self.dataset.getData(cols = (dataIn, dataOut))
        return self.system.getError(data)

    def meanError(self):
        """Return mean data reconstruction error of output units."""
        dataIn = self.system.getMapping()[0]
        dataOut = self.system.getMapping()[-1]
        data = self.dataset.getData(cols = (dataIn, dataOut))
        return self.system.getMeanError(data)

    ####################################################################
    # Evaluation of unit relations                                     #
    ####################################################################

    def getUnitRelation(self, preprocessing = None, **kwargs):
        """Return numpy array containing unit relations."""

        if isinstance(preprocessing, dict):
            datasetCopy = self.dataset._get()
            self.dataset.preprocessData(**kwargs['preprocessing'])
        relation = self.system.getUnitRelation(self.dataset, **kwargs)
        if isinstance(preprocessing, dict): self.dataset._set(datasetCopy)
        return relation

    def getUnitRelationMatrixMuSigma(self, matrix, relation):

        # parse relation
        reType = re.search('\Acorrelation|causality', relation.lower())
        if not reType:
            nemoa.log('warning', "unknown unit relation '" + relation + "'!")
            return None
        type = reType.group()

        numRelations = matrix.size
        numUnits = matrix.shape[0]

        # create temporary array which does not contain diag entries
        A = numpy.zeros((numRelations - numUnits))
        k = 0
        for i in range(numUnits):
            for j in range(numUnits):
                if i == j:
                    continue
                A[k] = matrix[i, j]
                k += 1

        mu = numpy.mean(A)
        sigma = numpy.std(A)

        if type == 'causality':
            Amax = numpy.max(A)
            Aabs = numpy.abs(A)
            Alist = []
            for i in range(Aabs.size):
                if Aabs[i] > Amax:
                    continue
                Alist.append(Aabs[i])
            A = numpy.array(Alist)

            mu = numpy.mean(A)
            sigma = numpy.std(A)

        return mu, sigma

    ##
    ## MODEL PARAMETER HANDLING
    ##

    #def findRelatedSampleGroups(self, **params):
        #nemoa.log("find related sample groups in dataset:")

        #partition = self.dataset.createRowPartition(**params)
        #return self.dataset.getRowPartition(partition)

    #def createBranches(self, modify, method, **params):
        #nemoa.log('create model branches:')
        
        #if modify == 'dataset':
            #if method == 'filter':
                #filters = params['filter']

                ## get params from main branch
                #mainParams = self.system._get()

                ## create branches for filters
                #for filter in filters:
                    
                    #branch = self.dataset.cfg['name'] + '.' + filter

                    ## copy params from main branch
                    #self.__config['branches'][branch] = mainParams.copy()

                    ## modify params
                    #self.__config['branches'][branch]['config']['params']['samplefilter'] = filter

                    ## set modified params
                    #self.system._set(**self.__config['branches'][branch])

                    ## reinit system
                    #self.system.initParams(self.dataset)

                    ## save system params in branch
                    #self.__config['branches'][branch] = self.system._get()

                    #nemoa.log("add model branch: '" + branch + "'")

                ## reset system params to main branch
                #self.system._set(**mainParams)

                #return True

        #return False

    #
    # SYSTEM EVALUATION
    #

    def _getEval(self, data = None, statistics = 100000, **kwargs):
        """Return dictionary with units and evaluation values."""
        if data == None: # get data if not given
            data = self.dataset.getData(statistics)
        return self.system.getDataEval(data, **kwargs)

    #
    # UNIT EVALUATION
    #

    def getUnitEval(self, data = None, statistics = None, **kwargs):
        """Return dictionary with units and evaluation values."""
        if data == None:
            data = self.dataset.getData( size = statistics,
                cols = self.groups(visible = True))
        return self.system.getUnitEval(data, **kwargs)

    #
    # LINK EVALUATION
    #

    def _getLinkEval(self, data= None, statistics = 10000, **kwargs):
        """Return dictionary with links and evaluation values."""
        if data == None: # get data if not given
            data = self.dataset.getData(statistics)
        return self.system.getLinkEval(data, **kwargs)

    #
    # MODEL EVALUATION
    #

    def eval(self, func = 'expect', data = None, block = [],
        k = 1, m = 1, statistics = 10000):

        # set default values to params if not set
        if data == None:
            data = self.dataset.getData(statistics)

        vEval, hEval = self.system.getUnitEval(data, func, block, k, m)
        mEval = numpy.mean(vEval)

        units = {}
        for i, v in enumerate(self.system.params['v']['label']):
            units[v] = vEval[i]
        for j, h in enumerate(self.system.params['h']['label']):
            units[h] = hEval[j]

        return mEval, units

    #
    # get / set all model parameters as dictionary
    #
    
    def _get(self, sec = None):
        dict = {
            'config': copy.deepcopy(self.__config),
            'network': self.network._get() if hasattr(self.network, '_get') else None,
            'dataset': self.dataset._get() if hasattr(self.dataset, '_get') else None,
            'system': self.system._get() if hasattr(self.system, '_get') else None
        }

        if not sec:
            return dict
        if sec in dict:
            return dict[sec]

        return None

    def _set(self, dict):
        """
        set configuration, parameters and data of model from given dictionary
        return true if no error occured
        """

        # get config from dict
        config = self.importConfigFromDict(dict)

        # check self
        if not nemoa.type.isDataset(self.dataset):
            nemoa.log('error', """
                could not configure dataset:
                model does not contain dataset instance!""")
            return False
        if not nemoa.type.isNetwork(self.network):
            nemoa.log('error', """
                could not configure network:
                model does not contain network instance!""")
            return False
        if not nemoa.type.isSystem(self.system):
            nemoa.log('error', """
                could not configure system:
                model does not contain system instance!""")
            return False

        self.__config = config['config'].copy()
        self.network._set(**config['network'])
        self.dataset._set(**config['dataset'])

        ## prepare
        if not 'update' in config['system']['config']:
            config['system']['config']['update'] = {'A': False}

        ## 2do system._set(...) shall create system
        ## and do something like self.configure ...

        # create system
        self.system = nemoa.system.new(
            config  = config['system']['config'].copy(),
            network = self.network,
            dataset = self.dataset
        )
        self.system._set(**config['system'])

        return self

    def save(self, file = None):
        """Save model settings to file and return filepath."""

        nemoa.log('save model to file')
        nemoa.setLog(indent = '+1')

        # get filename
        if file == None:
            fileName = '%s.mp' % (self.name())
            filePath = nemoa.workspace.path('models')
            file = filePath + fileName
        file = nemoa.common.getEmptyFile(file)

        # save model parameters and configuration to file
        nemoa.common.dictToFile(self._get(), file)

        # create console message
        nemoa.log("save model as: '%s'" % (os.path.basename(file)[:-3]))

        nemoa.setLog(indent = '-1')
        return file

    def show(self, plot, **kwargs):
        """Create plot of model with output to display."""
        return self.plot(plot, output = 'show', **kwargs)

    def plot(self, plot, output = 'file', file = None, **kwargs):
        """Create plot of model."""

        nemoa.log('create plot of model')
        nemoa.setLog(indent = '+1')

        # check if model is configured
        if not self.__isConfigured():
            nemoa.log('error', 'could not create plot of model: model is not yet configured!')
            nemoa.setLog(indent = '-1')
            return False

        # get plot instance
        nemoa.log('create plot instance')
        nemoa.setLog(indent = '+1')

        if isinstance(plot, str):
            plotName, plotParams = nemoa.common.strSplitParams(plot)
            mergeDict = plotParams
            for param in kwargs.keys():
                plotParams[param] = kwargs[param]
            objPlot = self.__getPlot(name = plotName, params = plotParams)
            if not objPlot:
                nemoa.log('warning', "could not create plot: unknown configuration '%s'" % (plotName))
                nemoa.setLog(indent = '-1')
                return None
        elif isinstance(plot, dict): objPlot = self.__getPlot(config = plot)
        else: objPlot = self.__getPlot()
        if not objPlot: return None

        # prepare filename
        if output == 'display': file = None
        elif output == 'file' and not file:
            file = nemoa.common.getEmptyFile(nemoa.workspace.path('plots') + \
                self.name() + '/' + objPlot.cfg['name'] + \
                '.' + objPlot.settings['fileformat'])

        # create plot
        retVal = objPlot.create(self, file = file)
        if not file == None: nemoa.log('save plot: ' + file)
        
        nemoa.setLog(indent = '-2')
        return retVal

    def __getPlot(self, name = None, params = {}, config = {}, **options):
        """Return new plot instance"""

        # return empty plot instance if no configuration information was given
        if not name and not config: return nemoa.plot.new()

        # get plot configuration
        if name == None: cfgPlot = config.copy()
        else: cfgPlot = nemoa.workspace.get( \
            'plot', name = name, params = params)
        if cfgPlot == None:
            nemoa.log('error', """
                could not create plot instance:
                unkown plot-id '%s'""" % (name))
            return None
        for param in params.keys():
            cfgPlot['params'][param] = params[param]

        return nemoa.plot.new(config = cfgPlot)

    ####################################################################
    # Generic / static model information                               #
    ####################################################################

    def name(self):
        """Return name of model."""
        return self.__config['name'] if 'name' in self.__config else ''

    def setName(self, name):
        """Set name of model."""
        if isinstance(self.__config, dict):
            self.__config['name'] = name
            return True
        return False

    def isEmpty(self):
        """Return true if model is empty."""
        return not 'name' in self.__config or not self.__config['name']

    def groups(self, **kwargs):
        """Return list with unit groups."""
        return self.system.getGroups(**kwargs)

    def units(self, **kwargs):
        """Return tuple with lists of units."""
        return self.system.getUnits(**kwargs)

    def links(self, **kwargs):
        return self.system.getLinks(**kwargs)

    def unit(self, unit):
        """Return information about one unit.
        
        Keyword Argument:
            unit -- name of unit
        """
        return self.network.node(unit)

    def link(self, link):
        """Return information about one link

        Keyword Argument:
            link -- name of link
        """
        return self.network.graph[link[0]][link[1]]

    def about(self, *args):
        """Return generic information about various parts of the model.

        Arguments:
            *args -- tuple of strings, containing a breadcrump trail to
                a specific information about the model

        Examples:
            about('dataset', 'preprocessing', 'transformation')
            
            about('system', 'units', 'method', 'error', 'description')
                Returns information about the "error" measurement
                function of the systems units.
        """
        if args[0] == 'dataset': return self.dataset.about(*args[1:])
        if args[0] == 'network': return self.network.about(*args[1:])
        if args[0] == 'system':  return self.system.about(*args[1:])
        if args[0] == 'name':    return self.name()
        return None

#class empty(model):
    #pass
