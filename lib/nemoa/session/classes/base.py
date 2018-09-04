# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class Session:
    """Session Manager."""

    _buffer = {}
    _config = None
    _default = {
        'current': {
            'workspace': None,
            'base': None,
            'mode': 'exec',
            'path': {},
            'shell': {
                'buffmode': 'line' }},
        'default': {
            'basepath': {
                'cwd': '%user_cwd%',
                'user': ('%user_data_dir%', 'workspaces'),
                'site': ('%site_data_dir%', 'workspaces') },
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

    def __init__(self, site = True, **kwargs):
        """ """

        import os
        import sys

        from nemoa.common.dict import merge
        from nemoa.common import ioini

        self._config = merge(kwargs, self._default)

        # reset workspace to default values
        self._set_workspace_reset()

        # initialize exception handler
        self._init_exception_handler()

        # update basepaths from user configuration
        configfile = self._config['default']['path']['baseconf']
        configfile = self._get_path_expand(configfile)

        if os.path.exists(configfile):
            ini_dict = ioini.load(configfile, {
                'folders': {
                    'user': 'str',
                    'cache': 'str',
                    'site': 'str' },
                'files': {
                    'logfile': 'str' }})

            if 'folders' in ini_dict:
                for key, val in ini_dict['folders'].items():
                    path = self._get_path_expand(val)
                    if path:
                        self._config['default']['basepath'][key] = path

            if 'files' in ini_dict:
                for key, val in ini_dict['files'].items():
                    path = self._get_path_expand(val)
                    if path: self._config['current']['path'][key] = path

    def create(self, key = None, *args, **kwargs):
        """Open object in current session."""
        if key == 'model':
            return nemoa.model.create(*args, **kwargs)
        if key == 'network':
            return nemoa.network.create(*args, **kwargs)
        if key == 'dataset':
            return nemoa.dataset.create(*args, **kwargs)
        if key == 'system':
            return nemoa.system.create(*args, **kwargs)
        return None

    def get(self, key = 'workspace', *args, **kwargs):
        """Get meta information and content."""

        if key == 'about': return self._get_about(*args, **kwargs)
        if key == 'base': return self._get_base()
        if key == 'default': return self._get_default(*args, **kwargs)
        if key == 'list': return self._get_list(*args, **kwargs)
        if key == 'mode': return self._get_mode(*args, **kwargs)
        if key == 'path': return self._get_path(*args, **kwargs)
        if key == 'shell': return self._get_shell(*args, **kwargs)
        if key == 'workspace': return self._get_workspace()

        if key in self._config['register']:
            return self._get_objconfig(key, *args, **kwargs)

        raise KeyError(f"unknown key '{key}'")

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

        raise KeyError(f"unknown key '{key}'")

    def _get_base(self):
        """Get name of current workspace search path."""
        return self._config['current'].get('base', None) or 'cwd'

    def _get_basepath(self, base = None):
        """Get path of given or current workspace search path."""

        if not base: base = self._get_base()
        elif base not in self._config['default']['basepath']: return None
        mask = self._config['default']['basepath'][base]

        return self._get_path_expand(mask)

    def _get_default(self, key = None, *args, **kwargs):
        """Get default value."""

        import copy

        if not key: return copy.deepcopy(self._config['default'])
        elif key not in self._config['default']:
            raise ValueError("key '%s' is not valid." % key)
        retval = self._config['default'][key]
        parent = key
        while args:
            if not isinstance(args[0], str) \
                or not args[0] in retval:
                raise ValueError("""could not get default
                    value: '%s' does not contain key '%s'.""" %
                    (parent, args[0]))
            parent = args[0]
            retval = retval[args[0]]
            args = args[1:]

        if isinstance(retval, dict): return copy.deepcopy(retval)
        return retval

    def _get_list(self, key = None, *args, **kwargs):
        """Get list. """

        if key is None:
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
            if 'base' not in kwargs: kwargs['base'] = self._get_base()
            if 'workspace' not in kwargs:
                kwargs['workspace'] = self._get_workspace()
            if 'attribute' not in kwargs: kwargs['attribute'] = 'name'
            return self._get_objconfigs(key[:-1], *args, **kwargs)

        raise Warning(f"unknown key '{key}'")

    def _get_list_bases(self, workspace = None):
        """Get list of searchpaths containing given workspace name."""

        if workspace is None:
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
                workspaces[base] = self._get_list_workspaces(base = base)
            return workspaces
        elif base not in self._config['default']['basepath']:
            raise ValueError("unknown workspace base '%s'." % base)

        import glob
        import os
        from nemoa.common import ospath

        basepath = self._config['default']['basepath'][base]
        baseglob = self._get_path_expand((basepath, '*'))

        workspaces = []
        fname = self._config['default']['path']['inifile'][-1]
        for subdir in glob.iglob(baseglob):
            if not os.path.isdir(subdir): continue
            fpath = ospath.join(subdir, fname)
            if not os.path.isfile(fpath): continue
            workspaces.append(os.path.basename(subdir))

        return sorted(workspaces)

    def _get_shell(self, key = None, *args, **kwargs):
        """Get shell attribute."""

        if key == 'inkey': return self._get_shell_inkey()
        if key == 'buffmode': return self._get_shell_buffmode()

        raise KeyError(f"unknown key '{key}'")

    def _get_shell_inkey(self):
        """Get current key buffer."""
        inkey = self._buffer.get('inkey', None)
        return inkey.get() if inkey else None

    def _get_shell_buffmode(self):
        """Get current mode for keyboard buffering."""
        return self._config['current']['shell'].get('buffmode', 'line')

    def _get_mode(self):
        """Get current session mode."""
        return self._config['current'].get('mode', 'exec')

    def _get_objconfig(self, objtype, name = None,
        workspace = None, base = 'user', attribute = None):
        """Get configuration of given object as dictionary."""

        if objtype not in self._config['register']:
            raise Warning("""could not get configuration:
                object class '%s' is not supported.""" % objtype)
        if not isinstance(name, str):
            raise Warning("""could not get %s:
                name of object is not valid.""" % objtype)

        # (optional) load workspace of given object
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()
        if workspace is None:
            workspace = cur_workspace
            base = cur_base
        elif workspace != cur_workspace or base != cur_base:
            if not self._set_workspace(workspace, base = base):
                raise Warning("""could not get configuration:
                    workspace '%s' does not exist.""" % workspace)

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
            if workspace != cur_workspace or base != cur_base:
                self._set_workspace(cur_workspace, base = cur_base)

        if not config:
            raise Warning("""could not get configuration:
                %s with name '%s' is not found in %s workspace '%s'.
                """ % (objtype, name, base, workspace))

        if not attribute: return config
        elif not isinstance(attribute, str):
            raise Warning("""could not get configuration:
                attribute is not vlid.""")
        elif attribute not in config:
            raise Warning("""could not get configuration:
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

        if objtype and objtype not in self._config['register']: return False

        # create dictionary
        objlist = []
        for key in list(self._config['register'].keys()):
            if objtype and not key == objtype: continue
            for obj in self._config['register'][key].values():
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
            workspace = kwargs.pop('workspace')
            if workspace != self._get_workspace(): chdir = True
        if 'base' in kwargs:
            base = kwargs.pop('base')
            if base != self._get_base(): chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(workspace, base = base)

        # get path
        if key is None:
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
            raise Warning("""could not get path:
                path identifier '%s' is not valid.""" % key) or None

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base = current.get('base'))
            else: self._set_workspace(None)

        return path or None

    def _get_path_expand(self, *args, check: bool = False,
        create: bool = False):
        """Get expanded path.

        Args:
            path (string or tuple or list):
            check (bool):
            create (bool):

        Returns:
            String containing expanded path.

        """

        import os
        from nemoa.common import ospath

        path = ospath.join(args)

        # expand nemoa environment variables
        base = self._get_base()
        udict = {
            'workspace': self._get_workspace() or 'none',
            'base': self._get_base() or 'none',
            'basepath': ospath.join(self._config['default']['basepath'][base])
        }

        for key, val in self._config['default']['basepath'].items():
            udict[key] = ospath.join(val)
        for key, val in self._config['current']['path'].items():
            udict[key] = ospath.join(val)

        path = ospath.expand(path, udict = udict)

        # (optional) create directory
        if create: ospath.mkdir(path)

        # (optional) check path
        if check and not os.path.exists(path): return None

        return path

    def _get_workspace(self):
        """Get name of current workspace."""
        return self._config['current'].get('workspace', None)

    def log(self, *args, **kwargs):
        """Log message to file and console output."""

        if not args: return True

        import logging
        import traceback

        from nemoa.common import sysinfo, module

        mode = self._get_mode()
        obj = args[0]

        # test if args are given from an exception
        # in this case the arguments are (type, value, traceback)
        if isinstance(obj, type(Exception)):
            if issubclass(obj, Warning): key = 'warning'
            else: key = 'error'
            if mode == 'shell': clr = module.caller(-5)
            else: clr = module.caller(-4)
            msg = str(args[1]).capitalize()
            etype = obj.__name__

        # test if args are given as an info message
        # in this case the arguments are (msg)
        elif isinstance(obj, str) and len(args) == 1:
            key, msg = 'info', args[0].capitalize()
            clr = module.caller(-3)

        # test if args are given as a message of given type
        # in this case the arguments are (type, msg)
        elif isinstance(obj, str) and len(args) == 2:
            key, msg = args[0], args[1].capitalize()
            clr = module.caller(-3)

        else: return True

        # define colors (platform dependent workaround)
        osname = sysinfo.osname()

        # 2do define colors based on shell not on platform
        if osname.lower() == 'windows' and mode != 'shell':
            color = {'blue': '', 'yellow': '', 'red': '', 'green': '',
                'default': '' }
        else:
            color = {'blue': '\033[94m', 'yellow': '\033[93m',
                'red': '\033[91m', 'green': '\033[92m', 'default': '\033[0m' }

        # get loggers
        loggers = list(logging.Logger.manager.loggerDict.keys())
        tty_log = logging.getLogger(__name__ + '.tty') \
            if __name__ + '.tty' in loggers \
            else logging.getLogger(__name__ + '.null')
        file_log = logging.getLogger(__name__ + '.file') \
            if __name__ + '.file' in loggers \
            else logging.getLogger(__name__ + '.null')

        # format message
        while '  ' in msg: msg = msg.replace('  ', ' ')

        file_msg = clr + ' -> ' + msg.strip()

        # create logging records (depending on loglevels)
        if key == 'info':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if mode == 'shell': return True
            else: tty_log.info(msg)
            return None

        if key == 'note':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if mode == 'shell': tty_log.info(msg)
            else: tty_log.info(color['blue'] + msg + color['default'])
            return None

        if key == 'header':
            if mode == 'debug': file_log.info(file_msg)
            if mode == 'silent': return True
            if mode == 'shell': return True
            tty_log.info(color['green'] + msg + color['default'])
            return None

        if key == 'warning':
            if mode != 'silent': tty_log.warning(
                f"{color['red']}{etype}:{color['default']} {msg}")
            file_log.warning(file_msg)
            return None

        if key == 'error':
            tty_log.error(f"{color['red']}{etype}:{color['default']} {msg}")
                #clr + ': ' + color['yellow'] + msg + color['default'])
            file_log.error(file_msg)
            for line in traceback.format_stack():
                msg = line.strip().replace(
                    '\n', '-> ').replace('  ', ' ').strip()
                file_log.error(msg)
            return None

        if key == 'critical':
            tty_log.critical(color['yellow'] + msg + color['default'])
            file_log.critical(file_msg)
            return None

        if key == 'debuginfo':
            if mode == 'debug': file_log.error(file_msg)
            return None

        if key == 'console':
            tty_log.info(msg)
            return None

        if key == 'logfile':
            file_log.info(file_msg)
            return None

        raise ValueError(f"unknown logging type '{key}'")

    def _init_logging(self):
        """Initialize logging and enable exception handling."""

        import logging
        import os

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
        logfile = self._config['current']['path'].get('logfile', None)
        if logfile:
            logfile = self._get_path_expand(logfile)
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

    def _init_exception_handler(self):
        """Initialize exception handler."""

        import sys

        # pipe exceptions to nemoa.log
        def hook(*args, **kwargs):
            import nemoa
            return nemoa.log(*args, **kwargs)

        sys.__excepthook__ = hook

        return True

    def run(self, script = None, *args, **kwargs):
        """Run python script."""

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
            if workspace != self._get_workspace(): chdir = True
        if 'base' in kwargs:
            base = kwargs['base']
            del kwargs['base']
            if base != self._get_base(): chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(workspace, base = base)

        # get configuration and run script
        config = self.get('script', name = script, *args, **kwargs)
        if not isinstance(config, dict) or 'path' not in config:
            raise Warning("""could not run script '%s':
                invalid configuration.""" % script)
        elif not os.path.isfile(config['path']):
            raise Warning("""could not run script '%s':
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

        if key == 'shell': return self._set_shell(*args, **kwargs)
        if key == 'mode': return self._set_mode(*args, **kwargs)
        if key == 'workspace':
            return self._set_workspace(*args, **kwargs)

        raise KeyError(f"unknown key '{key}'")

    def _set_shell(self, key, *args, **kwargs):
        """Set current shell attributes."""

        if key == 'buffmode':
            return self._set_shell_buffmode(*args, **kwargs)

        raise KeyError(f"unknown key '{key}'")

    def _set_shell_buffmode(self, mode = 'line'):
        """Set current key buffer mode."""

        curmode = self._get_shell_buffmode()

        if mode == curmode: return True

        if curmode == 'line' and mode == 'key':
            if not self._buffer.get('inkey', None):
                import nemoa.common.console as console
                self._buffer['inkey'] = console.Getch()
            self._buffer['inkey'].start()
            return True

        if curmode == 'key' and mode == 'line':
            self._buffer['inkey'].stop()
            del self._buffer['inkey']
            return True
        return False

    def _set_mode(self, mode = None, *args, **kwargs):
        """Set session mode."""

        if mode not in ['debug', 'exec', 'shell', 'silent']: return None

        self._config['current']['mode'] = mode

        return True

    def _set_workspace(self, workspace, base = None,
        update = False, scandir = True, logging = True):
        """Set workspace."""

        # reset workspace if given workspace is None
        if workspace is None:
            return self._set_workspace_reset()

        # return if workspace did not change
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()
        if workspace == cur_workspace \
            and base in [None, cur_base]: return True

        # detect base if base is not given
        if base is None:
            bases = self._get_list_bases(workspace)
            if not bases:
                raise Warning(
                    "could not open workspace '%s': "
                    "workspace could not be found "
                    "in any searchpath." % workspace) or None
            if len(bases) > 1:
                raise Warning(
                    "could not open workspace '%s': "
                    "workspace been found in different searchpaths: "
                    "%s." % (workspace, ', '.join(bases))) or None
            base = bases[0]

        # test if base and workspace are valid
        if workspace not in self._get_list_workspaces(base = base):
            basepath = self._get_path_expand(
                self._config['default']['basepath'][base])
            raise Warning(
                "could not open workspace '%s': "
                "workspace could not be found in searchpath "
                "'%s'." % (workspace, basepath)) or None

        # set current workspace name and workspace base name
        self._config['current']['workspace'] = workspace
        self._config['current']['base'] = base

        # update paths from default path structure
        for key, val in list(self._config['default']['path'].items()):
            self._config['current']['path'][key] = \
                self._get_path_expand(val)

        retval = True

        # (optional) use logfile of new workspace
        if retval and logging:
            retval &= self._init_logging()

        # open workspace
        if retval:
            instance = nemoa.workspace.open(workspace, base = base)
            retval &= bool(instance)
            if instance: self._config['workspace'] = instance

        # (optional) scan workspace folder for objects / files
        if retval and scandir:
            retval &= self._set_workspace_scandir()

        return retval

    def _set_workspace_reset(self):
        """ """

        import copy

        self._config['current'] = copy.deepcopy(self._default['current'])
        self._config['workspace'] = None

        return self._init_logging()

    def _set_workspace_scandir(self, *args, **kwargs):
        """Scan workspace for files."""

        import glob
        from nemoa.common import ospath

        # change current base and workspace (if necessary)
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()

        if len(args) > 0: workspace = args[0]
        else: workspace = cur_workspace
        if 'base' in kwargs: base = kwargs.pop('base')
        else: base = cur_base

        if (base, workspace) != (cur_base, cur_workspace):
            chdir = self._set_workspace(workspace, base = base)
        else:
            chdir = False

        # scan workspace for objects
        for objtype in list(self._config['register'].keys()):
            dirmask = self._config['current']['path'][objtype + 's']
            filemask = self._get_path_expand(dirmask, '*.*')
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
            objregister = self._config['register'][objtype]
            for filepath in glob.iglob(filemask):
                filetype = ospath.fileext(filepath)
                if filetype not in filetypes: continue
                basename = ospath.basename(filepath)
                filespace = self._get_workspace()
                filebase = self._get_base()
                fullname = '%s.%s.%s' % (filebase, filespace, basename)

                if fullname in objregister: continue

                # register object configuration
                objregister[fullname] = {
                    'base': filebase,
                    'fullname': fullname,
                    'name': basename,
                    'path': filepath,
                    'type': objtype,
                    'workspace': filespace }

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base = current.get('base'))
            else:
                self._set_workspace(None)

        return True

    def open(self, key = None, *args, **kwargs):
        """Open object in current session."""

        if not key: return None
        if not args:
            return self._set_workspace(key)
        elif len(args) == 1:
            if key == 'workspace':
                return self._set_workspace(args[0])
            if key == 'model':
                return nemoa.model.open(args[0], **kwargs)
            if key == 'dataset':
                return nemoa.dataset.open(args[0], **kwargs)
            if key == 'network':
                return nemoa.network.open(args[0], **kwargs)
            if key == 'system':
                return nemoa.system.open(args[0], **kwargs)

        return None
