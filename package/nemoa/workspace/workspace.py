#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, os, copy, importlib, imp

class workspace:
    """Nemoa workspace."""

    def __init__(self, project = None):
        """Initialize shared configuration."""
        nemoa.workspace.init()
        if not project == None: nemoa.workspace.load(project)

    def load(self, workspace):
        """Import configuration from workspace and update paths and logfile."""
        return nemoa.workspace.load(workspace)

    def name(self, *args, **kwargs):
        """Return name of workspace."""
        return nemoa.workspace.project(*args, **kwargs)

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""
        list = nemoa.workspace.list(type = type, namespace = self.name())
        if not type: names = \
            ['%s (%s)' % (item[2], item[1]) for item in list]
        elif type in ['model']: names = list
        else: names = [item[2] for item in list]
        return names

    def execute(self, name = None, **kwargs):
        """Execute nemoa script."""
        scriptName = name if '.' in name else '%s.%s' % (self.name(), name)
        config = nemoa.workspace.getConfig(
            type = 'script', config = scriptName, **kwargs)

        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = nemoa.workspace.getConfig(
                type = 'script', config = scriptName, **kwargs)
        if not config: return False
        if not os.path.isfile(config['path']): return nemoa.log('error', """
            could not run script '%s': file '%s' not found!
            """ % (scriptName, config['path']))

        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def dataset(self, config = None, **kwargs):
        """Return new dataset instance."""
        return self.__getInstance('dataset', config, **kwargs)

    def network(self, config = None, **kwargs):
        """Return new network instance."""
        return self.__getInstance('network', config, **kwargs)

    def system(self, config = None, **kwargs):
        """Return new system instance."""
        return self.__getInstance('system', config, **kwargs)

    def model(self, name = None, **kwargs):
        """Return model instance."""

        # try to import model from file
        if isinstance(name, str) and not kwargs:
            if not name in self.list(type = 'model'): return \
                nemoa.log('warning', """could not import model:
                a model with name '%s' does not exists!""" % (name))
            return self.__importModelFromFile(name)

        # check keyword arguments
        if not ('network' in kwargs and 'dataset' in kwargs \
            and 'system' in kwargs): return nemoa.log('warning', """
            could not create model:
            dataset, network and system parameters needed!""")

        # try to create new model
        return self.__createNewModel(name, **kwargs)

    def __getInstance(self, type = None, config = None, empty = False, **kwargs):
        """Return new instance of given object type and configuration."""
        nemoa.log('create%s %s instance' % (' empty' if empty else '', type))
        nemoa.setLog(indent = '+1')

        # import module
        module = importlib.import_module('nemoa.' + str(type))

        # get objects configuration as dictionary
        config = nemoa.workspace.getConfig(type = type,
            config = config, **kwargs)
        if not isinstance(config, dict):
            nemoa.log('error', """could not create %s instance:
                unknown configuration!""" % (type))
            nemoa.setLog(indent = '-1')
            return None

        # create and initialize new instance of given class
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not nemoa.type.isInstanceType(instance, type):
            nemoa.log('error', """could not create %s instance:
                invalid configuration!""" % (type))
            nemoa.setLog(indent = '-1')
            return None

        nemoa.log('name of %s is: \'%s\'' % (type, instance.name()))
        nemoa.setLog(indent = '-1')
        return instance

    def __createNewModel(self, name, config = None,
        dataset = None, network = None, system = None,
        configure = True, initialize = True):
        nemoa.log('create new model')
        nemoa.setLog(indent = '+1')

        model = self.__getModelInstance(name = name, config  = config,
            dataset = dataset, network = network, system  = system)

        if not nemoa.type.isModel(model):
            nemoa.log('error', 'could not create new model!')
            nemoa.setLog(indent = '-1')
            return False

        # configure model
        if configure: model.configure()

        # initialize model parameters
        if initialize: model.initialize()

        nemoa.setLog(indent = '-1')
        return model

    def __getModelInstance(self, name = None, config = None,
        dataset = None, network = None, system = None):
        """Return new model instance."""

        nemoa.log('create model instance')
        nemoa.setLog(indent = '+1')

        # create dataset instance (if not given)
        if not nemoa.type.isDataset(dataset): dataset = \
            self.__getInstance(type = 'dataset', config = dataset)
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error',
                'could not create model instance: dataset is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create network instance (if not given)
        if network == None: network = {'type': 'auto'}
        if not nemoa.type.isNetwork(network): network = \
            self.__getInstance(type = 'network', config = network)
        if not nemoa.type.isNetwork(network):
            nemoa.log('error',
                'could not create model instance: network is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create system instance (if not given)
        if not nemoa.type.isSystem(system): system = \
            self.__getInstance(type = 'system', config = system)
        if not nemoa.type.isSystem(system):
            nemoa.log('error',
                'could not create model instance: system is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create name string (if not given)
        if name == None: name = '-'.join(
            [dataset.name(), network.name(), system.name()])

        # create model instance
        model = self.__getInstance(
            type = 'model', config = config, name = name,
            dataset = dataset, network = network, system = system)

        nemoa.setLog(indent = '-1')
        return model

    def __importModelFromFile(self, file):
        """Return new model instance and set configuration and parameters from file."""

        nemoa.log('import model from file')
        nemoa.setLog(indent = '+1')

        # check file
        if not os.path.exists(file):
            if os.path.exists(
                nemoa.workspace.path('models') + file + '.nmm'):
                file = nemoa.workspace.path('models') + file + '.nmm'
            else: return nemoa.log('error', """
                could not load model '%s':
                file does not exist.""" % file)

        # load model parameters and configuration from file
        nemoa.log('load model: \'%s\'' % file)
        modelDict = nemoa.common.dictFromFile(file)

        model = self.__getModelInstance(
            name    = modelDict['config']['name'],
            config  = modelDict['config'],
            dataset = modelDict['dataset']['cfg'],
            network = modelDict['network']['cfg'],
            system  = modelDict['system']['config'])

        if nemoa.type.isModel(model): model._set(modelDict)
        else: return None

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
