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

class workspace:
    """Nemoa workspace."""

    def __init__(self, workspace = None):
        """Initialize shared configuration."""
        nemoa.workspace._init()
        if workspace: self.load(workspace)

    def load(self, workspace):
        """Import workspace and update paths and logfile."""
        return nemoa.workspace.load(workspace)

    def name(self):
        """Return name of workspace."""
        return nemoa.workspace.name()

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
        """Execute nemoa script."""
        scriptName = name \
            if '.' in name else '%s.%s' % (self.name(), name)
        config = nemoa.workspace._get_config(
            type = 'script', config = scriptName, **kwargs)

        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = nemoa.workspace._get_config(
                type = 'script', config = scriptName, **kwargs)
        if not config: return False
        if not os.path.isfile(config['path']):
            return nemoa.log('error', """could not run script '%s':
            file '%s' not found!""" % (scriptName, config['path']))

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
            if not name in self.list(type = 'model'): return \
                nemoa.log('error', """could not import model:
                a model with name '%s' does not exists!""" % (name))
            return self._import_model(name)

        # check keyword arguments
        if not ('network' in kwargs and 'dataset' in kwargs \
            and 'system' in kwargs): return nemoa.log('error',
                """could not create model:
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
        if not nemoa.type.isInstanceType(instance, type):
            nemoa.log('error', """could not create %s instance:
                invalid configuration!""" % (type))
            nemoa.log('set', indent = '-1')
            return None

        nemoa.log('name of %s is: \'%s\'' % (type, instance.name()))
        nemoa.log('set', indent = '-1')
        return instance

    def _create_new_model(self, name, config = None,
        dataset = None, network = None, system = None,
        configure = True, initialize = True):
        nemoa.log('create new model')
        nemoa.log('set', indent = '+1')

        model = self._get_model_instance(name = name, config  = config,
            dataset = dataset, network = network, system  = system)

        if not nemoa.type.isModel(model):
            nemoa.log('error', 'could not create new model!')
            nemoa.log('set', indent = '-1')
            return False

        if configure: model.configure() # configure model
        if initialize: model.initialize() # initialize model parameters

        nemoa.log('set', indent = '-1')
        return model

    def _get_model_instance(self, name = None, config = None,
        dataset = None, network = None, system = None):
        """Return new model instance."""

        nemoa.log('create model instance')
        nemoa.log('set', indent = '+1')

        # create dataset instance (if not given)
        if not nemoa.type.isDataset(dataset): dataset = \
            self._get_instance(type = 'dataset', config = dataset)
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error',
                'could not create model instance: dataset is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create network instance (if not given)
        if network == None: network = {'type': 'auto'}
        if not nemoa.type.isNetwork(network): network = \
            self._get_instance(type = 'network', config = network)
        if not nemoa.type.isNetwork(network):
            nemoa.log('error',
                'could not create model instance: network is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create system instance (if not given)
        if not nemoa.type.isSystem(system): system = \
            self._get_instance(type = 'system', config = system)
        if not nemoa.type.isSystem(system):
            nemoa.log('error',
                'could not create model instance: system is invalid!')
            nemoa.log('set', indent = '-1')
            return None

        # create name string (if not given)
        if name == None: name = '-'.join(
            [dataset.name(), network.name(), system.name()])

        # create model instance
        model = self._get_instance(
            type = 'model', config = config, name = name,
            dataset = dataset, network = network, system = system)

        nemoa.log('set', indent = '-1')
        return model

    def _import_model(self, file):
        """Import model from file.

        Opens gzip compressed model configuration and parameters. The
        configuration is first used to configure and init a new dataset,
        network and system instance and finally a new model instance.
        After this the parameters of the model are overwritten by the
        parameters from the file.

        Args:
            file: Path to nemoa model file (with fileextension .nmm)

        Returns:
            Nemoa model instance

        """

        nemoa.log('import model from file')
        nemoa.log('set', indent = '+1')

        # check file
        if not os.path.exists(file):
            if os.path.exists(
                nemoa.workspace.path('models') + file + '.nmm'):
                file = nemoa.workspace.path('models') + file + '.nmm'
            else: return nemoa.log('error',
                """could not load model '%s':
                file does not exist.""" % file)

        # load model configuration and parameters from file
        nemoa.log("load model: '%s'" % file)
        modelDict = nemoa.common.dict_from_file(file)

        # create new dataset, network, system and model instances
        model = self._get_model_instance(
            name    = modelDict['config']['name'],
            config  = modelDict['config'],
            dataset = modelDict['dataset']['cfg'],
            network = modelDict['network']['cfg'],
            system  = modelDict['system']['config'])
        if not nemoa.type.isModel(model): return None

        # copy configuration and parameters to model instance
        model._set(modelDict)

        nemoa.log('set', indent = '-1')
        return model

    # TODO: move to model base class as model.copy
    def _copy_model(self, model):
        """Return copy of model instance"""

        # get configuration and parameters from original model
        model_config = model._get_config()
        dataset_config = model.dataset._get_config()
        network_config = model.network._get_config()
        system_config = model.system._get_config()
        model_config_and_params = model._get()

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
        # model to the copy
        model_copy._set(model_config_and_params)

        return model_copy

class config:
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
        self._basepath = { # default basepaths
            'user': '~/.nemoa/', 'common': '/etc/nemoa/common/' }
        self._update_basepath() # update paths for shared and user
        # init tree structure for configuration storage
        self._store = {'dataset': {}, 'network': {}, 'system': {},
            'plot': {}, 'schedule': {}, 'script': {}}
        self._index = {}

        if shared: self._import_shared() # import shared resources

    def _update_basepath(self):
        if not os.path.exists(self._baseconf): return False

        # get basepath configuration
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
                val  = cfg.get('files', key)
                self._path[key] = self._expand_path(val)

        return True

    def _update_paths(self, base = 'user'):

        self._workspace_path = {
            'workspace': '%project%/',
            'datasets': '%project%/data/',
            'models': '%project%/models/',
            'scripts': '%project%/scripts/',
            'networks': '%project%/networks/',
            'plots': '%project%/plots/',
            'cache': '%project%/cache/',
            'logfile': '%project%/nemoa.log'
        }

        if base in ['user', 'common']:
            allowWrite = {'user': True, 'common': False}[base]
            for key in self._workspace_path:
                self._path[key] = self._expand_path('%' + base + '%/'
                    + self._workspace_path[key], create = allowWrite)

    def _list_user_workspaces(self):
        """Return list of private workspaces."""
        userDir = self._expand_path(self._basepath['user'])
        return [os.path.basename(w) for w in glob.iglob(userDir + '*')
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
        curWorkspace = self._workspace

        # import shared resources and update paths
        for workspace in self._list_shared_workspaces():
            self._workspace = workspace
            self._update_paths(base = 'common')
            self._scan_config_files()
            self._scan_scripts()
            self._scan_networks()

        # reset to current workspace
        self._workspace = curWorkspace

        nemoa.log('set', indent = '-1')
        return True

    def load(self, workspace):
        """Import configuration files from workspace."""
        nemoa.log('import private resources')
        nemoa.log('set', indent = '+1')

        # check if workspace exists
        if not workspace in self._list_user_workspaces(): return nemoa.log(
            'warning', """could not open workspace '%s':
            workspace folder could not be found in '%s'!
            """ % (workspace, self._basepath['user']))

        self._workspace = workspace # set workspace
        self._update_paths(base = 'user') # update paths
        self._update_cache_paths() # update path of cache
        nemoa.log('init', logfile = self._path['logfile']) # update logger
        self._scan_config_files() # import configuration files
        self._scan_scripts() # scan for scriptfiles
        self._scan_networks() # scan for network configurations

        nemoa.log('set', indent = '-1')
        return True

    def _update_cache_paths(self):
        """Update dataset cache paths to current workspace."""
        for key in self._store['dataset']:
            self._store['dataset'][key]['cache_path'] = self._path['cache']
        return True

    def _scan_config_files(self, files = None):
        """Import configuration files from current workspace."""
        nemoa.log('scanning for configuration files')
        nemoa.log('set', indent = '+1')

        # assert configuration files path
        if files == None: files = self._path['workspace'] + '*.ini'
        # import configuration files
        for file in glob.iglob(self._expand_path(files)):
            self._import_config_file(file)

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
        objConfList = importer.load(configFile)

        for objConf in objConfList: self._add_obj_to_store(objConf)
        self._check(objConfList)

        nemoa.log('set', indent = '-1')
        return True

    def _scan_scripts(self, files = None):
        """Scan for scripts files (current project)."""
        nemoa.log('scanning for script files')
        nemoa.log('set', indent = '+1')

        # assert script files path
        if files == None: files = self._path['scripts'] + '*.py'
        # import scripts files
        for file in glob.iglob(self._expand_path(files)):
            self._register_script(file)

        nemoa.log('set', indent = '-1')
        return True

    def _register_script(self, file):
        """Register script file (current workspace)."""
        if os.path.isfile(file): scriptFile = file
        elif os.path.isfile(self._path['scripts'] + file):
            scriptFile = self._path['scripts'] + file
        else: return nemoa.log('warning',
            "script file '%s' does not exist!" % (file))

        # import and register scripts (without testing)
        importer = self._ImportScript(self)
        script = importer.load(scriptFile)
        self._add_obj_to_store(script)
        return True

    def _scan_networks(self, files = None):
        """Scan for network configuration files (current workspace)."""
        nemoa.log('scanning for networks')
        nemoa.log('set', indent = '+1')

        # assert network files path
        if files == None: files = self._path['networks'] + '*.ini'
        # import network files
        for file in glob.iglob(self._expand_path(files)):
            self._register_network(file)

        nemoa.log('set', indent = '-1')
        return True

    def _register_network(self, file, format = None):
        """Register network (current workspace)."""
        if os.path.isfile(file): networkFile = file
        elif os.path.isfile(self._path['networks'] + file):
            networkFile = self._path['networks'] + file
        else: return nemoa.log('warning',
            "network file '%s' does not exist!" % (file))

        # if format is not given get format from file extension
        if not format:
            fileName = os.path.basename(file)
            fileExt  = os.path.splitext(fileName)[1]
            format    = fileExt.lstrip('.').strip().lower()

        # get network configuration from file
        if format == 'ini':
            importer = self._ImportNetworkIni(self)
            return self._add_obj_to_store(importer.load(networkFile))

        return nemoa.log('error',
            """could not import network '%s':
            network file format '%s' is currently not supported!
            """ % (file, format))

    def _check(self, objConfList):
        """Check and update object configurations."""
        for objConf in objConfList:
            objConf = self._check_obj_conf(objConf)
            if not objConf: self._del_obj_conf(objConf)
        return True

    def _check_obj_conf(self, objConf):
        """Check and update object configuration."""
        if not 'class'  in objConf or not objConf['class']: return None
        if not 'name'   in objConf: return None
        if not 'config' in objConf: return None

        if objConf['class'] == 'network':  return self._check_network(objConf)
        if objConf['class'] == 'dataset':  return self._check_dataset(objConf)
        if objConf['class'] == 'system':   return self._check_system(objConf)
        if objConf['class'] == 'schedule': return self._check_schedule(objConf)
        if objConf['class'] == 'plot':     return objConf

        return None

    def _check_network(self, objConf):
        """Check and update network configuration."""
        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # create 'layer', 'visible' and 'hidden' from 'layers'
        if 'layers' in conf:
            conf['layer']   = []
            conf['visible'] = []
            conf['hidden']  = []
            for layer in conf['layers']:
                if '=' in layer:
                    layerName = layer.split('=')[0].strip()
                    layerType = layer.split('=')[1].strip().lower()
                else:
                    layerName = layer.strip()
                    layerType = 'visible'

                conf['layer'].append(layerName)
                if layerType == 'visible': conf['visible'].append(layerName)
                else: conf['hidden'].append(layerName)
            del conf['layers']

        # get config from source file
        if 'source' in conf:
            if not 'file' in conf['source']: return nemoa.log('warning',
                "skipping network '" + name + "': "
                "missing source information! (parameter: 'source:file')")

            file = conf['source']['file']
            if not self._expand_path(file, check = True): return nemoa.log('warning',
                "skipping network '%s': file '%s' not found!" % (name, file))

            objConf['config']['source']['file'] = self._expand_path(file)

            if not 'file_format' in conf['source']:
                objConf['config']['source']['file_format'] = nemoa.common.getFileExt(file)

            format = objConf['config']['source']['file_format']

            # get network config
            networkCfg = self._register_network(file, format)
            if not networkCfg: return nemoa.log('warning',
                "skipping network '%s'" % (name))
            for key in networkCfg: objConf['config'][key] = networkCfg[key]

        return objConf

    def _check_dataset(self, objConf, frac = 1., update = True):
        """Check and update dataset configuration."""

        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # check source
        if not 'source' in conf: return nemoa.log('warning',
            "skipping dataset '" + name + "': "
            "missing source information! (parameter 'source')")

        if not 'file' in conf['source'] \
            and not 'datasets' in conf['source']: return nemoa.log('warning',
            "skipping dataset '" + name + "': "
            "missing source information! (parameter: 'source:file' or 'source:datasets')")

        # update for source type: file
        if 'file' in conf['source']:
            file = conf['source']['file']
            if not self._expand_path(file, check = True): return nemoa.log('warning',
                "skipping dataset '%s': file '%s' not found!" % (name, file))

            # update path for file and set type to 'file'
            conf['source']['file'] = self._expand_path(file)
            conf['type'] = 'file'

            # add missing source information
            if not 'file_format' in conf['source']:
                conf['source']['file_format'] = nemoa.common.getFileExt(file)

            # only update in the first call of checkDatasetConf
            if update: conf['cache_path'] = self._path['cache']

            return objConf

        # update for source type: datasets
        if 'datasets' in conf['source']:

            # add source table to config (on first call)
            if update: conf['table'] = {}

            srcList = nemoa.common.strToList(conf['source']['datasets'], ',')
            for srcName in srcList:

                # search for dataset object in register by name
                if self._is_obj_known('dataset', srcName):
                   srcID = self._get_obj_id_by_name('dataset', srcName)
                elif self._is_obj_known('dataset', "%s.%s" % (objConf['project'], srcName)):
                   srcName = "%s.%s" % (objConf['project'], srcName)
                   srcID = self._get_obj_id_by_name('dataset', srcName)
                else: return nemoa.log('warning',
                    "skipping dataset '" + name + "': "
                    "unknown dataset source '" + srcName + "'" )

                # recursively get object configuration
                srcObjConf = self._check_dataset(
                    self._get_obj_by_id(srcID),
                    frac = frac / len(srcList),
                    update = False)

                # for files create an entry in the dataset table
                if srcObjConf['config']['type'] == 'file':

                    # update auto fraction
                    srcObjConf['config']['fraction'] = frac / len(srcList)

                    # clean up and link config
                    srcObjConf['config'].pop('type')
                    conf['table'][srcName] = srcObjConf['config']

                # 2do: Test!!!
                elif srcObjConf['config']['type'] == 'compound':
                    for child in srcObjConf['source']['config']['table'].keys():
                        childCnf = srcObjConf['config']['config']['table'][child]

                        if child in objConf['config']['table']:
                            objConf['config']['table'][child]['fraction'] = \
                                objConf['config']['table'][child]['fraction'] + \
                                    childCnf['fraction'] * frac / len(srcList)
                        else:
                            objConf['config']['table'][child] = childCnf
                            objConf['config']['table'][child]['fraction'] = \
                                childCnf['fraction'] * frac / len(srcList)

            objConf['config']['type'] = 'compound'

        if update: objConf['config']['cache_path'] = self._path['cache']

        return objConf

    def _check_system(self, objConf):
        """Check and update system configuration"""
        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        if not 'package' in conf: return nemoa.log('warning',
            "skipping system '" + name + "': missing parameter 'package'!")
        if not 'class' in conf: return nemoa.log('warning',
            "skipping system '" + name + "': missing parameter 'class'!")

        conf['description'] = conf['description'].replace('\n', '') \
            if 'description' in conf else conf['name']

        # check if system exists
        try: exec "import nemoa.system." + conf['package']
        except: return nemoa.log('warning',
            "skipping system '%s': package 'system.%s' could not be found!" % (name, conf['package']))
        return objConf

    def _check_schedule(self, objConf):
        """Check and update schedule configuration"""

        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # create 'system'
        if not 'params' in conf or not conf['params']:
            conf['params'] = {}

            # search systems
            reSystem = re.compile('system [0-9a-zA-Z]*')
            for key in conf.keys():
                if reSystem.match(key):
                    name = key[7:].strip()
                    if not '.' in name:
                        name = objConf['project'] + '.' + name
                    conf['params'][name] = conf[key]
                    del conf[key]

        # 2do: allow stages for optimization schedule

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

        return objConf

    def _add_obj_to_store(self, objConf):
        """link object configuration to object dictionary."""
        if not isinstance(objConf, dict): return False

        type = objConf['class']
        name = objConf['name']
        config = objConf['config']

        nemoa.log('adding %s: %s' % (type, name))

        key = None
        objID = 0

        if not type in self._store.keys(): return nemoa.log('error',
            """could not register object '%s':
            unsupported object type '%s'!""" % (name, type))

        key = self._get_new_key(self._store[type], name)
        objID = self._get_obj_id_by_name(type, key)

        # add configuration to object tree
        self._store[type][key] = config
        self._store[type][key]['id'] = objID

        # add entry to index
        self._index[objID] = {
            'type': type, 'name': key, 'project': objConf['project']}

        return objID

    def _del_obj_conf(self, objConf):
        """Unlink object configuration from object dictionary."""
        if not objConf: return False
        id = self._get_obj_id_by_name(objConf['class'], objConf['name'])
        if not id in self._index.keys(): return nemoa.log('warning', '2do')

        # delete entry in index
        self._index.pop(id)
        return True

    def list(self, type = None, namespace = None):
        """List known object configurations."""

        if type == 'model':
            fileExt = 'nmm'
            searchPath = '%s*.%s' % (self._path['models'], fileExt)
            models = []
            for model in glob.iglob(searchPath):
                if os.path.isdir(model): continue
                name = os.path.basename(model)[:-(len(fileExt) + 1)]
                models.append(name)
            return sorted(models, key = str.lower)

        # TODO: Something wents wrong if list is executed from inside
        if type == 'workspace':
            return sorted(self._list_user_workspaces())

        objList = []
        for id in self._index:
            if type and type != self._index[id]['type']: continue
            if namespace and namespace != self._index[id]['project']: continue
            objList.append((id, self._index[id]['type'], self._index[id]['name']))
        return sorted(objList, key = lambda col: col[2])

    def _is_obj_known(self, type, name):
        """Return True if object is registered."""
        return self._get_obj_id_by_name(type, name) in self._index

    def _get_obj_id_by_name(self, type, name):
        """Return id of object as integer
        calculated as hash from type and name"""
        return nemoa.common.strToHash(str(type) + chr(10) + str(name))

    def _get_obj_by_id(self, id):
        """Return object from store by id."""
        if not id in self._index:
            nemoa.log('warning', '2DO')
            return None

        oClass = self._index[id]['type']
        oName  = self._index[id]['name']
        oPrj   = self._index[id]['project']
        oConf  = self._store[oClass][oName].copy()

        return {'class': oClass, 'name': oName, 'project': oPrj, 'config':  oConf}

    def get(self, type = None, name = None, merge = ['params'], params = None, id = None):
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
            if cfg == None: return nemoa.log('warning',
                """could not get configuration:
                no %s with id %i could be found """ % (type, id))

        # could not identify configuration
        else: return nemoa.log('warning',
            """could not get configuration:
            'id' or 'name' of object is needed!""")

        if not cfg: return None

        # optionaly merge sub dictionaries
        # defined by a list of keys and a dictionary
        if params == None \
            or not isinstance(params, dict) \
            or not isinstance(merge, list): return cfg
        subMerge = cfg
        for key in merge:
            if not isinstance(subMerge, dict): return cfg
            if not key in subMerge.keys(): subMerge[key] = {}
            subMerge = subMerge[key]
        for key in params.keys():
            subMerge[key] = params[key]
            cfg['id'] += self._get_obj_id_by_name(
                '%s.%s' % ('.'.join(merge), + key), params[key])

        return cfg

    def _expand_path(self, str, check = False, create = False):
        """Return string containing expanded path."""

        path = str.strip()               # clean up input string
        path = os.path.expanduser(path)  # expand unix home directory
        path = self._expand_path_env(path) # expand nemoa env vars
        path = os.path.expandvars(path)  # expand unix env vars

        # (optional) create directory
        if create and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # (optional) check path
        if check and not os.path.exists(path): return nemoa.log(
            'warning', "directory '%s' does not exist!" % (path))

        return path

    def _expand_path_env(self, path = ''):
        """Expand nemoa environment variables in string"""

        replace = { 'project': self._workspace }

        update = True
        while update:
            update = False

            # expand path vars (keys of self._path)
            for var in self._path.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self._path[var])
                    path   = path.replace('//', '/')
                    update = True

            # expand basepath variables (keys of self._basepath)
            for var in self._basepath.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self._basepath[var])
                    path   = path.replace('//', '/')
                    update = True

            # expand other variables (keys of replace)
            for var in replace:
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', replace[var])
                    path   = path.replace('//', '/')
                    update = True

        return path

    def _get_new_key(self, dict, key):

        if not key in dict: return key

        i = 1
        while True:
            i += 1 # start with 2
            new = '%s (%i)' % (key, i)
            if not new in dict: break

        return new

    # import config file
    class _ImportConfig:
        generic  = None
        sections = None
        project  = None

        def __init__(self, config):
            self.generic = {
                'name': 'str',
                'description': 'str' }

            self.sections = {
                'network': {'type': 'str', 'layers': 'list', 'labels': 'list', 'source': 'dict', 'params': 'dict'},
                'dataset': {'preprocessing': 'dict', 'source': 'dict', 'params': 'dict'},
                'system': {'package': 'str', 'class': 'str', 'params': 'dict'},
                'schedule': {'stage [0-9a-zA-Z]*': 'dict', 'system [0-9a-zA-Z]*': 'dict', 'params': 'dict'},
                'plot': {'package': 'str', 'class': 'str', 'params': 'dict'} }

            self._path = config.path()
            self.project = config.workspace()

        # object definition / configuration files

        def load(self, file):

            # init parser
            cfg = ConfigParser.ConfigParser()
            cfg.optionxform = str
            cfg.read(file)

            # parse sections and create list with objects
            objects = []
            for section in cfg.sections():
                objCfg = self._read_section(cfg, section)
                if objCfg: objects.append(objCfg)

            return objects

        def _read_section(self, cfg, section):
            """Parse sections."""

            # use regular expression to match sections
            reSection = re.compile('\A' + '|'.join(self.sections.keys()))
            reMatch = reSection.match(section)
            if not reMatch: return None

            type = reMatch.group()
            name = self.project + '.' + section[len(type):].strip()

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

            objCfg = {
                'class': type,
                'name': name,
                'project': self.project,
                'config': config}

            return objCfg

        def _convert(self, str, type):
            if type == 'str': return str.strip().replace('\n', '')
            if type == 'list': return nemoa.common.strToList(str)
            if type == 'dict': return nemoa.common.strToDict(str)
            return str

    # import script files
    class _ImportScript:

        def __init__(self, config):
            self.project = config.workspace()

        def load(self, file):
            name = self.project + '.' + os.path.splitext(os.path.basename(file))[0]
            path = file

            return {
                'class': 'script',
                'name': name,
                'project': self.project,
                'config': {
                    'name': name,
                    'path': path }}

    # import network files
    class _ImportNetworkIni:

        workspace  = None

        def __init__(self, config):
            self.workspace = config.workspace()

        def load(self, file):
            """Return network configuration as dictionary.

            Args:
                file: .ini configuration file used to generate nemoa
                    network compatible network configuration dictionary.

            """

            netcfg = ConfigParser.ConfigParser()
            netcfg.optionxform = str
            netcfg.read(file)

            name = os.path.splitext(os.path.basename(file))[0]
            fullname = '.'.join([self.workspace, name])

            network = {
                'class': 'network',
                'name': fullname,
                'project': self.workspace,
                'config': {
                    'package': 'base',
                    'class': 'network',
                    'type': None,
                    'name': name,
                    'source': {
                        'file': file,
                        'file_format': 'ini' }}}

            # validate 'network' section
            if not 'network' in netcfg.sections(): return nemoa.log(
                'warning', """could not import network configuration:
                file '%s' does not contain section 'network'!""" % (file))

            # name of network ('name')
            if 'name' in netcfg.options('network'):
                network_name = netcfg.get('network', 'name').strip()
                network['config']['name'] = network_name
                network['name'] = \
                    '.'.join([self.workspace, network_name])

            # short description of the network ('description')
            if 'description' in netcfg.options('network'):
                network['config']['description'] = \
                    netcfg.get('network', 'description').strip()
            else: network['config']['description'] = ''

            # python module containing the network class ('package')
            if 'package' in netcfg.options('network'):
                network['config']['package'] = \
                    netcfg.get('network', 'package').strip()

            # python network class inside module ('class')
            if 'class' in netcfg.options('network'):
                network['config']['class'] = \
                    netcfg.get('network', 'class').strip()

            # type of network ('type')
            # currently supported:
            #     'layer': layered feedforward network
            if 'type' in netcfg.options('network'):
                network['config']['type'] = \
                    netcfg.get('network', 'type').strip().lower()
            else: network['config']['type'] = 'auto'

            # TODO: make network type specific sections
            # 'labelformat': annotation of nodes, default: 'generic:string'
            if 'labelformat' in netcfg.options('network'):
                network['config']['label_format'] \
                    = netcfg.get('network', 'nodes').strip()
            else: network['config']['label_format'] = 'generic:string'

            # depending on type, use different class methods to parse
            # and interpret type specific parameters and sections
            if network['config']['type'] in ['layer', 'auto']:
                return self._parse_layer_network(file, netcfg, network)

            return nemoa.log('warning',
                """could not import network configuration:
                file '%s' contains unsupported network type '%s'.""" %
                (file, network['config']['type']))

        def _parse_layer_network(self, file, netcfg, network):

            config = network['config']

            # 'layers': ordered list of network layers
            if not 'layers' in netcfg.options('network'):
                return nemoa.log('warning', """file '%s' does not
                    contain parameter 'layers'.""" % (file))
            else: config['layer'] = nemoa.common.strToList(
                netcfg.get('network', 'layers'))

            # init network dictionary
            config['visible'] = []
            config['hidden']  = []
            config['nodes']   = {}
            config['edges']   = {}

            # parse '[layer *]' sections and add nodes
            # and layer types to network dict
            for layer in config['layer']:
                layerSec = 'layer ' + layer
                if not layerSec in netcfg.sections():
                    return nemoa.log('warning', """file '%s' does not
                        contain information about layer '%s'."""
                        % (file, layer))

                # get type of layer ('type')
                # layer type can be ether 'visible' or 'hidden'
                if not 'type' in netcfg.options(layerSec):
                    return nemoa.log('warning', """type of layer '%s'
                        has to be specified ('visible', 'hidden')!"""
                        % (layer))
                if netcfg.get(layerSec, 'type').lower() in ['visible']:
                    config['visible'].append(layer)
                elif netcfg.get(layerSec, 'type').lower() in ['hidden']:
                    config['hidden'].append(layer)
                else: return nemoa.log('warning',
                    "unknown type of layer '" + layer + "'!")

                # get nodes of layer from given list file ('file')
                if 'file' in netcfg.options(layerSec):
                    file_str = netcfg.get(layerSec, 'file')
                    listFile = nemoa.workspace._expand_path(file_str)
                    if not os.path.exists(listFile):
                        return nemoa.log('error', """listfile '%s'
                            does not exists!""" % (listFile))
                    with open(listFile, 'r') as listFile:
                        fileLines = listFile.readlines()
                    nodeList = [node.strip() for node in fileLines]
                # get nodes of layer from given list ('nodes')
                elif 'nodes' in netcfg.options(layerSec):
                    node_str = netcfg.get(layerSec, 'nodes')
                    nodeList = nemoa.common.strToList(node_str)
                # get nodes of layer from given layer size ('size')
                elif 'size' in netcfg.options(layerSec):
                    layer_size = int(netcfg.get(layerSec, 'size'))
                    nodeList = []
                    for n in xrange(1, layer_size + 1):
                        nodeList.append('n%s' % (n))
                else:
                    return nemoa.log('warning',
                        """layer '%s' does not contain
                        node information!""" % (layer))

                config['nodes'][layer] = []
                for node in nodeList:
                    node = node.strip()
                    if node == '': continue
                    if not node in config['nodes'][layer]:
                        config['nodes'][layer].append(node)

            # check network layers
            if config['visible'] == []: return nemoa.log('error',
                "layer network '" + file + "' does not contain visible layers!")

            # parse '[binding *]' sections and add edges to network dict
            for i in xrange(len(config['layer']) - 1):
                layerA = config['layer'][i]
                layerB = config['layer'][i + 1]

                edgeType = layerA + '-' + layerB
                config['edges'][edgeType] = []
                edgeSec = 'binding ' + edgeType

                # create full binfing between two layers if not specified
                if not edgeSec in netcfg.sections():
                    for nodeA in config['nodes'][layerA]:
                        for nodeB in config['nodes'][layerB]:
                            config['edges'][edgeType].append((nodeA, nodeB))
                    continue

                # get edges from '[binding *]' section
                for nodeA in netcfg.options(edgeSec):
                    nodeA = nodeA.strip()
                    if nodeA == '' or \
                        not nodeA in config['nodes'][layerA]: continue
                    for nodeB in nemoa.common.strToList(netcfg.get(edgeSec, nodeA)):
                        nodeB = nodeB.strip()
                        if nodeB == '' \
                            or not nodeB in config['nodes'][layerB] \
                            or (nodeA, nodeB) in config['edges'][edgeType]:
                            continue
                        config['edges'][edgeType].append((nodeA, nodeB))

            # check network binding
            for i in xrange(len(config['layer']) - 1):
                layerA = config['layer'][i]
                layerB = config['layer'][i + 1]

                edgeType = layerA + '-' + layerB
                if config['edges'][edgeType] == []: return nemoa.log('warning',
                    "layer '%s' and layer '%s' are not connected!" % (layerA, layerB))

            return network
