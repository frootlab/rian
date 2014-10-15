# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import copy
import os
import importlib
import imp
import re
import ConfigParser
import glob

class Workspace:
    """Nemoa workspace."""

    _workspace = None

    def __init__(self, workspace = None):
        """initialize shared configuration."""
        nemoa.workspace._init()
        if workspace:
            self._workspace = workspace
            self.load(workspace)

    def load(self, workspace):
        """import workspace and update paths and logfile."""
        return nemoa.workspace.load(workspace)

    def name(self):
        """Return name of workspace."""
        return self._workspace

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""
        list = nemoa.workspace.list(type = type,
            namespace = self.name())
        if not type: names = \
            ['%s (%s)' % (item[2], item[1]) for item in list]
        elif type in ['model']: names = list
        else: names = [item[2] for item in list]
        return names

    def execute(self, name = None, **kwargs):
        """execute nemoa script."""
        script_name = name \
            if '.' in name else '%s.%s' % (self._workspace, name)
        config = nemoa.workspace._get_config(
            type = 'script', config = script_name, **kwargs)

        if not config and not '.' in name:
            script_name = 'base.' + name
            config = nemoa.workspace._get_config(
                type = 'script', config = script_name, **kwargs)
        if not config: return False
        if not os.path.isfile(config['path']):
            return nemoa.log('error', """could not run script '%s':
            file '%s' not found!""" % (script_name, config['path']))

        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def dataset(self, config = None, **kwargs):
        """Return new dataset instance."""
        return self._get_instance('dataset', config, **kwargs)

    def network(self, config = None, **kwargs):
        """Return new network instance."""
        return self._get_instance('network', config, **kwargs)

    def system(self, config = None, **kwargs):
        """Return new system instance."""
        return self._get_instance('system', config, **kwargs)

    def model(self, name = None, **kwargs):
        """Return model instance."""

        # try to import model from file
        if isinstance(name, str) and not kwargs:
            if not name in self.list(type = 'model'):
                return nemoa.log('error', """could not import model:
                    a model with name '%s' does not exists!""" % (name))
            return self._import_model(name)

        # check keyword arguments
        if not ('network' in kwargs and 'dataset' in kwargs \
            and 'system' in kwargs):
            return nemoa.log('error', """could not create model:
                dataset, network and system parameters needed!""")

        # try to create new model
        return self._create_new_model(name, **kwargs)

    def _get_instance(self, type = None, config = None,
        empty = False, **kwargs):
        """Create new instance of given object type."""
        nemoa.log('create%s %s instance'
            % (' empty' if empty else '', type))
        nemoa.log('set', indent = '+1')

        # import module
        module = importlib.import_module('nemoa.' + str(type))

        # get objects configuration as dictionary
        config = nemoa.workspace._get_config(type = type,
            config = config, **kwargs)
        if not isinstance(config, dict):
            nemoa.log('error', """could not create %s instance:
                unknown configuration!""" % (type))
            nemoa.log('set', indent = '-1')
            return None

        # create and initialize new instance of given class
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not nemoa.type.is_instance_of_type(instance, type):
            nemoa.log('error', """could not create %s instance:
                invalid configuration!""" % (type))
            nemoa.log('set', indent = '-1')
            return None

        nemoa.log("name of %s is: '%s'" % (type, instance.get('name')))
        nemoa.log('set', indent = '-1')
        return instance

    def _create_new_model(self, name, config = None,
        dataset = None, network = None, system = None,
        configure = True, initialize = True):
        nemoa.log('create new model')
        nemoa.log('set', indent = '+1')

        model = self._get_model_instance(
            name = name, config = config,
            dataset = dataset, network = network, system  = system)

        if not nemoa.type.is_model(model):
            nemoa.log('error', 'could not create new model!')
            nemoa.log('set', indent = '-1')
            return False

        if configure: model._configure() # configure model
        if initialize: model._initialize() # initialize model parameters

        nemoa.log('set', indent = '-1')
        return model

    def _get_model_instance(self, name = None, config = None,
        dataset = None, network = None, system = None):
        """Return new model instance."""

        nemoa.log('create model instance')
        nemoa.log('set', indent = '+1')

        # create dataset instance (if not given)
        if not nemoa.type.is_dataset(dataset): dataset = \
            self._get_instance(type = 'dataset', config = dataset)
        if not nemoa.type.is_dataset(dataset):
            nemoa.log('error',
                'could not create model instance: dataset is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create network instance (if not given)
        if network == None: network = {'type': 'auto'}
        if not nemoa.type.is_network(network): network = \
            self._get_instance(type = 'network', config = network)
        if not nemoa.type.is_network(network):
            nemoa.log('error',
                'could not create model instance: network is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create system instance (if not given)
        if not nemoa.type.is_system(system): system = \
            self._get_instance(type = 'system', config = system)
        if not nemoa.type.is_system(system):
            nemoa.log('error',
                'could not create model instance: system is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create name string (if not given)
        if name == None:
            name = '-'.join([
                str(dataset.get('name')),
                str(network.get('name')),
                str(system.get('name'))])

        # create model instance
        model = self._get_instance(
            type = 'model', config = config, name = name,
            dataset = dataset, network = network, system = system)

        nemoa.log('set', indent = '-1')
        return model

    def _import_model(self, path):
        """Import model from file.

        Opens gzip compressed model configuration and parameters. The
        configuration is first used to configure and init a new dataset,
        network and system instance and finally a new model instance.
        After this the parameters of the model are overwritten by the
        parameters from the file.

        Args:
            path: Path to nemoa model file (with fileextension .npz)

        Returns:
            Nemoa model instance

        """

        nemoa.log('import model from file')
        nemoa.log('set', indent = '+1')

        # check file
        if not os.path.exists(path):
            if os.path.exists(
                nemoa.workspace.path('models') + path + '.nmm'):
                path = nemoa.workspace.path('models') + path + '.nmm'
            else:
                return nemoa.log('error', """could not load model '%s':
                    file does not exist.""" % path)

        # load model configuration and parameters from file
        nemoa.log("load model: '%s'" % path)
        model_copy = nemoa.common.dict_from_file(path)

        # create new dataset, network, system and model instances
        model = self._get_model_instance(
            name = model_copy['config']['name'],
            config = model_copy['config'],
            dataset = model_copy['dataset']['config'],
            network = model_copy['network']['config'],
            system = model_copy['system']['config'])
        if not nemoa.type.is_model(model): return None

        # copy configuration and parameters to model instance
        model.set('copy', **model_copy)

        nemoa.log('set', indent = '-1')
        return model

    # TODO: move to model base class as model.copy
    def _copy_model(self, model):
        """Return copy of model instance"""

        # create backup from original model
        model_backup = model.get('copy')
        model_config = model_backup['config']
        dataset_config = model_backup['dataset']['config']
        network_config = model_backup['network']['config']
        system_config = model_backup['system']['config']

        # create new model with configurations from original model
        # this ensures objects of same type as in the original model
        model_copy = self.model(
            configure = False,
            initialize = False,
            config = model_config,
            dataset = dataset_config,
            network = network_config,
            system = system_config)

        # finally copy configuration and parameters from the original
        # model to the model copy
        model_copy.set('copy', model_backup)

        return model_copy

class Config:
    """nemoa workspace module internal configuration object."""

    _baseconf = 'nemoa.ini' # base configuration file
    _basepath = None        # paths for shared ressources and workspaces
    _path = None            # paths for logfile, cachefile, etc.
    _workspace = None       # current workspace
    _workspace_path = None  # paths for datasets, networks, models, etc.
    _store = None           # information storage for known objects
    _index = None           # index for storage

    def __init__(self, shared = True):

        self._path = {}
        self._basepath = {
            'user': '~/.nemoa/',
            'common': '/etc/nemoa/common/' }

        self._update_basepath() # update paths for shared and user

        # init tree structure for configuration storage
        self._store = {
            'dataset': {}, 'network': {}, 'system': {},
            'plot': {}, 'schedule': {}, 'script': {} }
        self._index = {}

        if shared: self._import_shared() # import shared resources

    def _update_basepath(self):
        """Update base directories from base configuration."""

        if not os.path.exists(self._baseconf): return False

        # Create ConfigParser instance and get basepath configuration
        cfg = ConfigParser.ConfigParser()
        cfg.optionxform = str
        cfg.read(self._baseconf)

        # [folders]
        if 'folders' in cfg.sections():
            for key in ['user', 'cache', 'common']:
                if not key in cfg.options('folders'): continue
                val = cfg.get('folders', key)
                path = self._expand_path(val)
                if path: self._basepath[key] = path

        # [files]
        if 'files' in cfg.sections():
            for key in ['logfile']:
                if not key in cfg.options('files'): continue
                val = cfg.get('files', key)
                self._path[key] = self._expand_path(val)

        return True

    def _update_paths(self, base = 'user'):

        self._workspace_path = {
            'datasets': '%workspace%/data/',
            'models': '%workspace%/models/',
            'scripts': '%workspace%/scripts/',
            'networks': '%workspace%/networks/',
            'plots': '%workspace%/plots/',
            'cache': '%workspace%/cache/',
            'logfile': '%workspace%/nemoa.log'
        }

        if base in ['user', 'common']: # TODO: change allow_write
            allow_write = {'user': False, 'common': False}[base]
            for key in self._workspace_path:
                path = '%' + base + '%/' + self._workspace_path[key]
                self._path[key] = \
                    self._expand_path(path, create = allow_write)

        return True

    def _list_user_workspaces(self):
        """Return list of private workspaces."""
        user_dir = self._expand_path(self._basepath['user'])
        return [os.path.basename(w) for w in glob.iglob(user_dir + '*')
            if os.path.isdir(w)]

    def _list_shared_workspaces(self):
        """Return list of shared resources."""
        shared = self._expand_path(self._basepath['common'])
        return [os.path.basename(w) for w in glob.iglob(shared + '*')
            if os.path.isdir(w)]

    def workspace(self):
        """Return name of current workspace."""
        return self._workspace

    def name(self):
        """Return name of current workspace."""
        return self._workspace

    def path(self, key = None):
        """Return path."""
        if isinstance(key, str) and key in self._path.keys():
            if isinstance(self._path[key], dict):
                return self._path[key].copy()
            return self._path[key]
        return self._path.copy()

    def _import_shared(self):
        """Import shared resources."""
        nemoa.log('import shared resources')
        nemoa.log('set', indent = '+1')

        # get current workspace
        cur_workspace = self._workspace

        # import shared resources and update paths
        for workspace in self._list_shared_workspaces():
            self._workspace = workspace
            self._update_paths(base = 'common')
            self._scan_config_files('%common%/%workspace%')
            self._scan_for_scripts()
            self._scan_for_networks()

        # reset to current workspace
        self._workspace = cur_workspace

        nemoa.log('set', indent = '-1')
        return True

    def load(self, workspace):
        """Import configuration files from workspace."""
        nemoa.log('import private resources')
        nemoa.log('set', indent = '+1')

        # check if workspace exists
        if not workspace in self._list_user_workspaces():
            return nemoa.log('warning', """could not open workspace
                '%s': folder could not be found in '%s'!"""
                % (workspace, self._basepath['user']))

        self._workspace = workspace       # set workspace
        self._update_paths(base = 'user') # update paths
        self._update_cache_paths()        # update path of cache
        nemoa.log('init', logfile = self._path['logfile']) # update logger

        path = '%user%/%workspace%'
        self._scan_config_files(path) # import configuration files
        self._scan_for_scripts()          # scan for scriptfiles
        self._scan_for_networks()     # scan for network configs

        nemoa.log('set', indent = '-1')
        return True

    def _update_cache_paths(self):
        """Update dataset cache paths to current workspace."""
        for key in self._store['dataset']:
            self._store['dataset'][key]['cache_path'] \
                = self._path['cache']
        return True

    def _scan_config_files(self, path):
        """Import configuration files from current workspace."""
        nemoa.log('scanning for configuration files')
        nemoa.log('set', indent = '+1')

        # assert configuration files path
        files = self._expand_path(path + '/*.ini')

        # import configuration files
        for file_path in glob.iglob(files):
            self._import_config_file(file_path)

        nemoa.log('set', indent = '-1')
        return True

    def _import_config_file(self, file):
        """Import configuration file."""

        # search definition file
        if os.path.isfile(file): configFile = file
        elif os.path.isfile(self._basepath['workspace'] + file):
            configFile = self._basepath['workspace'] + file
        else: return nemoa.log('warning',
            "configuration file '%s' does not exist!" % (file))

        # logger info
        nemoa.log("parsing configuration file: '" + configFile + "'")
        nemoa.log('set', indent = '+1')

        # import and register objects without testing
        importer = self._ImportConfig(self)
        obj_conf_list = importer.load(configFile)

        for obj_conf in obj_conf_list:
            if self._is_obj_known(obj_conf['class'], obj_conf['name']):
                continue
            self._add_obj_to_store(obj_conf)
        self._check(obj_conf_list)

        nemoa.log('set', indent = '-1')
        return True

    def _scan_for_networks(self, files = None):
        """Scan for networks in current workspace."""
        nemoa.log('scanning for networks')
        nemoa.log('set', indent = '+1')

        # network files path
        if files == None: files = self._path['networks'] + '*.ini'

        # scan for network files
        for path in glob.iglob(self._expand_path(files)):
            name = os.path.splitext(os.path.basename(path))[0]
            fullname = self._workspace + '.' + name
            if self._is_obj_known('network', fullname): continue

            self._add_obj_to_store({
                'class': 'network',
                'name': fullname,
                'workspace': self._workspace,
                'config': {
                    'name': name,
                    'path': path }})

        nemoa.log('set', indent = '-1')
        return True

    def _scan_for_scripts(self, files = None):
        """Scan for script files in current workspace."""
        nemoa.log('scanning for script files')
        nemoa.log('set', indent = '+1')

        # script files path
        if files == None: files = self._path['scripts'] + '*.py'

        # scan for script files
        for path in glob.iglob(self._expand_path(files)):
            name = os.path.splitext(os.path.basename(path))[0]
            fullname = self._workspace + '.' + name
            if self._is_obj_known('script', fullname): continue
            self._add_obj_to_store({
                'class': 'script',
                'name': fullname,
                'workspace': self._workspace,
                'config': {
                    'name': name,
                    'path': path }})

        nemoa.log('set', indent = '-1')
        return True

    def _check(self, obj_conf_list):
        """Check and update object configurations."""
        for obj_conf in obj_conf_list:
            obj_conf = self._check_obj_conf(obj_conf)
            if not obj_conf: self._del_obj_conf(obj_conf)
        return True

    def _check_obj_conf(self, obj_conf):
        """Check and update object configuration."""
        if not 'class' in obj_conf or not obj_conf['class']: return None
        if not 'name' in obj_conf: return None
        if not 'config' in obj_conf: return None

        if obj_conf['class'] == 'network':
            return self._update_network_config(obj_conf)
        if obj_conf['class'] == 'dataset':
            return self._update_dataset_config(obj_conf)
        if obj_conf['class'] == 'system':
            return self._update_system_config(obj_conf)
        if obj_conf['class'] == 'schedule':
            return self._update_schedule_config(obj_conf)
        if obj_conf['class'] == 'plot':
            return obj_conf

        return None

    def _update_network_config(self, obj_conf):
        """Check and update network configuration."""
        type = obj_conf['class']
        name = obj_conf['name']
        conf = obj_conf['config']

        # create 'layer', 'visible' and 'hidden' from 'layers'
        if 'layers' in conf:
            conf['layer'] = []
            conf['visible'] = []
            conf['hidden'] = []
            for layer in conf['layers']:
                if '=' in layer:
                    layer_name = layer.split('=')[0].strip()
                    layer_type = layer.split('=')[1].strip().lower()
                else:
                    layer_name = layer.strip()
                    layer_type = 'visible'

                conf['layer'].append(layer_name)
                if layer_type == 'visible':
                    conf['visible'].append(layer_name)
                else: conf['hidden'].append(layer_name)
            del conf['layers']

        # get config from source file
        if 'source' in conf:
            if not 'file' in conf['source']:
                return nemoa.log('warning', """skipping network '%s':
                    missing source information! (parameter:
                    'source:file')""" % (name))

            path = conf['source']['file']
            if not self._expand_path(path, check = True):
                return nemoa.log('warning', """skipping network '%s':
                    file '%s' not found!""" % (name, path))

            obj_conf['config']['source']['file'] = \
                self._expand_path(path)

            if not 'filetype' in conf['source']:
                obj_conf['config']['source']['filetype'] = \
                    nemoa.common.get_file_extension(path)

            filetype = obj_conf['config']['source']['filetype']

            # get network file
            if os.path.isfile(path):
                network_file = path
            elif os.path.isfile(self._path['networks'] + path):
                network_file = self._path['networks'] + path
            else:
                network_file = None

            if not network_file:
                return nemoa.log('error', """skipping network '%s':
                    file '%s' does not exist.""" % (name, path))

            # get network config
            network_cfg = nemoa.network.fileimport.load(network_file,
                filetype = filetype, workspace = self._workspace)

            if not network_cfg:
                return nemoa.log('error', """skipping network '%s':
                    could not import file '%s'."""
                    % (name, network_file))

            # update configuration
            for key in network_cfg:
                obj_conf['config'][key] = network_cfg[key]

        return obj_conf

    def _update_dataset_config(self, obj_conf, frac = 1., update = True):
        """Check and update dataset configuration."""

        type = obj_conf['class']
        name = obj_conf['name']
        conf = obj_conf['config']

        # check source
        if not 'source' in conf:
            return nemoa.log('warning', """skipping dataset '%s':
                missing source information! ('source')""" % (name))

        if not 'file' in conf['source'] \
            and not 'datasets' in conf['source']:
            return nemoa.log('warning', """skipping dataset '%s':
                missing source information! ('source:file' or
                'source:datasets')""" % (name))

        # update for source type: file
        if 'file' in conf['source']:
            source_file = conf['source']['file']
            if not self._expand_path(source_file, check = True):
                return nemoa.log('warning', """skipping dataset '%s':
                    file '%s' not found!""" % (name, source_file))

            # update path for file
            conf['source']['file'] = self._expand_path(source_file)
            #conf['import_type'] = 'file'

            # add missing source information
            if not 'filetype' in conf['source']:
                conf['source']['filetype'] = \
                    nemoa.common.get_file_extension(source_file)

            # only update in the first call of check_datasetConf
            if update: conf['cache_path'] = self._path['cache']

            return obj_conf

        # update for source type: datasets
        if 'datasets' in conf['source']:

            # add source table to config (on first call)
            if update: conf['table'] = {}

            source_list = nemoa.common.str_to_list(
                conf['source']['datasets'], ',')
            for source_name in source_list:

                # search for dataset object in register by name
                if self._is_obj_known('dataset', source_name):
                    source_id = self._get_obj_id_by_name('dataset',
                        source_name)
                elif self._is_obj_known('dataset',
                    '%s.%s' % (obj_conf['workspace'], source_name)):
                    source_name = "%s.%s" % (obj_conf['workspace'],
                        source_name)
                    source_id = self._get_obj_id_by_name('dataset',
                        source_name)
                else:
                    return nemoa.log('warning', """skipping dataset
                        '%s': unknown dataset source '%s'."""
                        % (name, source_name))

                # recursively get object configuration
                source_obj_conf = self._update_dataset_config(
                    self._get_obj_by_id(source_id),
                    frac = frac / len(source_list),
                    update = False)

                # for files create an entry in the dataset table
                if source_obj_conf['config']['type'] == 'file':

                    # update auto fraction
                    source_obj_conf['config']['fraction'] = \
                        frac / len(source_list)

                    # clean up and link config
                    source_obj_conf['config'].pop('type')
                    conf['table'][source_name] = \
                        source_obj_conf['config']

                # TODO: Test!!!
                elif source_obj_conf['config']['type'] == 'compound':
                    for child in source_obj_conf['source']['config']['table'].keys():
                        child_cnf = source_obj_conf['config']['config']['table'][child]

                        if child in obj_conf['config']['table']:
                            obj_conf['config']['table'][child]['fraction'] = \
                                obj_conf['config']['table'][child]['fraction'] + \
                                    child_cnf['fraction'] * frac / len(source_list)
                        else:
                            obj_conf['config']['table'][child] = child_cnf
                            obj_conf['config']['table'][child]['fraction'] = \
                                child_cnf['fraction'] * frac / len(source_list)

            obj_conf['config']['type'] = 'compound'

        if update: obj_conf['config']['cache_path'] = self._path['cache']

        return obj_conf

    def _update_system_config(self, obj_conf):
        """Update system configuration"""

        config = obj_conf['config']
        name = obj_conf['name']

        # system module
        if not 'package' in config:
            return nemoa.log('warning', """skipping system '%s':
                missing parameter 'package'.""" % (name))
        try:
            module_name = 'nemoa.system.%s' % (config['package'])
            system_module = importlib.import_module(module_name)
        except:
            return nemoa.log('warning', """skipping system '%s':
                module 'nemoa.system.%s' could not be imported."""
                % (name, config['package']))

        # system class
        if not 'class' in config:
            return nemoa.log('warning', """skipping system '%s':
                missing parameter 'class'.""" % (name))
        if not hasattr(system_module, config['class']):
            return nemoa.log('warning', """skipping system '%s':
                python module 'nemoa.system.%s' does not contain class
                '%s'. (parameter 'class')."""
                % (name, config['class'], config['package']))
        else:
            system_class = getattr(system_module, config['class'])

        # update system description
        if not 'about' in config:
            obj_conf['config']['about'] = system_class.__doc__
        else:
            obj_conf['config']['about'] = \
                nemoa.common.str_doc_trim(config['about'])

        # cleanup
        del system_class
        del system_module

        return obj_conf

    def _update_schedule_config(self, obj_conf):
        """Check and update schedule configuration"""

        type = obj_conf['class']
        name = obj_conf['name']
        conf = obj_conf['config']

        # create 'system'
        if not 'params' in conf or not conf['params']:
            conf['params'] = {}

            # search systems
            reSystem = re.compile('system [0-9a-zA-Z]*')
            for key in conf.keys():
                if reSystem.match(key):
                    name = key[7:].strip()
                    if not '.' in name:
                        name = obj_conf['workspace'] + '.' + name
                    conf['params'][name] = conf[key]
                    del conf[key]

        # TODO: allow stages for optimization schedule

        ## create 'stage'
        #if not 'stage' in conf or not conf['stage']:
            #conf['stage'] = []

            ## search stages
            #reStage = re.compile('stage [0-9a-zA-Z]*')
            #for key in conf.keys():
                #if reStage.match(key):
                    #conf['stage'].append(conf[key])
                    #conf['stage'][len(conf['stage']) - 1]['name'] = key[6:]
                    #del conf[key]

            #if not conf['stage'] and (not 'params' in conf or not conf['params']):
                #nemoa.log('warning',
                    #"skipping schedule '" + name + "': "
                    #"missing optimization parameters! ('params' or 'stage [NAME]')!")
                #return None

        return obj_conf

    def _add_obj_to_store(self, obj_conf):
        """link object configuration to object dictionary."""
        if not isinstance(obj_conf, dict): return False

        type = obj_conf['class']
        name = obj_conf['name']
        config = obj_conf['config']

        nemoa.log('adding %s: %s' % (type, name))

        key = None
        obj_id = 0

        if not type in self._store.keys(): return nemoa.log('error',
            """could not register object '%s':
            unsupported object type '%s'!""" % (name, type))

        key = self._get_new_key(self._store[type], name)
        obj_id = self._get_obj_id_by_name(type, key)

        # add configuration to object tree
        self._store[type][key] = config
        self._store[type][key]['id'] = obj_id

        # add entry to index
        self._index[obj_id] = {
            'type': type, 'name': key, 'workspace': obj_conf['workspace']}

        return obj_id

    def _del_obj_conf(self, obj_conf):
        """Unlink object configuration from object dictionary."""
        if not obj_conf: return False
        id = self._get_obj_id_by_name(obj_conf['class'], obj_conf['name'])
        # TODO: create useful warning
        if not id in self._index.keys(): return nemoa.log('warning', '')

        # delete entry in index
        self._index.pop(id)
        return True

    def list(self, type = None, namespace = None):
        """List known object configurations."""

        if type == 'model':
            fileExt = 'nmm'
            search_path = '%s*.%s' % (self._path['models'], fileExt)
            models = []
            for model in glob.iglob(search_path):
                if os.path.isdir(model): continue
                name = os.path.basename(model)[:-(len(fileExt) + 1)]
                models.append(name)
            return sorted(models, key = str.lower)

        # TODO: Something wents wrong if list is executed from inside
        if type == 'workspace':
            return sorted(self._list_user_workspaces())

        obj_list = []
        for id in self._index:
            if type and type != self._index[id]['type']: continue
            if namespace and namespace != self._index[id]['workspace']:
                continue
            obj_list.append((id, self._index[id]['type'],
                self._index[id]['name']))
        return sorted(obj_list, key = lambda col: col[2])

    def _is_obj_known(self, type, name):
        """Return True if object is registered."""
        return self._get_obj_id_by_name(type, name) in self._index

    def _get_obj_id_by_name(self, type, name):
        """Return id of object as integer
        calculated as hash from type and name"""
        return nemoa.common.str_to_hash(str(type) + chr(10) + str(name))

    def _get_obj_by_id(self, id):
        """Return object from store by id."""
        if not id in self._index:
            nemoa.log('warning', '2DO')
            return None

        obj_class = self._index[id]['type']
        obj_name = self._index[id]['name']
        obj_workspace = self._index[id]['workspace']
        obj_conf = self._store[obj_class][obj_name].copy()

        return {'class': obj_class, 'name': obj_name,
            'workspace': obj_workspace, 'config':  obj_conf}

    def get(self, type = None, name = None, merge = ['params'],
        params = None, id = None):
        """Return configuration as dictionary for given object."""
        if not type in self._store.keys():
            return nemoa.log('warning', """could not get configuration:
                object class '%s' is not known.""" % type)

        cfg = None

        # get configuration from type and name
        if name:
            if not name in self._store[type].keys(): return False
            cfg = self._store[type][name].copy()

        # get configuration from type and id
        elif id:
            for name in self._store[type].keys():
                if not self._store[type][name]['id'] == id: continue
                cfg = self._store[type][name]
            if cfg == None:
                return nemoa.log('warning', """could not get
                    configuration: no %s with id %i could be found."""
                    % (type, id))

        # could not identify configuration
        else:
            return nemoa.log('warning', """could not get configuration:
                'id' or 'name' of object is needed!""")

        if not cfg: return None

        # optionaly merge sub dictionaries
        # defined by a list of keys and a dictionary
        if params == None \
            or not isinstance(params, dict) \
            or not isinstance(merge, list): return cfg
        sub_merge = cfg
        for key in merge:
            if not isinstance(sub_merge, dict): return cfg
            if not key in sub_merge.keys(): sub_merge[key] = {}
            sub_merge = sub_merge[key]
        for key in params.keys():
            sub_merge[key] = params[key]
            cfg['id'] += self._get_obj_id_by_name(
                '%s.%s' % ('.'.join(merge), + key), params[key])

        return cfg

    def _expand_path(self, path, check = False, create = False):
        """Return string containing expanded path."""

        # expand variables
        path = path.strip()                # clean up input string
        path = os.path.expanduser(path)    # expand unix home directory
        path = self._expand_path_env(path) # expand nemoa env vars
        path = os.path.expandvars(path)    # expand unix env vars

        # (optional) create directory
        if create and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # (optional) check path
        if check and not os.path.exists(path):
            return nemoa.log('warning',
                "directory '%s' does not exist!" % (path))

        return path

    def _expand_path_env(self, path = ''):
        """expand nemoa environment variables in string."""

        replace = { 'workspace': self._workspace }

        update = True
        while update:
            update = False

            # expand path vars (keys of self._path)
            for var in self._path.keys():
                if '%' + var + '%' in path:
                    path = path.replace('%' + var + '%',
                        self._path[var])
                    path = path.replace('//', '/')
                    update = True

            # expand basepath variables (keys of self._basepath)
            for var in self._basepath.keys():
                if '%' + var + '%' in path:
                    path = path.replace('%' + var + '%',
                        self._basepath[var])
                    path = path.replace('//', '/')
                    update = True

            # expand other variables (keys of replace)
            for var in replace:
                if '%' + var + '%' in path:
                    path = path.replace('%' + var + '%', replace[var])
                    path = path.replace('//', '/')
                    update = True

        return path

    @staticmethod
    def _get_new_key(dict, key):

        if not key in dict: return key

        i = 1
        while True:
            i += 1 # start with 2
            new = '%s (%i)' % (key, i)
            if not new in dict: break

        return new

    class _ImportConfig:
        """import configuration file."""

        generic = None
        sections = None
        _workspace = None
        _path = None

        def __init__(self, config):
            self.generic = {
                'name': 'str',
                'type': 'str',
                'about': 'str' }

            self.sections = {
                'dataset': {'preprocessing': 'dict',
                    'source': 'dict', 'params': 'dict'},
                'system': {'package': 'str',
                    'class': 'str', 'params': 'dict'},
                'schedule': {'stage [0-9a-zA-Z]*': 'dict',
                    'system [0-9a-zA-Z]*': 'dict', 'params': 'dict'},
                'plot': {'package': 'str', 'class': 'str',
                    'params': 'dict'} }

            self._path = config.path()
            self._workspace = config.workspace()

        def load(self, file):
            """load object definition / configuration file."""

            # init parser
            cfg = ConfigParser.ConfigParser()
            cfg.optionxform = str
            cfg.read(file)

            # parse sections and create list with objects
            objects = []
            for section in cfg.sections():
                obj_conf = self._read_section(cfg, section)
                if obj_conf: objects.append(obj_conf)

            return objects

        def _read_section(self, cfg, section):
            """Parse sections."""

            # use regular expression to match sections
            reSection = re.compile('\A' + '|'.join(self.sections.keys()))
            reMatch = reSection.match(section)
            if not reMatch: return None

            type = reMatch.group()
            name = self._workspace + '.' + section[len(type):].strip()

            if type in self.sections.keys():
                config = {}

                # add generic options
                for key, frmt in self.generic.items():
                    if key in cfg.options(section): config[key] = \
                        self._convert(cfg.get(section, key), frmt)
                    else: config[key] = self._convert('', frmt)

                # add special options (use regular expressions)
                for (regExKey, frmt) in self.sections[type].items():
                    reKey = re.compile(regExKey)
                    for key in cfg.options(section):
                        if not reKey.match(key): continue
                        config[key] = self._convert(cfg.get(section, key), frmt)

            else: return None

            # get name from section name
            if config['name'] == '': config['name'] = name
            else: name = config['name']

            obj_conf = {
                'class': type,
                'name': name,
                'workspace': self._workspace,
                'config': config}

            return obj_conf

        def _convert(self, str, type):
            if type == 'str': return str.strip().replace('\n', '')
            if type == 'list': return nemoa.common.str_to_list(str)
            if type == 'dict': return nemoa.common.str_to_dict(str)
            return str
