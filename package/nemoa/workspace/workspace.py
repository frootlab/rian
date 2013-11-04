#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, os, copy, pprint

class workspace:
    """Base class for workspaces."""

    #
    # WORKSPACE CONFIGURATION
    #

    def __init__(self, project = None):
        """Initialize shared configuration."""

        # get base configuration
        nemoa.workspace.init()

        # load user definitions
        if not project == None:
            self.load(project)

    def load(self, project):
        """Import configuration from project and update paths and logfile."""
        return nemoa.workspace.loadProject(project)

    #
    # Wrap configuration
    #

    #def get(*args, **kwargs):
        #return __shared['config'].get(*args, **kwargs)

    #def list(self, *args, **kwargs):
        #return nemoa.workspace.list(*args, **kwargs)

    #def path(*args, **kwargs):
        #return __shared['config'].path(*args, **kwargs)

    def project(self, *args, **kwargs):
        return nemoa.workspace.project(*args, **kwargs)

    #def getPath(*args, **kwargs):
        #return __shared['config'].getPath(*args, **kwargs)

    #
    #
    #

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""
        list = nemoa.workspace.list(type = type, namespace = namespace)
        if not type:
            for item in list:
                nemoa.log('info', "'%s' (%s)" % (item[2], item[1]))
        elif type in ['model']:
            for item in list:
                nemoa.log('info', "'%s'" % (item))
        else:
            for item in list:
                nemoa.log('info', "'%s'" % (item[2]))
        return len(list)

    def execute(self, name = None, **kwargs):
        """Execute python script."""
        if not '.' in name:
            scriptName = nemoa.workspace.project() + '.' + name
        else:
            scriptName = name

        config = nemoa.workspace.getConfig(type = 'script', config = scriptName, **kwargs)
        
        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = nemoa.workspace.getConfig(type = 'script', config = scriptName, **kwargs)
        if not config:
            return False
        if not os.path.isfile(config['path']):
            nemoa.log('error', """
                could not run script \'%s\': file \'%s\' not found!
                """ % (scriptName, config['path']))
            return False
        
        import imp
        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def show(self, type = None, name = None, **kwargs):
        """Print object configuration from type and name."""
        return pprint.pprint(nemoa.workspace.get(type, name))

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
        optimize = False, **kwargs):
        """Return new model instance."""

        # if keyword argument 'file' is given
        # try to get model from file
        if 'file' in kwargs:
            return self.__getModelInstanceFromFile(kwargs['file'])

        nemoa.log('title', 'create model')
        nemoa.setLog(indent = '+1')

        # create model instance
        model = self.__getModelInstance(
            config = config,
            dataset = dataset,
            network = network,
            system = system,
            name = name)

        # configure model (optional)
        if configure:
            model.configure()

        # initialize model parameters (optional)
        if initialize:
            model.initialize()

        # optimize model (optional)
        if optimize:
            model.optimize(optimize)

        # save model (optional)
        if 'autosave' in kwargs and kwargs['autosave']:
            model.save()

        nemoa.setLog(indent = '-1')
        return model

    def __getInstance(self, type = None, config = None, empty = False, **kwargs):
        """Return new instance of given object type and configuration."""
        nemoa.log('info', 'create %s %s instance' % \
            ('empty' if empty else '', type))
        nemoa.setLog(indent = '+1')

        # import module
        import importlib
        module = importlib.import_module("nemoa." + str(type))

        # get objects configuration as dictionary
        config = nemoa.workspace.getConfig(type = type, config = config, **kwargs)
        if config == None:
            nemoa.log('error', 'could not create %s instance: unknown configuration!' % (type))
            nemoa.setLog(indent = '-1')
            return None

        # create new instance of given class and initialize with configuration
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not nemoa.type.isInstanceType(instance, type):
            nemoa.log('error', 'could not create %s instance: invalid configuration!' % (type))
            nemoa.setLog(indent = '-1')
            return None

        nemoa.log('info', 'name of %s is: \'%s\'' % (type, instance.getName()))
        nemoa.setLog(indent = '-1')
        return instance

    def __getModelInstance(self, config = None,
        dataset = None, network = None, system = None, name = None):
        """Return new model instance."""

        nemoa.log('info', 'create model instance')
        nemoa.setLog(indent = '+1')

        # prepare parameters
        if network == None:
            network = {'type': 'auto'}

        # create dataset instance if not given via keyword arguments
        if not nemoa.type.isDataset(dataset):
            dataset = self.__getInstance(type = 'dataset', config = dataset)
        if not nemoa.type.isDataset(dataset): 
            nemoa.log('error', 'could not create model instance: dataset is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create network instance if not given via keyword arguments
        if not nemoa.type.isNetwork(network):
            network = self.__getInstance(type = 'network', config = network)
        if not nemoa.type.isNetwork(network): 
            nemoa.log('error', 'could not create model instance: network is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create system instance if not given via keyword arguments
        if not nemoa.type.isSystem(system):
            system = self.__getInstance(type = 'system', config = system)
        if not nemoa.type.isSystem(system):
            nemoa.log('error', 'could not create model instance: system is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # get name if not given via keyword argument
        if name == None:
            name = '-'.join([dataset.getName(), network.getName(), system.getName()])

        # create model instance
        model = self.__getInstance(type = 'model', config = config,
            dataset = dataset, network = network, system = system,
            name = name)

        nemoa.setLog(indent = '-1')
        return model

    def __getModelInstanceFromFile(self, file):
        """Return new model instance and set configuration and parameters from file."""

        nemoa.log('title', 'load model from file')
        nemoa.setLog(indent = '+1')

        # check file
        if not os.path.exists(file):
            if os.path.exists(
                nemoa.workspace.path('models') + file + '.mp'):
                file = nemoa.workspace.path('models') + file + '.mp'
            else:
                nemoa.log("error", """
                    could not load model '%s':
                    file does not exist.""" % file)
                return None

        # load model parameters and configuration from file
        nemoa.log('info', 'load model: \'%s\'' % file)
        import cPickle, gzip
        modelDict = cPickle.load(gzip.open(file, 'rb'))

        model = self.__getModelInstance(
            config = modelDict['config'],
            dataset = modelDict['dataset']['cfg'],
            network = modelDict['network']['cfg'],
            system = modelDict['system']['config'],
            name = modelDict['config']['name'])

        if not nemoa.type.isModel(model):
            return None
        else:
            model._set(modelDict)

        nemoa.setLog(indent = '-1')
        return model

    def copy(self, model):
        """Return copy of model instance"""
        return self.model(
            config = model.getConfig(),
            dataset = model.dataset.getConfig(),
            network = model.network.getConfig(),
            system = model.system.getConfig(),
            configure = False, initialize = False)._set(model._get())

    #def __getPlot(self, name = None, params = {}, config = {}, **options):
        #"""Return new plot instance"""

        ## return empty plot instance if no configuration information was given
        #if not name and not config:
            #import nemoa.plot as plot
            #return plot.new()

        ## get plot configuration
        #if name == None:
            #cfgPlot = config.copy()
        #else:
            #cfgPlot = nemoa.workspace.get('plot', name = name, params = params)

        ## create plot instance
        #if not cfgPlot == None:
            #nemoa.log("info", "create plot instance: '" + name + "'")
            ## merge params
            #for param in params.keys():
                #cfgPlot['params'][param] = params[param]
            #import nemoa.plot as plot
            #return plot.new(config = cfgPlot)
        #else:
            #nemoa.log("error", "could not create plot instance: unkown plot-id '" + name + "'")
            #return None

    #def plot(self, model, plot, output = 'file', file = None, **kwargs):
        #"""Create plot of model."""

        #singleModelPlot = True

        ## if 'model' parameter is a string, load model
        #if isinstance(model, str):
            #model = self.loadModel(model)
        ## if 'model' parameter is a list of models, load models
        #elif isinstance(model, (list, tuple)):
            #singleModelPlot = False
            #models = model
            #for i, model in enumerate(models):
                #if isinstance(model, str):
                    #models[i] = self.loadModel(model)
        #elif not nemoa.type.isModel(model):
            #nemoa.log("warning", "could not create plot: invalid parameter 'model' given")
            #return None

        ## get plot instance
        #if isinstance(plot, str):
            #plotName, plotParams = nemoa.common.strSplitParams(plot)
            #mergeDict = plotParams
            #for param in kwargs.keys():
                #plotParams[param] = kwargs[param]
            #objPlot = self.__getPlot(name = plotName, params = plotParams)
            #if not objPlot:
                #nemoa.log("warning", "could not create plot: unknown configuration '%s'" % (plotName))
                #return None
        #elif isinstance(plot, dict):
            #objPlot = self.__getPlot(config = plot)
        #else:
            #objPlot = self.__getPlot()
        #if not objPlot:
            #return None

        ## prepare filename
        #if output == 'display':
            #file = None
        #elif output == 'file' and not file:
            #file = nemoa.common.getEmptyFile(nemoa.workspace.path('plots') + \
                #model.getName() + '/' + objPlot.cfg['name'] + \
                #'.' + objPlot.settings['fileformat'])
            #nemoa.log("console", "create plot: " + file)

        #if singleModelPlot:
            ## if type of plot not is singleModelPlot
            #return objPlot.create(model, file = file)
        #else:
            #return objPlot.create(models, file = file)
