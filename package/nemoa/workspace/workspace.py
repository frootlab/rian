#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, os, copy, importlib, imp

class workspace:
    """Base class for workspaces."""

    def __init__(self, project = None):
        """Initialize shared configuration."""
        nemoa.workspace.init()
        if not project == None:
            nemoa.workspace.loadProject(project)

    def load(self, project):
        """Import configuration from project and update paths and logfile."""
        return nemoa.workspace.loadProject(project)

    def project(self, *args, **kwargs):
        """Return name of project."""
        return nemoa.workspace.project(*args, **kwargs)

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""
        list = nemoa.workspace.list(type = type, namespace = namespace)
        if not type:
            listOfNames = ["%s (%s)" % (item[2], item[1]) for item in list]
        elif type in ['model']:
            listOfNames = list
        else:
            listOfNames = [item[2] for item in list]
        return listOfNames

    def execute(self, name = None, **kwargs):
        """Execute python script."""
        if not '.' in name:
            scriptName = self.project() + '.' + name
        else:
            scriptName = name

        config = nemoa.workspace.getConfig(
            type = 'script', config = scriptName, **kwargs)
        
        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = nemoa.workspace.getConfig(
                type = 'script', config = scriptName, **kwargs)
        if not config:
            return False
        if not os.path.isfile(config['path']):
            nemoa.log('error', """
                could not run script \'%s\': file \'%s\' not found!
                """ % (scriptName, config['path']))
            return False

        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def show(self, type = None, name = None, **kwargs):
        """Print object configuration from type and name."""
        return nemoa.common.printDict(nemoa.workspace.get(type, name))

    def dataset(self, config = None, **kwargs):
        """Return new dataset instance."""
        return self.__getInstance('dataset', config, **kwargs)

    def network(self, config = None, **kwargs):
        """Return new network instance."""
        return self.__getInstance('network', config, **kwargs)

    def system(self, config = None, **kwargs):
        """Return new system instance."""
        return self.__getInstance('system', config, **kwargs)

    def model(self, config = None, name = None, **kwargs):
        """Return new model instance."""

        # if keyword argument 'file' is given
        # try to get model from file
        if 'file' in kwargs:
            return self.__getModelInstanceFromFile(kwargs['file'])

        nemoa.log('title', 'create model')
        nemoa.setLog(indent = '+1')

        # create model instance
        if not 'dataset' in kwargs \
            or not 'network' in kwargs \
            or not 'system' in kwargs:
            nemoa.log('error', """
                could not create model:
                dataset, network and system parameters needed!""")
            nemoa.setLog(indent = '-1')
            return None
        model = self.__getModelInstance(
            config = config, name = name,
            dataset = kwargs['dataset'],
            network = kwargs['network'],
            system  = kwargs['system'])

        # configure model (optional, default: True)
        if not 'configure' in kwargs \
            or ('configure' in kwargs \
            and kwargs['configure'] == True):
            if model == None:
                nemoa.log('error', """
                    could not configure model:
                    model instance is not valid!""")
                nemoa.setLog(indent = '-1')
                return None
            model.configure()

        # initialize model parameters (optional)
        if 'initialize' in kwargs \
            and kwargs['initialize'] == True:
            model.initialize()

        # optimize model (optional)
        if 'optimize' in kwargs \
            and not kwargs['optimize'] == False:
            model.optimize(optimize)

        # save model to file (optional)
        if 'save' in kwargs \
            and not kwargs['save']:
            model.save()

        nemoa.setLog(indent = '-1')
        return model

    def __getInstance(self, type = None, config = None, empty = False, **kwargs):
        """Return new instance of given object type and configuration."""
        nemoa.log('info', 'create %s %s instance' % \
            ('empty' if empty else '', type))
        nemoa.setLog(indent = '+1')

        # import module
        module = importlib.import_module("nemoa." + str(type))

        # get objects configuration as dictionary
        config = nemoa.workspace.getConfig(type = type, config = config, **kwargs)
        if config == None:
            nemoa.log('error', """
                could not create %s instance:
                unknown configuration!""" % (type))
            nemoa.setLog(indent = '-1')
            return None

        # create and initialize new instance of given class
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not nemoa.type.isInstanceType(instance, type):
            nemoa.log('error', """
                could not create %s instance:
                invalid configuration!""" % (type))
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
            dataset = self.__getInstance(
                type = 'dataset', config = dataset)
        if not nemoa.type.isDataset(dataset): 
            nemoa.log('error', """
                could not create model instance:
                dataset is invalid!""")
            nemoa.setLog(indent = '-1')
            return None

        # create network instance if not given via keyword arguments
        if not nemoa.type.isNetwork(network):
            network = self.__getInstance(
                type = 'network', config = network)
        if not nemoa.type.isNetwork(network): 
            nemoa.log('error', """
                could not create model instance:
                network is invalid!""")
            nemoa.setLog(indent = '-1')
            return None

        # create system instance if not given via keyword arguments
        if not nemoa.type.isSystem(system):
            system = self.__getInstance(
                type = 'system', config = system)
        if not nemoa.type.isSystem(system):
            nemoa.log('error', """
                could not create model instance:
                system is invalid!""")
            nemoa.setLog(indent = '-1')
            return None

        # get name if not given via keyword argument
        if name == None:
            name = '-'.join([dataset.getName(), network.getName(), system.getName()])

        # create model instance
        model = self.__getInstance(
            type = 'model', config = config, name = name,
            dataset = dataset, network = network, system = system)

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
        modelDict = nemoa.common.dictFromFile(file)

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
