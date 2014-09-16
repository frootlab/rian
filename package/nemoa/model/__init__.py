#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, copy, time, os

class __base:

    dataset = None
    network = None
    system  = None

    ####################################################################
    # Model configuration                                              #
    ####################################################################

    def __init__(self, config = {}, dataset = None, network = None, system = None, **kwargs):
        """Initialize model and configure dataset, network and system.

        Keyword Arguments:
            dataset -- nemoa dataset instance
            network -- nemoa network instance
            system  -- nemoa system instance
        """

        # initialize private scope class attributes
        self.__config = {}

        # update model name
        self.setName(kwargs['name'] if 'name' in kwargs else None)
        nemoa.log('linking dataset, network and system instances to model')

        self.dataset = dataset
        self.network = network
        self.system  = system

        if not self._isEmpty() and self.__checkModel(): self.updateConfig()

    def __setConfig(self, config):
        """Set configuration from dictionary."""
        self.__config = config.copy()
        return True

    def __getConfig(self):
        """Return configuration as dictionary."""
        return self.__config.copy()

    def exportOutputData(self, *args, **kwargs):
        """Export data to file."""
        # copy dataset
        dataSettings = self.dataset._get()
        self.dataset.transformData(system = self.system)
        self.dataset.export(*args, **kwargs)
        self.dataset._set(dataSettings)
        return True

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
            or not nemoa.type.isDataset(self.dataset): return False
        if (allowNone and self.network == None) \
            or not nemoa.type.isNetwork(self.network): return False
        if (allowNone and self.system == None) \
            or not nemoa.type.isSystem(self.system): return False
        return True

    def updateConfig(self):
        """Update model configuration."""

        # set version of model
        self.__config['version'] = nemoa.version

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
            and self._isEmpty(): return self

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
        elif self.system._isEmpty(): return False

        # initialize system parameters
        self.system.initParams(self.dataset)

        # update network
        self.system.updateNetwork(self.network)

        return self

    def optimize(self, schedule = None, **kwargs):
        """Optimize system parameters."""

        nemoa.log('optimize model')
        nemoa.setLog(indent = '+1')

        # check if model is empty
        if self._isEmpty():
            nemoa.log('warning', "empty models can not be optimized!")
            nemoa.setLog(indent = '-1')
            return self

        # check if model is configured
        if not self.__isConfigured():
            nemoa.log('error',
                'could not optimize model: model is not yet configured!')
            nemoa.setLog(indent = '-1')
            return False

        # get optimization schedule
        if schedule == None: schedule = self.system.getType() + '.default'
        elif not '.' in schedule: schedule = \
            self.system.getType() + '.' + schedule
        schedule = nemoa.workspace.getConfig(
            type = 'schedule', config = schedule,
            merge = ['params', self.system.getType()],
            **kwargs)
        if not schedule:
            nemoa.log('error', """
                could not optimize system parameters:
                optimization schedule is not valid!""")
            nemoa.setLog(indent = '-1')
            return self

        # optimization of system parameters
        nemoa.log("starting optimization schedule: '%s'" % (schedule['name']))
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
        if self.dataset._isEmpty(): return True

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
        if nemoa.type.isNetwork(network): self.network = network

        # check if network instance is valid
        if not nemoa.type.isNetwork(self.network): return nemoa.log(
            'error', """could not configure network:
            no network instance available!""")

        # check if network instance is empty
        if self.network._isEmpty(): return True

        # check if dataset instance is available
        if self.dataset == None and dataset == None: return nemoa.log(
            'error', """could not configure network:
            no dataset instance available!""")

         # check if system instance is available
        if self.system == None and system == None: return nemoa.log(
            'error', """could not configure network:
            no system was given!""")

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
    # Model interface to dataset instance                              #
    ####################################################################

    def getData(self, dataset = None, layer = None, transform = 'expect', **kwargs):
        """Return data from dataset."""
        if not nemoa.type.isDataset(dataset): dataset = self.dataset
        if not isinstance(layer, str):
            i = self.system.getMapping()[0]
            o = self.system.getMapping()[-1]
            return dataset.getData(cols = (i, o), **kwargs)
        mapping = self.system.getMapping(tgt = layer)
        data = dataset.getData(cols = self.system.getMapping()[0], **kwargs)
        return self.system.mapData(data, mapping = mapping, transform = transform)

    ####################################################################
    # Model Evaluation                                                 #
    ####################################################################

    def eval(self, *args, **kwargs):
        """Return model evaluation."""

        # evaluation of system
        if len(args) == 0: args = ('system', )
        if args[0] == 'system':
            # get data for system evaluation
            if 'data' in kwargs.keys():
                # get data from keyword argument
                data = kwargs['data']
                del kwargs['data']
            else:
                # fetch data from dataset using parameters:
                # 'preprocessing', 'statistics'
                if 'preprocessing' in kwargs.keys():
                    preprocessing = kwargs['preprocessing']
                    del kwargs['preprocessing']
                else: preprocessing = {}
                if not isinstance(preprocessing, dict): preprocessing = {}
                if preprocessing:
                    datasetCopy = self.dataset._get()
                    self.dataset.preprocessData(preprocessing)
                if 'statistics' in kwargs.keys():
                    statistics = kwargs['statistics']
                    del kwargs['statistics']
                else: statistics = 0
                data = self.dataset.getData(
                    size = statistics, cols = self.groups(visible = True))
                if preprocessing: self.dataset._set(datasetCopy)

            return self.system.eval(data, *args[1:], **kwargs)

        # evaluation of dataset
        if args[0] == 'dataset': return self.dataset.eval(*args[1:], **kwargs)

        # evaluation of network
        if args[0] == 'network': return self.network.eval(*args[1:], **kwargs)

        return nemoa.log('warning', 'could not evaluate model')

    ####################################################################
    # Evaluation of unit relations                                     #
    ####################################################################

    def _get(self, sec = None):
        dict = {
            'config': copy.deepcopy(self.__config),
            'network': self.network._get() if hasattr(self.network, '_get') else None,
            'dataset': self.dataset._get() if hasattr(self.dataset, '_get') else None,
            'system': self.system._get() if hasattr(self.system, '_get') else None
        }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set(self, dict):
        """Set configuration, parameters and data of model from given dictionary
        return true if no error occured"""

        # get config from dict
        config = self.importConfigFromDict(dict)

        # check self
        if not nemoa.type.isDataset(self.dataset): return nemoa.log('error',
            'could not configure dataset: model does not contain dataset instance!')
        if not nemoa.type.isNetwork(self.network): return nemoa.log('error',
            'could not configure network: model does not contain network instance!')
        if not nemoa.type.isSystem(self.system): return nemoa.log('error',
            'could not configure system: model does not contain system instance!')

        self.__config = config['config'].copy()
        self.network._set(**config['network'])
        self.dataset._set(**config['dataset'])

        # prepare
        if not 'update' in config['system']['config']:
            config['system']['config']['update'] = {'A': False}

        # 2do system._set(...) shall create system and do something like self.configure ...

        # create system
        self.system = nemoa.system.new(
            config  = config['system']['config'].copy(),
            network = self.network,
            dataset = self.dataset )
        self.system._set(**config['system'])

        return self

    def save(self, file = None):
        """Save model settings to file and return filepath."""

        nemoa.log('save model to file')
        nemoa.setLog(indent = '+1')

        # get filename
        if file == None:
            fileExt  = 'nmm'
            fileName = '%s.%s' % (self.name(), fileExt)
            filePath = nemoa.workspace.path('models')
            file = filePath + fileName
        file = nemoa.common.getEmptyFile(file)

        # save model parameters and configuration to file
        nemoa.common.dictToFile(self._get(), file)

        # create console message
        nemoa.log("save model as: '%s'" %
            (os.path.basename(file)[:-(len(fileExt) + 1)]))

        nemoa.setLog(indent = '-1')
        return file

    def show(self, *args, **kwargs):
        """Create plot of model with output to display."""
        kwargs['output'] = 'show'
        return self.plot(*args, **kwargs)

    def plot(self, *args, **kwargs):
        """Create plot of model."""
        nemoa.log('create plot of model')
        nemoa.setLog(indent = '+1')

        # check args and kwargs
        if 'output' in kwargs:
            output = kwargs['output']
            del(kwargs['output'])
        else: output = 'file'
        if 'file' in kwargs:
            file = kwargs['file']
            del(kwargs['file'])
        else: file = None
        if len(args): plot = args[0]
        else: plot = None

        # check if model is configured
        if not self.__isConfigured():
            nemoa.log('error', """could not create plot of model:
                model is not yet configured!""")
            nemoa.setLog(indent = '-1')
            return False

        # get plot instance
        nemoa.log('create plot instance')
        nemoa.setLog(indent = '+1')

        if plot == None: plot = self.system.getType() + '.default'
        if isinstance(plot, str):
            plotName, plotParams = nemoa.common.strSplitParams(plot)
            mergeDict = plotParams
            for param in kwargs.keys(): plotParams[param] = kwargs[param]
            objPlot = self.__getPlot(*args, params = plotParams)
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

    def __getPlot(self, *args, **kwargs):
        """Return new plot instance"""

        # return empty plot instance if no configuration was given
        if not args and not 'config' in kwargs: return nemoa.plot.new()

        if 'params' in kwargs:
            params = kwargs['params']
            del(kwargs['params'])
        else: params = None
        if 'config' in kwargs:
            config = kwargs['config']
            del(kwargs['config'])
        else: config = None
        options = kwargs

        # get plot configuration from plot name
        if isinstance(args[0], str):
            cfg = None

            # search for given configuration
            for plot in [args[0],
                '%s.%s' % (self.system.getType(), args[0]),
                'base.' + args[0]]:
                cfg = nemoa.workspace.get('plot', \
                   name = plot, params = params)
                if isinstance(cfg, dict): break

            # search in model / system relations
            if not isinstance(cfg, dict):
                if args[0] == 'dataset':
                    if len(args) > 1: relClass = args[1]
                    else: relClass = 'histogram'
                    cfg = nemoa.common.dictMerge(params, {
                        'package': 'dataset',
                        'class': relClass,
                        'params': {},
                        'description': 'distribution',
                        'name': 'distribution',
                        'id': 0})
                elif args[0] == 'network':
                    cfg = nemoa.common.dictMerge(params, {
                        'package': 'network',
                        'class': 'graph',
                        'params': {},
                        'description': '',
                        'name': 'structure',
                        'id': 0})
                elif args[0] == 'system':
                    if len(args) == 1:
                        pass # 2DO!
                    elif args[1] == 'relations':
                        if len(args) == 2:
                            pass
                        elif args[2] in self.about('system', 'relations').keys():
                            relation = self.about('system', 'relations')[args[2]]
                            if len(args) > 3: relClass = args[3]
                            else: relClass = relation['show']
                            cfg = nemoa.common.dictMerge(params, {
                                'package': 'system',
                                'class': relClass,
                                'params': {'relation': args[0]},
                                'description': relation['description'],
                                'name': relation['name'],
                                'id': 0})
                elif args[0] in self.about('system', 'relations').keys():
                    relation = self.about('system', 'relations')[args[0]]
                    if len(args) > 1: relClass = args[1]
                    else: relClass = relation['show']
                    cfg = nemoa.common.dictMerge(params, {
                        'package': 'system',
                        'class': relClass,
                        'params': {'relation': args[0]},
                        'description': relation['description'],
                        'name': relation['name'],
                        'id': 0})

            # could not find configuration
            if not isinstance(cfg, dict): return nemoa.log('error',
                "could not create plot instance: unsupported plot '%s'" % (args[0]))
        elif isinstance(config, dict): cfg = config

        # overwrite config with given params
        if isinstance(params, dict):
            for key in params.keys(): cfg['params'][key] = params[key]

        return nemoa.plot.new(config = cfg)

    ####################################################################
    # Generic / static model information                               #
    ####################################################################

    def name(self):
        """Return name of model."""
        return self.__config['name'] if 'name' in self.__config else ''

    def setName(self, name):
        """Set name of model."""
        if not isinstance(self.__config, dict): return False
        self.__config['name'] = name
        return self

    def _isEmpty(self):
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

            about('system', 'units', 'error', 'description')
                Returns information about the "error" measurement
                function of the systems units.
        """
        if not args: return {
            'name':        self.name(),
            'description': '',
            'dataset':     self.dataset.about(*args[1:]),
            'network':     self.network.about(*args[1:]),
            'system':      self.system.about(*args[1:])
        }

        if args[0] == 'name': return self.name()
        if args[0] == 'description': return ''
        if args[0] == 'dataset': return self.dataset.about(*args[1:])
        if args[0] == 'network': return self.network.about(*args[1:])
        if args[0] == 'system': return self.system.about(*args[1:])

        return None

def new(*args, **kwargs):
    """Return new model instance."""
    return __base(*args, **kwargs)
