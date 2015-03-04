# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class Session:
    """Session Manager."""

    _config = None
    _default = {
        'log': {
            'mode': 'exec',
            'indent': 0 },
        'current': {
            'workspace': None,
            'base': None,
            'path': {} },
        'default': {
            'basepath': {
                'cwd': '%user_cwd%',
                'user': ('%user_data_dir%', 'workspaces'),
                'common': ('%site_data_dir%', 'workspaces') },
            'filetype': {
                'dataset': 'csv',
                'network': 'graphml',
                'system': 'npz',
                'model': 'npz',
                'script': 'py' },
            'path': {
                'baseconf': ('%user_config_dir%', 'nemoa.ini'),
                'datasets': ('%basepath%', '%workspace%', 'datasets'),
                'networks': ('%basepath%', '%workspace%', 'networks'),
                'systems': ('%basepath%', '%workspace%', 'systems'),
                'models': ('%basepath%', '%workspace%', 'models'),
                'scripts': ('%basepath%', '%workspace%', 'scripts'),
                'cache': ('%basepath%', '%workspace%', 'cache'),
                'inifile':
                    ('%basepath%', '%workspace%', 'workspace.ini'),
                'logfile':
                    ('%basepath%', '%workspace%', 'nemoa.log') }},
        'register': {
            'dataset': {},
            'model': {},
            'network': {},
            'script': {},
            'system': {} }}

    def __init__(self, shared = True, **kwargs):
        """ """

        import os

        self._config = nemoa.common.dict.merge(kwargs, self._default)

        # enable error handling
        self.log('init')

        # update basepaths from user configuration
        configfile = self._config['default']['path']['baseconf']
        configfile = self._get_path_expand(configfile)

        if os.path.exists(configfile):
            ini_dict = nemoa.common.inifile.load(
                configfile, {
                'folders': {
                    'user': 'str',
                    'cache': 'str',
                    'common': 'str' },
                'files': {
                    'logfile': 'str' }})

            if 'folders' in ini_dict:
                for key, val in ini_dict['folders'].iteritems():
                    path = self._get_path_expand(val)
                    if path:
                        self._config['default']['basepath'][key] = path

            if 'files' in ini_dict:
                for key, val in ini_dict['files'].iteritems():
                    path = self._get_path_expand(val)
                    if path: self._config['current']['path'][key] = path

        # import shared resources
        if shared:
            for workspace in self._get_list_workspaces(base = 'common'):
                self._set_workspace_scandir(workspace, base = 'common')

    def get(self, key = 'workspace', *args, **kwargs):
        """Get meta information and content."""

        if key == 'about': return self._get_about(*args, **kwargs)
        if key == 'base': return self._get_base()
        if key == 'default': return self._get_default(*args, **kwargs)
        if key == 'list': return self._get_list(*args, **kwargs)
        #if key == 'mode': return self._get_mode(*args, **kwargs)
        if key == 'path': return self._get_path(*args, **kwargs)
        if key == 'workspace': return self._get_workspace()

        if key in self._config['register']:
            return self._get_objconfig(key, *args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _get_about(self, key = 'about', *args, **kwargs):
        """Get nemoa meta information."""

        if key == 'about': return nemoa.__description__
        if key == 'version': return nemoa.__version__
        if key == 'status': return nemoa.__status__
        if key == 'description': return nemoa.__doc__.strip()
        if key == 'url': return nemoa.__url__
        if key == 'license': return nemoa.__license__
        if key == 'copyright': return nemoa.__copyright__
        if key == 'author': return nemoa.__author__
        if key == 'email': return nemoa.__email__
        if key == 'maintainer': return nemoa.__maintainer__
        if key == 'credits': return nemoa.__credits__

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _get_base(self):
        """Get name of current workspace search path."""
        return self._config['current'].get('base', None) or 'cwd'

    def _get_basepath(self, base = None):
        """Get path of given or current workspace search path."""

        if not base:
            base = self._get_base()
        elif not base in self._config['default']['basepath']:
            return None
        mask = self._config['default']['basepath'][base]

        return self._get_path_expand(mask)

    def _get_default(self, key = None, *args, **kwargs):
        """Get default value."""
        
        import copy
        
        if not key: return copy.deepcopy(self._config['default'])
        elif not key in self._config['default']:
            return nemoa.log('error', """could not get default value:
                key '%s' is not valid.""" % key)
        retval = self._config['default'][key]
        parent = key
        while args:
            if not isinstance(args[0], basestring) \
                or not args[0] in retval:
                return nemoa.log('error', """could not get default
                    value: '%s' does not contain key '%s'.""" %
                    (parent, args[0]))
            parent = args[0]
            retval = retval[args[0]]
            args = args[1:]
        
        if isinstance(retval, dict): return copy.deepcopy(retval)
        return retval

    def _get_list(self, key = None, *args, **kwargs):
        """Get list. """

        if key == None:
            retval = {}
            workspace = self._get_workspace()
            base = self._get_base()
            for key in self._config['register']:
                keys = key + 's'
                objlist = self._get_list(keys,
                    workspace = workspace, base = base)
                retval[keys] = objlist
            return retval
        if key == 'bases':
            return self._get_list_bases(*args, **kwargs)
        if key == 'workspaces':
            return self._get_list_workspaces(*args, **kwargs)
        if key in [rkey + 's' for rkey in self._config['register']]:
            if not 'base' in kwargs:
                kwargs['base'] = self._get_base()
            if not 'workspace' in kwargs:
                kwargs['workspace'] = self._get_workspace()
            if not 'attribute' in kwargs:
                kwargs['attribute'] = 'name'
            return self._get_objconfigs(key[:-1], *args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _get_list_bases(self, workspace = None):
        """Get list of searchpaths containing given workspace name."""

        if workspace == None:
            return sorted(self._config['default']['basepath'].keys())
        bases = []
        for base in self._config['default']['basepath']:
            if workspace in self._get_list_workspaces(base = base):
                bases.append(base)

        return sorted(bases)

    def _get_list_workspaces(self, base = None):
        """Get list of workspaces in given searchpath."""

        if not base:
            workspaces = {}
            for base in self._config['default']['basepath']:
                workspaces[base] = \
                    self._get_list_workspaces(base = base)
            return workspaces
        elif not base in self._config['default']['basepath']:
            return nemoa.log('error', """could not get workspaces:
                unknown workspace base '%s'.""" % base)

        basepath = self._config['default']['basepath'][base]
        baseglob = self._get_path_expand((basepath, '*'))

        import glob
        import os

        workspaces = []
        fname = self._config['default']['path']['inifile'][-1]
        for subdir in glob.iglob(baseglob):
            if not os.path.isdir(subdir): continue
            fpath = nemoa.common.ospath.get_valid_path(subdir, fname)
            if not os.path.isfile(fpath): continue
            workspaces.append(os.path.basename(subdir))

        return sorted(workspaces)

    def _get_objconfig(self, objtype, name = None,
        workspace = None, base = 'user', attribute = None):
        """Get configuration of given object as dictionary."""

        if not objtype in self._config['register']:
            return nemoa.log('warning', """could not get configuration:
                object class '%s' is not supported.""" % objtype)
        if not isinstance(name, basestring):
            return nemoa.log('warning', """could not get %s:
                name of object is not valid.""" % objtype)

        # (optional) load workspace of given object
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()
        if workspace == None:
            workspace = cur_workspace
            base = cur_base
        elif not workspace == cur_workspace or not base == cur_base:
            if not self._set_workspace(workspace, base = base):
                nemoa.log('warning', """could not get configuration:
                    workspace '%s' does not exist.""" % workspace)
                return  {}

        # find object configuration in workspace
        search = [name, '%s.%s.%s' % (base, workspace, name),
            name + '.default', 'base.' + name]
        config = None
        for fullname in search:
            if fullname in self._config['register'][objtype]:
                config = self._config['register'][objtype][fullname]
                break

        # (optional) load current workspace
        if cur_workspace:
            if not workspace == cur_workspace or not base == cur_base:
                self._set_workspace(cur_workspace, base = cur_base)

        if not config:
            return nemoa.log('warning', """could not get configuration:
                %s with name '%s' is not found in %s workspace '%s'.
                """ % (objtype, name, base, workspace))

        if not attribute: return config
        elif not isinstance(attribute, basestring):
            return nemoa.log('warning', """could not get configuration:
                attribute is not vlid.""")
        elif not attribute in config:
            return nemoa.log('warning', """could not get configuration:
                attribute '%s' is not valid.""" % attribute)

        return config[attribute]

    def _get_objconfigs(self, objtype = None, workspace = None,
        base = None, attribute = 'name'):
        """Get registered object configurations of given type."""

        if not objtype:
            objs = {}
            for obj in self._config['register']:
                objs[obj] = self._get_objconfigs(objtype = obj,
                    workspace = workspace, base = base)
            return objs

        if objtype:
            if not objtype in self._config['register']: return False

        # create dictionary
        objlist = []
        for key in self._config['register'].keys():
            if objtype and not key == objtype: continue
            for obj in self._config['register'][key].itervalues():
                if base and not base == obj['base']:
                    continue
                if workspace and not workspace == obj['workspace']:
                    continue
                if attribute and not attribute in obj:
                    continue
                if attribute: objlist.append(obj[attribute])
                else: objlist.append(obj)

        if attribute: return sorted(objlist)
        return sorted(objlist, key = lambda obj: obj['name'])

    def _get_path(self, key = None, *args, **kwargs):
        """Get path of given object or object type."""

        if key == 'basepath':
            return self._get_basepath(*args, **kwargs)

        # change current workspace if necessary
        chdir = False
        workspace = self._get_workspace()
        base = None
        if 'workspace' in kwargs:
            workspace = kwargs['workspace']
            del kwargs['workspace']
            if not workspace == self._get_workspace(): chdir = True
        if 'base' in kwargs:
            base = kwargs['base']
            del kwargs['base']
            if not base == self._get_base(): chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(workspace, base = base)

        # get path
        if key == None:
            import copy
            path = copy.deepcopy(self._config['current']['path'])
        elif key == 'expand':
            if 'workspace' in kwargs: del kwargs['workspace']
            if 'base' in kwargs: del kwargs['base']
            path = self._get_path_expand(*args, **kwargs)
        elif key in self._config['current']['path']:
            path = self._config['current']['path'][key]
        elif key in self._config['register']:
            name = kwargs.get('name', None) \
                or (args[0] if len(args) > 0 else None)
            path = self._get_objconfig(objtype = key, name = name,
                attribute = 'path')
        else:
            path = nemoa.log('warning', """could not get path:
                path identifier '%s' is not valid.""" % key) or None

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base = current.get('base'))
            else:
                self._set_workspace(None)

        return path or None

    def _get_path_expand(self, *args, **kwargs):
        """Get expanded path.

        Args:
            path (string or tuple or list):
            check (bool):
            create (bool):
        
        Returns:
            String containing expanded path.
        
        """

        import os

        path = nemoa.common.ospath.get_norm_path(args)
        check = kwargs.get('check', False)
        create = kwargs.get('create', False)

        # expand nemoa environment variables
        base = self._get_base()
        replace = {
            'workspace': self._get_workspace(),
            'base': self._get_base(),
            'basepath': nemoa.common.ospath.get_norm_path(
                self._config['default']['basepath'][base]) }
        for key, val in self._config['default']['basepath'].iteritems():
            replace[key] = nemoa.common.ospath.get_norm_path(val)
        for key, val in self._config['current']['path'].iteritems():
            replace[key] = nemoa.common.ospath.get_norm_path(val)
        for key in ['user_cache_dir', 'user_config_dir',
            'user_data_dir', 'user_log_dir', 'user_cwd',
            'site_config_dir', 'site_data_dir']:
            replace[key] = nemoa.common.ospath.getstorage(
                key, appname = 'nemoa', appauthor = 'Froot')

        update = True
        while update:
            update = False
            for key, val in replace.items():
                if not '%' + key + '%' in path:
                    continue
                try:
                    path = path.replace('%' + key + '%', val)
                except TypeError:
                    del replace[key]
                update = True

        # (optional) create directory
        if create and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # (optional) check path
        if check and not os.path.exists(path): return None

        return path

    def _get_workspace(self):
        """Get name of current workspace."""
        return self._config['current'].get('workspace', '')

    def log(self, key = None, *args, **kwargs):
        """Log message."""

        if not key: return True

        if key == 'init': return self._log_init(*args, **kwargs)
        if key == 'set': return self._log_set(*args, **kwargs)
        if key == 'get': return self._log_get(*args, **kwargs)

        import inspect
        import logging
        import platform
        import traceback

        indent = self._config['log']['indent']
        toplevel = (indent == 0)
        mode = self._config['log']['mode']

        # get arguments
        if len(args) == 0:
            msg = key
            key = 'info'
        if len(args) == 1:
            msg = args[0]

        # define colors (platform dependent workaround)
        systype = platform.system().lower()
        if systype == 'windows':
            color = {
                'blue': '',
                'yellow': '',
                'red': '',
                'green': '',
                'default': ''}
        else:
            color = {
                'blue': '\033[94m',
                'yellow': '\033[93m',
                'red': '\033[91m',
                'green': '\033[92m',
                'default': '\033[0m' }

        # get loggers
        loggers = logging.Logger.manager.loggerDict.keys()
        tty_log = logging.getLogger(__name__ + '.tty') \
            if __name__ + '.tty' in loggers \
            else logging.getLogger(__name__ + '.null')
        file_log = logging.getLogger(__name__ + '.file') \
            if __name__ + '.file' in loggers \
            else logging.getLogger(__name__ + '.null')

        # format message
        msg = msg.strip().replace('\n', '')
        while '  ' in msg: msg = msg.replace('  ', ' ')

        if mode == 'shell':
            pre = color['blue'] + '> ' + color['default']
            tty_msg = msg
        else:
            pre = ''
            tty_msg = '  ' * indent + msg

        # create file message
        clr_stack = inspect.stack()[1]
        clr_method = clr_stack[3]
        clr_module = inspect.getmodule(clr_stack[0]).__name__
        clr_name = clr_module + '.' + clr_method
        file_msg = clr_name + ' -> ' + msg.strip()

        # create logging records (depending on loglevels)
        if key == 'info':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if mode == 'shell': return True
            else:
                if toplevel: tty_log.info(
                    color['blue'] + tty_msg + color['default'])
                else: tty_log.info(tty_msg)
            return True

        if key == 'note':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if not toplevel or mode == 'shell': tty_log.info(pre + tty_msg)
            else: tty_log.info(color['blue'] + tty_msg + color['default'])
            return True

        if key == 'header':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if mode == 'shell' and not toplevel: return True
            tty_log.info(color['green'] + tty_msg + color['default'])
            return True

        if key == 'warning':
            if not mode == 'silent':
                tty_log.warning(pre + color['yellow'] \
                    + tty_msg + color['default'])
            file_log.warning(file_msg)
            return False

        if key == 'error':
            tty_log.error(pre + color['yellow'] + tty_msg
                + ' (see logfile for debug info)' + color['default'])
            file_log.error(file_msg)
            for line in traceback.format_stack():
                msg = line.strip().replace(
                    '\n', '-> ').replace('  ', ' ').strip()
                file_log.error(msg)
            return False

        if key == 'critical':
            tty_log.critical(pre + color['yellow'] \
                + tty_msg + color['default'])
            file_log.critical(file_msg)
            return False

        if key == 'debuginfo':
            if mode == 'debug': file_log.error(file_msg)
            return False

        if key == 'console':
            tty_log.info(pre + tty_msg)
            return True

        if key == 'logfile':
            file_log.info(file_msg)
            return True

        return self.log('warning', "unknown logging command '%s'!" % (cmd))

    def _log_init(self, *args, **kwargs):
        """ """

        import os
        import logging

        # initialize null logger, remove all previous handlers
        # and set up null handler
        logger_null = logging.getLogger(__name__ + '.null')
        for h in logger_null.handlers: logger_null.removeHandler(h)
        if hasattr(logging, 'NullHandler'):
            null_handler = logging.NullHandler()
            logger_null.addHandler(null_handler)

        # initialize console logger, remove all previous handlers
        # and set up console handler
        logger_console = logging.getLogger(__name__ + '.tty')
        logger_console.setLevel(logging.INFO)
        for h in logger_console.handlers:
            logger_console.removeHandler(h)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(fmt = '%(message)s'))
        logger_console.addHandler(console_handler)

        # initialize file logger, remove all previous handlers
        # and set up file handler
        if not 'logfile' in kwargs or not kwargs['logfile']:
            return True
        logfile = kwargs['logfile']

        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        logger_file = logging.getLogger(__name__ + '.file')
        logger_file.setLevel(logging.INFO)
        for h in logger_file.handlers: logger_file.removeHandler(h)
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(logging.Formatter(
            fmt = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%m/%d/%Y %H:%M:%S'))
        logger_file.addHandler(file_handler)

        return True

    def _log_set(self, *args, **kwargs):
        """ """
        
        # set logging mode
        if 'mode' in kwargs and kwargs['mode'] \
            in ['debug', 'exec', 'shell', 'silent']:
            self._config['log']['mode'] = kwargs['mode']

        # set indent
        if 'indent' in kwargs:
            if isinstance(kwargs['indent'], int):
                self._config['log']['indent'] = kwargs['indent']
            elif isinstance(kwargs['indent'], str) \
                and kwargs['indent'][0] in ['+', '-']:
                size = int(kwargs['indent'][1:])
                self._config['log']['indent'] += size \
                    if kwargs['indent'][0] == '+' else -size
                    
        return True

    def _log_get(self, *args, **kwargs):
        """ """
            
        # return global logging parameters.
        if len(args) == 0:
            return self._config['log']
        if len(args) == 1 and args[0] in self._config['log'].keys():
            return self._config['log'][args[0]]

        return False

    def run(self, script = None, *args, **kwargs):
        """ """

        import imp
        import os

        retval = True

        # change current workspace if necessary
        chdir = False
        workspace = self._get_workspace()
        base = None
        if 'workspace' in kwargs:
            workspace = kwargs['workspace']
            del kwargs['workspace']
            if not workspace == self._get_workspace(): chdir = True
        if 'base' in kwargs:
            base = kwargs['base']
            del kwargs['base']
            if not base == self._get_base(): chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(workspace, base = base)

        # get configuration and run script
        config = self.get('script', name = script, *args, **kwargs)
        if not isinstance(config, dict) or not 'path' in config:
            retval = nemoa.log('warning', """could not run script '%s':
                invalid configuration.""" % script)
        elif not os.path.isfile(config['path']):
            retval = nemoa.log('warning', """could not run script '%s':
                file '%s' not found.""" % (script, config['path']))
        else:
            module = imp.load_source('script', config['path'])
            module.main(self._config['workspace'], *args, **kwargs)
        
        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base = current.get('base'))
            else:
                self._set_workspace(None)
        
        return retval
    
    def set(self, key, *args, **kwargs):
        """Set configuration parameters and env vars."""

        # 2do: set(workspace = '', base = '')
        if key == 'workspace':
            return self._set_workspace(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _set_workspace(self, workspace, base = None,
        refresh = False, scandir = True, setlog = True):
        """Set workspace."""

        if not workspace:
            nemoa.log('init', logfile = None)
            self._config['workspace'] = None
            self._config['current']['path'] = {}
            self._config['current']['workspace'] = None
            self._config['current']['base'] = None
            return True
        if workspace == self._get_workspace() and not refresh:
            # 2do: do not ignore base
            return True
        if not base:
            bases = self._get_list_bases(workspace)
            if not bases:
                return nemoa.log('warning', """could not open workspace
                    '%s': workspace could not be found
                    in any searchpath.""" % workspace) or None
            if len(bases) > 1:
                return nemoa.log('warning', """could not open workspace
                    '%s': workspace found in different searchpaths:
                    %s.""" % (workspace, ', '.join(bases))) or None
            base = bases[0]
        elif not workspace in self._get_list_workspaces(base = base):
            basepath = self._get_path_expand(
                self._config['default']['basepath'][base])
            return nemoa.log('warning', """could not open workspace
                '%s': workspace could not be found in searchpath
                '%s'.""" % (workspace, basepath)) or None

        # set current workspace name and workspace base name
        self._config['current']['workspace'] = workspace
        self._config['current']['base'] = base

        # update paths from default path structure
        for key, val in self._config['default']['path'].items():
            self._config['current']['path'][key] = \
                self._get_path_expand(val)

        # (optional) initialise logfile of new workspace
        if setlog:
            logpath = self._get_path_expand(
                self._config['current']['path']['logfile'])
            nemoa.log('init', logfile = logpath)

        # open workspace
        self._config['workspace'] = \
            nemoa.workspace.open(workspace, base = base)

        # (optional) scan workspace folder for objects / files
        if scandir:
            self._set_workspace_scandir()

        return True

    def _set_workspace_scandir(self, *args, **kwargs):
        """Scan workspace for files."""

        import glob

        # change current workspace if necessary
        chdir = False
        workspace = self._get_workspace()
        base = None
        if 'workspace' in kwargs:
            workspace = kwargs['workspace']
            del kwargs['workspace']
            if not workspace == self._get_workspace(): chdir = True
        if 'base' in kwargs:
            base = kwargs['base']
            del kwargs['base']
            if not base == self._get_base(): chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(workspace, base = base)

        # scan workspace for objects
        for objtype in self._config['register'].keys():
            filemask = self._get_path_expand(
                self._config['current']['path'][objtype + 's'], '*.*')
            if objtype == 'dataset':
                filetypes = nemoa.dataset.imports.filetypes()
            elif objtype == 'network':
                filetypes = nemoa.network.imports.filetypes()
            elif objtype == 'system':
                filetypes = nemoa.system.imports.filetypes()
            elif objtype == 'model':
                filetypes = nemoa.model.imports.filetypes()
            elif objtype == 'script':
                filetypes = ['py']

            # scan for files
            for path in glob.iglob(filemask):
                filetype = nemoa.common.ospath.fileext(path)
                if not filetype in filetypes: continue
                iname = nemoa.common.ospath.basename(path)
                iworkspace = self._get_workspace()
                ibase = self._get_base()
                fullname = '%s.%s.%s' % (ibase, iworkspace, iname)
                
                if fullname in self._config['register'][objtype]:
                    continue

                # add configuration to object tree
                self._config['register'][objtype][fullname] = {
                    'name': iname,
                    'type': objtype,
                    'path': path,
                    'workspace': iworkspace,
                    'base': ibase,
                    'fullname': fullname }

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base = current.get('base'))
            else:
                self._set_workspace(None)

        return True
