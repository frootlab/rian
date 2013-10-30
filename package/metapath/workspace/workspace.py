#!/usr/bin/env python
# -*- coding: utf-8 -*-

import metapath.common as mp
import os, copy, pprint

class workspace:
    """Base class for workspaces."""

    #
    # WORKSPACE CONFIGURATION
    #

    def __init__(self, project = None):
        """Initialize shared configuration."""

        # get base configuration
        import metapath.workspace.config
        mp.shared['config'] = metapath.workspace.config.config()

        # import all common definitions
        mp.shared['config'].loadCommon()

        # load user definitions
        if not project == None:
            self.load(project)

    def load(self, project):
        """Import configuration from project and update paths and logfile."""

        return mp.shared['config'].loadProject(project)

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""

        list = mp.shared['config'].list(type = type, namespace = namespace)
        if not type:
            for item in list:
                mp.log('info', "'%s' (%s)" % (item[2], item[1]))
        elif type in ['model', 'script']:
            for item in list:
                mp.log('info', "'%s'" % (item))
        else:
            for item in list:
                mp.log('info', "'%s'" % (item[2]))
        return len(list)

    def execute(self, name = None, **kwargs):
        """Execute python script."""
        if not '.' in name:
            scriptName = mp.shared['config'].project() + '.' + name
        else:
            scriptName = name

        config = self.__getConfig(type = 'script', config = scriptName, **kwargs)
        
        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = self.__getConfig(type = 'script', config = scriptName, **kwargs)
        if not config:
            return False
        if not os.path.isfile(config['path']):
            mp.log('error', """
                could not run script \'%s\': file \'%s\' not found!
                """ % (scriptName, config['path']))
            return False
        
        import imp
        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def show(self, type = None, name = None, **kwargs):
        """Print object configuration from type and name."""
        return pprint.pprint(mp.shared['config'].get(type, name))

    def dataset(self, config = None, **kwargs):
        """Return new dataset instance."""
        return self.__getInstance('dataset', config, **kwargs)

    def network(self, config = None, **kwargs):
        """Return new network instance."""
        return self.__getInstance('network', config, **kwargs)

    def system(self, config = None, **kwargs):
        """Return new system instance."""
        return self.__getInstance('system', config, **kwargs)

    def model(self, config = None,
        dataset = None, network = None, system = None,
        configure = True, initialize = True, name = None,
        optimize = False, autosave = False, **kwargs):
        """Return new model instance."""

        mp.log('title', 'create new model')
        mp.setLog(indent = '+1')

        # create model instance
        model = self.__getModelInstance(config = config,
            dataset = dataset, network = network, system = system,
            name = name)

        # configure model (optional)
        if configure:
            model.configure()

        # initialize model parameters (optional)
        if initialize:
            model.initialize()

        mp.setLog(indent = '-1')

        # optimize model (optional)
        if optimize:
            self.optimize(model, optimize)

        # save model (optional)
        if autosave:
            self.saveModel(model)

        return model

    def __getInstance(self, type = None, config = None, empty = False, **kwargs):
        """Return new instance of given object type and configuration."""
        mp.log('info', 'create %s %s instance' % \
            ('empty' if empty else 'new', type))
        mp.setLog(indent = '+1')

        # import module
        import importlib
        module = importlib.import_module("metapath." + str(type))

        # get objects configuration as dictionary
        config = self.__getConfig(type = type, config = config, **kwargs)
        if config == None:
            mp.log('error', 'could not create %s instance: unknown configuration!' % (type))
            mp.setLog(indent = '-1')
            return None

        # create new instance of given class and initialize with configuration
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not mp.isInstanceType(instance, type):
            mp.log('error', 'could not create %s instance: invalid configuration!' % (type))
            mp.setLog(indent = '-1')
            return None

        mp.log('info', 'name of %s is: \'%s\'' % (type, instance.getName()))
        mp.setLog(indent = '-1')
        return instance

    def __getModelInstance(self, config = None,
        dataset = None, network = None, system = None, name = None):
        """Return new model instance."""

        mp.log('info', 'create new model instance')
        mp.setLog(indent = '+1')

        # prepare parameters
        if network == None:
            network = {'type': 'auto'}

        # create dataset instance if not given via keyword arguments
        if not mp.isDataset(dataset):
            dataset = self.__getInstance(type = 'dataset', config = dataset)
        if not mp.isDataset(dataset): 
            mp.log('error', 'could not create model instance: dataset is invalid!')
            mp.setLog(indent = '-1')
            return None

        # create network instance if not given via keyword arguments
        if not mp.isNetwork(network):
            network = self.__getInstance(type = 'network', config = network)
        if not mp.isNetwork(network): 
            mp.log('error', 'could not create model instance: network is invalid!')
            mp.setLog(indent = '-1')
            return None

        # create system instance if not given via keyword arguments
        if not mp.isSystem(system):
            system = self.__getInstance(type = 'system', config = system)
        if not mp.isSystem(system):
            mp.log('error', 'could not create model instance: system is invalid!')
            mp.setLog(indent = '-1')
            return None

        # get name if not given via keyword argument
        if name == None:
            name = '-'.join([dataset.getName(), network.getName(), system.getName()])

        # create model instance
        model = self.__getInstance(type = 'model', config = config,
            dataset = dataset, network = network, system = system,
            name = name)

        mp.setLog(indent = '-1')
        return model

    def __getConfig(self, type = None, config = None, merge = ['params'], **kwargs):
        """Return object configuration as dictionary."""
        if config == None:
            return {}
        # for loading models it's necessary
        if isinstance(config, dict):
            return copy.deepcopy(config)
        elif isinstance(config, str) and isinstance(type, str):
            name, params = mp.strSplitParams(config)
            if 'params' in kwargs and isinstance(kwargs['params'], dict):
                params = mp.dictMerge(kwargs['params'], params)
            return mp.shared['config'].get(
                type = type, name = name,
                merge = merge, params = params)
        return False

    def copy(self, model):
        """Return copy of model instance"""
        return self.model(
            config = model.getConfig(),
            dataset = model.dataset.getConfig(),
            network = model.network.getConfig(),
            system = model.system.getConfig(),
            configure = False, initialize = False)._set(model._get())

    def __getPlot(self, name = None, params = {}, config = {}, **options):
        """Return new plot instance"""

        # return empty plot instance if no configuration information was given
        if not name and not config:
            import metapath.plot as plot
            return plot.new()

        # get plot configuration
        if name == None:
            cfgPlot = config.copy()
        else:
            cfgPlot = mp.shared['config'].get('plot', name = name, params = params)

        # create plot instance
        if not cfgPlot == None:
            mp.log("info", "create plot instance: '" + name + "'")
            # merge params
            for param in params.keys():
                cfgPlot['params'][param] = params[param]
            import metapath.plot as plot
            return plot.new(config = cfgPlot)
        else:
            mp.log("error", "could not create plot instance: unkown plot-id '" + name + "'")
            return None

    def optimize(self, model, schedule, **kwargs):
        """Optimize model instance."""

        mp.log('title', 'optimize model')
        mp.setLog(indent = '+1')

        # check model
        if model.isEmpty():
            mp.log('warning', 'empty model can not be optimized!')
            mp.setLog(indent = '-1')
            return model

        # get optimization configuration
        config = self.__getConfig(
            type = 'schedule', config = schedule,
            merge = ['params', model.system.getName()],
            **kwargs)

        retVal = model.optimize(schedule = config)
        mp.setLog(indent = '-1')
        return retVal

    def loadModel(self, file):
        """Load model settings from file and return model instance."""

        mp.log('title', 'import model from file')
        mp.setLog(indent = '+1')

        # check file
        if not os.path.exists(file):
            if os.path.exists(mp.shared['config'].path('models') + file + '.mp'):
                file = mp.shared['config'].path('models') + file + '.mp'
            else:
                mp.log("error", "could not load model '%s': file does not exist." % file)
                return None

        # load model parameters and configuration from file
        mp.log('info', 'load model: \'%s\'' % file)
        import cPickle, gzip
        config = cPickle.load(gzip.open(file, 'rb'))

        # create empty model instance and initialize with config
        model = self.model(
            config = config['config'],
            dataset = config['dataset']['cfg'],
            network = config['network']['cfg'],
            system = config['system']['config'],
            configure = False, initialize = False)

        # set config to set model parameters
        model._set(config)
        mp.setLog(indent = '-1')

        return model

    def saveModel(self, model, file = None):
        """Save model settings to file and return filepath."""

        # check object class
        if not mp.isModel(model):
            mp.log("warning", "could not save model: invalid model instance given!")
            return False

        # get filename
        if file == None:
            fileName = '%s.mp' % (model.getName())
            filePath = mp.shared['config'].path('models')
            file = filePath + fileName
        file = mp.getEmptyFile(file)

        # save model parameters and configuration to file
        import cPickle, gzip
        cPickle.dump(
            obj = model._get(),
            file = gzip.open(file, "wb", compresslevel = 3),
            protocol = 2)

        # create console message
        finalName = os.path.basename(file)[:-3]
        mp.log("info", "save model as: '%s'" % (finalName))

        return file

    def plot(self, model, plot, output = 'file', file = None, **kwargs):
        """Create plot of model."""

        singleModelPlot = True

        # if 'model' parameter is a string, load model
        if isinstance(model, str):
            model = self.loadModel(model)
        # if 'model' parameter is a list of models, load models
        elif isinstance(model, (list, tuple)):
            singleModelPlot = False
            models = model
            for i, model in enumerate(models):
                if isinstance(model, str):
                    models[i] = self.loadModel(model)
        elif not mp.isModel(model):
            mp.log("warning", "could not create plot: invalid parameter 'model' given")
            return None

        # get plot instance
        if isinstance(plot, str):
            plotName, plotParams = mp.strSplitParams(plot)
            mergeDict = plotParams
            for param in kwargs.keys():
                plotParams[param] = kwargs[param]
            objPlot = self.__getPlot(name = plotName, params = plotParams)
            if not objPlot:
                mp.log("warning", "could not create plot: unknown configuration '%s'" % (plotName))
                return None
        elif isinstance(plot, dict):
            objPlot = self.__getPlot(config = plot)
        else:
            objPlot = self.__getPlot()
        if not objPlot:
            return None

        # prepare filename
        if output == 'display':
            file = None
        elif output == 'file' and not file:
            file = mp.getEmptyFile(mp.shared['config'].path('plots') + \
                model.getName() + '/' + objPlot.cfg['name'] + \
                '.' + objPlot.settings['fileformat'])
            mp.log("console", "create plot: " + file)

        if singleModelPlot:
            # if type of plot not is singleModelPlot
            return objPlot.create(model, file = file)
        else:
            return objPlot.create(models, file = file)
