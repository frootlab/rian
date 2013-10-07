# -*- coding: utf-8 -*-
import metapath.common as mp
import os
import re
import ConfigParser
import glob

class config:
    """
    configuration management
    """

    def __init__(self):

        # internal configuration
        self.__baseconf = 'metapath.ini'

        # configuration storage (dict + index)
        self.__store = {
            'system': {},
            'network': {},
            'dataset': {},
            'schedule': {},
            'analyse': {},
            'plot': {},
            'report': {} }
        self.__index = {}

        # current project and paths
        self.__project = None
        self.__path = {}
        self.__basepath = None
        self.__projectPath = None

        # update base paths
        self.__updateBasepath()

    def __updateBasepath(self):
        if not os.path.exists(self.__baseconf):
            return False

        # default basepaths
        self.__basepath = {
            'user': '~/metapath/',
            'common': '/etc/metapath/common/' }

        # get basepath configuration
        cfg = ConfigParser.ConfigParser()
        cfg.optionxform = str
        cfg.read(self.__baseconf)

        # [folders]
        if 'folders' in cfg.sections():
            for key in ['user', 'cache', 'common']:
                if not key in cfg.options('folders'):
                    continue
                val  = cfg.get('folders', key)
                path = self.getPath(val)
                if path:
                    self.__basepath[key] = path

        # [files]
        if 'files' in cfg.sections():
            for key in ['logfile']:
                if not key in cfg.options('files'):
                    continue
                val  = cfg.get('files', key)
                self.__path[key] = self.getPath(val)

        return True

    def __updatePaths(self, base = 'user'):

        self.__projectPath = {
            'workspace': '%project%/',
            'datasets': '%project%/data/',
            'models': '%project%/models/',
            'networks': '%project%/networks/',
            'plots': '%project%/plots/',
            'reports': '%project%/reports/',
            'cache': '%project%/cache/',
            'logfile': '%project%/metapath.log'
        }

        if base in ['user', 'common']:
            if base == 'user':
                allowWrite = True
            else:
                allowWrite = False
            for key in self.__projectPath:
                self.__path[key] = self.getPath(
                    '%' + base + '%/' + self.__projectPath[key], create = allowWrite)

    def __listUserProjects(self):
        """
        return list of user projects
        """

        projects = []
        prjDirs = self.__basepath['user'] + '*'
        for prjDir in glob.iglob(self.getPath(prjDirs)):
            if not os.path.isdir(prjDir):
                continue

            projects.append(os.path.basename(prjDir))

        return projects

    def __listCommonProjects(self):
        """
        return list of common projects
        """

        projects = []
        prjDirs = self.__basepath['common'] + '*'
        for prjDir in glob.iglob(self.getPath(prjDirs)):
            if not os.path.isdir(prjDir):
                continue

            projects.append(os.path.basename(prjDir))

        return projects

    def project(self):
        """
        return name of current project
        """
        return self.__project

    def path(self, key = None):
        """
        return path
        """
        if isinstance(key, str) and key in self.__path.keys():
            if isinstance(self.__path[key], dict):
                return self.__path[key].copy()
            return self.__path[key]
        return self.__path.copy()

    def loadCommon(self):
        """
        import common projects
        """
        mp.log('comment', 'import common configuration files')

        # get current project
        curProject = self.__project
        
        # 
        for project in self.__listCommonProjects():

            # set common project, update paths and import workspaces
            self.__project = project
            self.__updatePaths(base = 'common')
            self.__importConfigFilesFromProject()

        # reset to previous project
        self.__project = curProject

        return True

    def loadProject(self, project):
        """
        import configuration files from user project
        """
        mp.log('comment', 'import project configuration files')

        # check if project exists
        if not project in self.__listUserProjects():
            mp.log('warning', """
                could not load project '%s':
                project folder could not be found in '%s'!
                """ % (project, self.__basepath['user']))
            return False
        
        # set project
        self.__project = project

        # update paths
        self.__updatePaths(base = 'user')

        # update logger to current logfile
        mp.initLogger(logfile = self.__path['logfile'])

        # import workspaces of current project
        self.__importConfigFilesFromProject()

        # update path of cache
        self.__updateCachePaths()

        return True

    def __updateCachePaths(self):
        """
        update dataset cache paths to current project
        """
        for key in self.__store['dataset']:
            self.__store['dataset'][key]['cache_path'] = self.__path['cache']
        return True

    # configuration files

    def __importConfigFilesFromProject(self, files = None):
        """
        import all config files from current project
        """

        # are files given?
        if files == None:
            files = self.__path['workspace'] + '*.ini'

        # import definition files
        for file in glob.iglob(self.getPath(files)):
            self.__importConfigFile(file)

        return True

    def __importConfigFile(self, file):
        """
        Import config file
        """

        # search definition file
        if os.path.isfile(file):
            configFile = file
        elif os.path.isfile(self.__basepath['workspace'] + file):
            configFile = self.__basepath['workspace'] + file
        else:
            mp.log("warning", "configuration file '%s' does not exist!" % (file))
            return False

        # logger info
        mp.log("info", "import configuration file: '" + configFile + "'")

        # import and register objects without testing
        importer = configFileImporter(self)
        objConfList = importer.load(configFile)

        for objConf in objConfList:
            self.__addObjToStore(objConf)

        self.__check(objConfList)

        return True

    def __importNetworkConfigFile(self, file, format = None):
        """
        Import network configuration from file
        """

        # file
        file = self.getPath(file).strip()

        # search network file
        if os.path.isfile(self.__path['networks'] + file):
            file = os.path.abspath(self.__path['networks'] + file)
        elif os.path.isfile(file):
            file = os.path.abspath(file)
        else:
            mp.log("warning", "network file '" + file + "' does not exist!")
            return None

        # format
        if not format:
            file_name = os.path.basename(file)
            file_ext  = os.path.splitext(file_name)[1]
            format    = file_ext.lstrip('.').strip().lower()

        if format == 'ini':
            importer = networkConfigFileImporter()
            return importer.load(file)

        return None

    def __check(self, objConfList):
        """
        Check (and update) object configurations and delete invalid objects
        """
        for objConf in objConfList:
            objConf = self.__checkObjConf(objConf)
            if not objConf:
                self.__delObjConf(objConf)
        return True

    def __checkObjConf(self, objConf):
        """
        Check and update object configuration
        """
    
        if not 'class' in objConf or not objConf['class']:
            return None
        if not 'name' in objConf:
            return None
        if not 'config' in objConf:
            return None

        if objConf['class'] == 'network':
            return self.__checkNetworkConf(objConf)
        if objConf['class'] == 'dataset':
            return self.__checkDatasetConf(objConf)
        if objConf['class'] == 'system':
            return self.__checkSystemConf(objConf)
        if objConf['class'] == 'schedule':
            return self.__checkScheduleConf(objConf)

        # analse: get from source
        if objConf['class'] == 'analyse':
            if not 'plots' in conf:
                objConf['config']['plots'] = []
            return objConf

        # plot: get from source
        if objConf['class'] == 'plot':
            return objConf

        return None

    def __checkNetworkConf(self, objConf):
        """
        Check and update network configuration
        """
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
                if layerType == 'visible':
                    conf['visible'].append(layerName)
                else:
                    conf['hidden'].append(layerName)
            del conf['layers']

        # get config from source file
        if 'source' in conf:
            if not 'file' in conf['source']:
                mp.log("warning", 
                    "skipping network '" + name + "': "
                    "missing source information! (parameter: 'source:file')")
                return None

            file = conf['source']['file']
            if not self.getPath(file, check = True):
                mp.log("warning", 
                    "skipping network '" + name + "': "
                    "file '" + file + "' does not exist!" )
                return None
            objConf['config']['source']['file'] = self.getPath(file)

            if not 'file_format' in conf['source']:
                objConf['config']['source']['file_format'] = mp.getFileExt(file)

            format = objConf['config']['source']['file_format']

            # get network config
            networkCfg = self.__importNetworkConfigFile(file, format)
            for key in networkCfg:
                objConf['config'][key] = networkCfg[key]

        return objConf

    def __checkDatasetConf(self, objConf, frac = 1.0, update = True):
        """
        Check and update dataset configuration
        """

        # allready configured?
        #if not 'class' in objConf.keys():
        #    return objConf

        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # check source
        if not 'source' in conf:
            mp.log("warning", 
                "skipping dataset '" + name + "': "
                "missing source information! (parameter 'source')")
            return None

        if not 'file' in conf['source'] and not 'datasets' in conf['source']:
            mp.log("warning", 
                "skipping dataset '" + name + "': "
                "missing source information! (parameter: 'source:file' or 'source:datasets')")
            return None

        # update for source type: file
        if 'file' in conf['source']:
            file = conf['source']['file']
            if not self.getPath(file, check = True):
                mp.log("warning", 
                    "skipping dataset '" + name + "': "
                    "file '" + file + "' does not exist!" )
                return None

            # update path for file and set type to 'file'
            conf['source']['file'] = self.getPath(file)
            conf['type'] = 'file'

            # add missing source information
            if not 'file_format' in conf['source']:
                conf['source']['file_format'] = mp.getFileExt(file)
            
            # only update in the first call of checkDatasetConf
            if update:
                conf['cache_path'] = self.__path['cache']

            return objConf

        # update for source type: datasets
        if 'datasets' in conf['source']:

            # add source table to config (on first call)
            if update:
                conf['table'] = {}

            srcList = mp.strToList(conf['source']['datasets'], ',')
            for srcName in srcList:

                # search for dataset object in register by name
                if self.__isObjKnown('dataset', srcName):
                   srcID = self.__getObjIDByName('dataset', srcName)
                elif self.__isObjKnown('dataset', "%s.%s" % (objConf['project'], srcName)):
                   srcName = "%s.%s" % (objConf['project'], srcName)
                   srcID = self.__getObjIDByName('dataset', srcName)
                else:
                    mp.log("warning",
                        "skipping dataset '" + name + "': "
                        "unknown dataset source '" + srcName + "'" )
                    return None

                # recursively get object configuration
                srcObjConf = self.__checkDatasetConf(
                    self.__getObjByID(srcID),
                    frac = frac / len(srcList),
                    update = False)

                # for files create an entry in the dataset table
                if srcObjConf['config']['type'] == 'file':

                    # update auto fraction
                    srcObjConf['config']['source']['fraction'] = frac / len(srcList)

                    # clean up and link config
                    srcObjConf['config'].pop('type')
                    conf['table'][srcName] = srcObjConf['config']

                #
                # 2DO: Te3st!!!
                #

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

        if update:
            objConf['config']['cache_path'] = self.__path['cache']

        return objConf

    def __checkSystemConf(self, objConf):
        """
        Check and update system configuration
        """
        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        if not 'package' in conf:
            mp.log("warning", 
                "skipping system '" + name + "': "
                "missing parameter 'package'!")
            return None

        if not 'class' in conf:
            mp.log("warning", 
                "skipping system '" + name + "': "
                "missing parameter 'class'!")
            return None

        if not 'description' in conf:
            conf['description'] = conf['name']
        else:
            conf['description'] = conf['description'].replace('\n', '')

        # check if system exists
        try:
            exec "import metapath.system." + conf['package']
            found = True
        except:
            found = False

        if not found:
            mp.log("warning", 
                "skipping system '" + name + "': "
                "package 'system." + conf['package'] + "' could not be found!")
            return None

        return objConf

    def __checkScheduleConf(self, objConf):
        """
        Check and update schedule configuration
        """
        
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

        ####
        #
        # 2DO: REPAIR STAGES IN OPTIMIZATION!!!!!!
        #
        ####

        """
        # create 'stage'
        if not 'stage' in conf or not conf['stage']:
            conf['stage'] = []

            # search stages
            reStage = re.compile('stage [0-9a-zA-Z]*')
            for key in conf.keys():
                if reStage.match(key):
                    conf['stage'].append(conf[key])
                    conf['stage'][len(conf['stage']) - 1]['name'] = key[6:]
                    del conf[key]

            if not conf['stage'] and (not 'params' in conf or not conf['params']):
                mp.log("warning", 
                    "skipping schedule '" + name + "': "
                    "missing optimization parameters! ('params' or 'stage [NAME]')!")
                return None
        """

        return objConf

    def __addObjToStore(self, objConf):
        """
        Add object configuration to object tree
        """
        type = objConf['class']
        name = objConf['name']
        config = objConf['config']

        key = None
        objID = 0

        if not type in self.__store.keys():
            mp.log('error', '2DO')
            return False

        key = self.__getNewKey(self.__store[type], name)
        objID = self.__getObjIDByName(type, key)

        # add configuration to object tree
        self.__store[type][key] = config
        self.__store[type][key]['id'] = objID

        # add entry to index
        self.__index[objID] = {'type': type, 'name': key, 'project': objConf['project']}

        return objID

    def __delObjConf(self, objConf):
        """
        Delete object configuration from object store
        """
        if not objConf:
            return False
        id = self.__getObjIDByName(objConf['class'], objConf['name'])
        if not id in self.__index.keys():
            mp.log('warning', '2do')
            return False

        # delete configuration from tree
        
        
        # delete entry in index
        self.__index.pop(id)
        return True

    def list(self, type = None):
        """
        List configurations
        """

        if type == 'model':
            models = []
            for model in glob.iglob(self.__path['models'] + '*.mp'):
                if os.path.isdir(model):
                    continue

                models.append(os.path.basename(model)[:-3])

            return sorted(models, key = str.lower)
        
        objList = []
        for id in self.__index:
            if type and type != self.__index[id]['type']:
                continue

            objList.append((id, self.__index[id]['type'], self.__index[id]['name']))
        return objList

    def __isObjKnown(self, type, name):
        """
        Return true if object is registered
        """
        return self.__getObjIDByName(type, name) in self.__index

    def __getObjIDByName(self, type, name):
        """
        Return id of object as integer
        calculated as hash from type and name
        """
        return mp.strToHash(str(type) + chr(10) + str(name))

    def __getObjByID(self, id):
        """
        Return object from store by id
        """
        if not id in self.__index:
            mp.log('warning', '2DO')
            return None

        oClass = self.__index[id]['type']
        oName  = self.__index[id]['name']
        oPrj   = self.__index[id]['project']
        oConf  = self.__store[oClass][oName].copy()

        return {'class': oClass, 'name': oName, 'project': oPrj, 'config':  oConf}

    def get(self, type = None, name = None, merge = ['params'], params = None, id = None):
        """
        Return configuration as dictionary for given object
        """
        if not type in self.__store.keys():
            mp.log('warning', """
                could not get configuration:
                object class '%s' is not known
                """ % type)
            return None

        # search 'name' or 'id' in 'section' or take first entry
        cfg = None

        # get configuration from type and name
        if name:
            if name in self.__store[type].keys():
                cfg = self.__store[type][name].copy()
            elif 'base.' + name in self.__store[type].keys():
                cfg = self.__store[type]['base.' + name].copy()
            else:
                mp.log('warning', """
                    could not get configuration:
                    no %s with name '%s' could be found
                    """ % (type, name))
                return None

        # get configuration from type and id
        elif id:
            for name in self.__store[type].keys():
                if not self.__store[type][name]['id'] == id:
                    continue
                cfg = self.__store[type][name]
            if cfg == None:
                mp.log('warning', """
                    could not get configuration:
                    no %s with id %i could be found
                    """ % (type, id))
                return None
        
        # could not identify configuration
        else:
            mp.log('warning', """
                could not get configuration:
                'id' or 'name' of object is needed
                """)
            return None

        if not cfg:
            return None

        # optionaly merge sub dictionaries
        # defined by a list of keys and a dictionary
        if params == None \
            or not isinstance(params, dict)\
            or not isinstance(merge, list):
            return cfg
        subMerge = cfg
        for key in merge:
            if not isinstance(subMerge, dict):
                return cfg
            if not key in subMerge.keys():
                subMerge[key] = {}
            subMerge = subMerge[key]
        for key in params.keys():
            subMerge[key] = params[key]
            cfg['id'] += self.__getObjIDByName('.'.join(merge) + '.' + key, params[key])

        return cfg

    def getPath(self, str, check = False, create = False):
        """
        resolve path
        """

        # clean up input string
        path = str.strip()

        # replace metapath vars
        replace = {
            'project': self.__project }

        update = True
        while update:
            update = False

            # replace path keys with values
            for var in self.__path.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self.__path[var])
                    path   = path.replace('//', '/')
                    update = True

            # replace basepath keys with values
            for var in self.__basepath.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self.__basepath[var])
                    path   = path.replace('//', '/')
                    update = True

            # replace other vars
            for var in replace:
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', replace[var])
                    path   = path.replace('//', '/')
                    update = True

        # create paths
        if create:
            dir = os.path.dirname(path)
            if not os.path.exists(dir):
                os.makedirs(dir)

        # check path
        if check and not os.path.exists(path):
            mp.log('warning', "path '%s' does not exist!" % (path))
            return False

        return path

    def __getNewKey(self, dict, key):

        if not key in dict:
            return key

        i = 1
        while True:
            i += 1 # start with 2
            new = '%s (%i)' % (key, i)
            if not new in dict:
                break

        return new

#
# import metapath config file
#

class configFileImporter:

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
            'plot': {'package': 'str', 'class': 'str', 'params': 'dict'},
            'analyse': {'plots': 'list', 'reports': 'list', 'params': 'dict'} }

        self.__path = config.path()
        self.project = config.project()

    #
    # definition files
    #

    def load(self, file):

        # init parser
        cfg = ConfigParser.ConfigParser()
        cfg.optionxform = str
        cfg.read(file)

        # parse sections and create list with objects
        objects = []
        for section in cfg.sections():
            objCfg = self.__readSection(cfg, section)
            if objCfg:
                objects.append(objCfg)

        return objects

    def __readSection(self, cfg, section):
        """
        parse sections
        """

        # use regular expression to match sections
        reSection = re.compile('\A' + '|'.join(self.sections.keys()))
        reMatch = reSection.match(section)
        if not reMatch:
            return None

        type = reMatch.group()
        name = self.project + '.' + section[len(type):].strip()

        if type in self.sections.keys():
            config = {}

            # add generic options
            for key, frmt in self.generic.items():
                if key in cfg.options(section):
                    config[key] = self.__convert(cfg.get(section, key), frmt)
                else:
                    config[key] = self.__convert('', frmt)

            # add special options (use regular expressions)
            for (regExKey, frmt) in self.sections[type].items():
                reKey = re.compile(regExKey)
                for key in cfg.options(section):
                    if not reKey.match(key):
                        continue
                    config[key] = self.__convert(cfg.get(section, key), frmt)

        else:
            return None

        # get name from section name
        if config['name'] == '':
            config['name'] = name
        else:
            name = config['name']

        objCfg = {
            'class':   type,
            'name':    name,
            'project': self.project,
            'config':  config}

        return objCfg

    def __convert(self, str, type):
        if type == 'str':
            return str.strip().replace('\n', '')
        if type == 'list':
            return mp.strToList(str)
        if type == 'dict':
            return mp.strToDict(str)
        return str

class networkConfigFileImporter:

    def __init__(self):
        pass

    def load(self, file):
        netcfg = ConfigParser.ConfigParser()
        netcfg.optionxform = str
        netcfg.read(file)
        network = {}

        # validate 'network' section
        if not 'network' in netcfg.sections():
            mp.log("warning", 
                "skipping section '" + section + "': "
                "network file '" + file + "' does not contain section 'network'!")
            return None

        # 'nodes': annotation, default: 'none'
        if 'nodes' in netcfg.options('network'):
            network['label_format'] = netcfg.get('network', 'nodes').strip()
        else:
            network['label_format'] = 'generic:string'

        # type
        if 'type' in netcfg.options('network'):
            network['type'] = netcfg.get('network', 'type').strip().lower()
        else:
            network['type'] = 'auto'

        # 'layers'
        if 'layers' in netcfg.options('network'):
            layer = mp.strToList(netcfg.get('network', 'layers'))
            network['layer']   = []
            network['visible'] = []
            network['hidden']  = []
            for l in layer:
                type = l.split(':')[0]
                name = l.split(':')[1]
                network['layer'].append(name)
                if type == 'visible':
                    network['visible'].append(name)
                else:
                    network['hidden'].append(name)
        else:
            mp.log("warning", 
                "skipping section '" + section + "': "
                "network file '" + network['file'] + "' missing parameter 'layers'!")
            return None
        if network['visible'] == []:
            mp.log("warning", 
                "skipping section '" + section + "': "
                "network file '" + network['file'] + "' does not contain visible layers!")
            return None
        if network['hidden'] == []:
            mp.log("warning", 
                "skipping section '" + section + "': "
                "network file '" + network['file'] + "' does not contain hidden layers!")
            return None

        # get nodes and edges from binding sections
        nodes = {}
        edges = {}
        for i in range(len(network['layer']) - 1):
            layerA = network['layer'][i]
            layerB = network['layer'][i + 1]

            if not layerA in nodes:
                nodes[layerA] = []
            if not layerB in nodes:
                nodes[layerB] = []

            edge_type = layerA + '-' + layerB
            edge_section = edge_type + ' binding'
            edges[edge_type] = []

            for nodeA in netcfg.options(edge_section):
                nodeA = nodeA.strip()
                if nodeA == '':
                    continue
                if not nodeA in nodes[layerA]:
                    nodes[layerA].append(nodeA)
                nodesB = mp.strToList(netcfg.get(edge_section, nodeA))
                for nodeB in nodesB:
                    nodeB = nodeB.strip()
                    if nodeB == '':
                        continue
                    if not nodeB in nodes[layerB]:
                        nodes[layerB].append(nodeB)
                    if not (nodeA, nodeB) in edges[edge_type]:
                        edges[edge_type].append((nodeA, nodeB))

        network['nodes'] = nodes
        network['edges'] = edges

        return network
