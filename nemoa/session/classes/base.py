# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import copy
import glob
import imp
import logging
import os
import traceback
from flab.base import env, stack
import nemoa
from nemoa import workspace
from nemoa.core import tty
from flab.io import ini

class Session:
    """Session Manager."""

    _buffer: dict = {}
    _config = None
    _struct: dict = {
        'folders': {
            'user': str,
            'cache': str,
            'site': str},
        'files': {
            'logfile': str}}
    _default: dict = {
        'current': {
            'workspace': None,
            'base': None,
            'mode': 'exec',
            'path': {},
            'shell': {
                'buffmode': 'line'}},
        'default': {
            'basepath': {
                'cwd': '%user_cwd%',
                'user': ('%user_data_dir%', 'workspaces'),
                'site': ('%site_data_dir%', 'workspaces')},
            'filetype': {
                'dataset': 'csv',
                'network': 'graphml',
                'system': 'npz',
                'model': 'npz',
                'script': 'py'},
            'path': {
                'baseconf': ('%user_config_dir%', 'nemoa.ini'),
                'datasets': ('%basepath%', '%workspace%', 'datasets'),
                'networks': ('%basepath%', '%workspace%', 'networks'),
                'systems': ('%basepath%', '%workspace%', 'systems'),
                'models': ('%basepath%', '%workspace%', 'models'),
                'scripts': ('%basepath%', '%workspace%', 'scripts'),
                'cache': ('%basepath%', '%workspace%', 'cache'),
                'ini':
                    ('%basepath%', '%workspace%', 'workspace.ini'),
                'logfile':
                    ('%basepath%', '%workspace%', 'nemoa_old.log')}},
        'register': {
            'dataset': {},
            'model': {},
            'network': {},
            'script': {},
            'system': {}}}

    def __init__(self, site: bool = True, **kwds):
        """ """
        self._config = {**self._default, **kwds}

        # reset workspace to default values
        self._set_workspace_reset()

        # update basepaths from user configuration
        configfile = self._config['default']['path']['baseconf']
        configfile = self._get_path_expand(configfile)

        if os.path.exists(configfile):
            ini_dict = ini.load(configfile, scheme=self._struct)

            if 'folders' in ini_dict:
                for key, val in ini_dict['folders'].items():
                    path = self._get_path_expand(val)
                    if path:
                        self._config['default']['basepath'][key] = path

            if 'files' in ini_dict:
                for key, val in ini_dict['files'].items():
                    path = self._get_path_expand(val)
                    if path: self._config['current']['path'][key] = path

    def create(self, key: str, *args, **kwds):
        """Open object in current session."""
        if key == 'model':
            from nemoa import model
            return model.create(*args, **kwds)
        if key == 'network':
            from nemoa import network
            return network.create(*args, **kwds)
        if key == 'dataset':
            from nemoa import dataset
            return dataset.create(*args, **kwds)
        if key == 'system':
            from nemoa import system
            return system.create(*args, **kwds)
        return None

    def get(self, key='workspace', *args, **kwds):
        """Get meta information and content."""

        if key == 'about':
            return self._get_about(*args, **kwds)
        if key == 'base':
            return self._get_base()
        if key == 'default':
            return self._get_default(*args, **kwds)
        if key == 'list':
            return self._get_list(*args, **kwds)
        if key == 'mode':
            return self._get_mode(*args, **kwds)
        if key == 'path':
            return self._get_path(*args, **kwds)
        if key == 'shell':
            return self._get_shell(*args, **kwds)
        if key == 'workspace':
            return self._get_workspace()

        if key in self._config['register']:
            return self._get_objconfig(key, *args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def path(self, *args, **kwds):
        """Get path of given object."""

        return self._get_path(*args, **kwds)

    def _get_about(self, key='about', *args, **kwds):
        """Get nemoa meta information."""

        if key == 'about':
            return nemoa.__description__
        if key == 'version':
            return nemoa.__version__
        if key == 'status':
            return nemoa.__status__
        if key == 'description':
            return nemoa.__doc__.strip()
        if key == 'url':
            return nemoa.__url__
        if key == 'license':
            return nemoa.__license__
        if key == 'copyright':
            return nemoa.__copyright__
        if key == 'author':
            return nemoa.__author__
        if key == 'email':
            return nemoa.__email__
        if key == 'maintainer':
            return nemoa.__maintainer__
        if key == 'credits':
            return nemoa.__credits__

        raise KeyError(f"unknown key '{key}'")

    def _get_base(self):
        """Get name of current workspace search path."""
        return self._config['current'].get('base', None) or 'cwd'

    def _get_basepath(self, base=None):
        """Get path of given or current workspace search path."""

        if not base:
            base = self._get_base()
        elif base not in self._config['default']['basepath']:
            return None
        mask = self._config['default']['basepath'][base]

        return self._get_path_expand(mask)

    def _get_default(self, key=None, *args, **kwds):
        """Get default value."""
        if not key:
            return copy.deepcopy(self._config['default'])
        elif key not in self._config['default']:
            raise KeyError(f"key '{key}' is not valid")
        retval = self._config['default'][key]
        parent = key
        while args:
            if not isinstance(args[0], str) or not args[0] in retval:
                return None
            parent = args[0]
            retval = retval[args[0]]
            args = args[1:]

        return copy.deepcopy(retval)

    def _get_list(self, key=None, *args, **kwds):
        """Get list. """

        if key is None:
            retval = {}
            ws = self._get_workspace()
            base = self._get_base()
            for key in self._config['register']:
                keys = key + 's'
                objlist = self._get_list(keys, ws=ws, base=base)
                retval[keys] = objlist
            return retval
        if key == 'bases':
            return self._get_list_bases(*args, **kwds)
        if key == 'workspaces':
            return self._get_list_workspaces(*args, **kwds)
        if key in [rkey + 's' for rkey in self._config['register']]:
            if 'base' not in kwds:
                kwds['base'] = self._get_base()
            if 'ws' not in kwds:
                kwds['ws'] = self._get_workspace()
            if 'attribute' not in kwds:
                kwds['attribute'] = 'name'
            return self._get_objconfigs(key[:-1], *args, **kwds)

        raise Warning(f"unknown key '{key}'")

    def _get_list_bases(self, ws=None):
        """Get list of searchpaths containing given workspace name."""

        if ws is None:
            return sorted(self._config['default']['basepath'].keys())
        bases = []
        for base in self._config['default']['basepath']:
            if ws in self._get_list_workspaces(base=base):
                bases.append(base)

        return sorted(bases)

    def _get_list_workspaces(self, base=None):
        """Get list of workspaces in given searchpath."""

        if not base:
            wsdict = {}
            for base in self._config['default']['basepath']:
                wsdict[base] = self._get_list_workspaces(base=base)
            return wsdict
        if base not in self._config['default']['basepath']:
            raise ValueError("unknown workspace base '%s'" % base)

        basepath = self._config['default']['basepath'][base]
        baseglob = self._get_path_expand((basepath, '*'))

        wslist = []
        fname = self._config['default']['path']['ini'][-1]
        for subdir in glob.iglob(baseglob):
            if not os.path.isdir(subdir):
                continue
            fpath = str(env.join_path(subdir, fname))
            if not os.path.isfile(fpath):
                continue
            wslist.append(os.path.basename(subdir))

        return sorted(wslist)

    def _get_shell(self, key=None, *args, **kwds):
        """Get shell attribute."""

        if key == 'inkey':
            return self._get_shell_inkey()
        if key == 'buffmode':
            return self._get_shell_buffmode()

        raise KeyError(f"unknown key '{key}'")

    def _get_shell_inkey(self):
        """Get current key buffer."""
        inkey = self._buffer.get('inkey', None)
        return inkey.getch() if inkey else None

    def _get_shell_buffmode(self):
        """Get current mode for keyboard buffering."""
        return self._config['current']['shell'].get('buffmode', 'line')

    def _get_mode(self):
        """Get current session mode."""
        return self._config['current'].get('mode', 'exec')

    def _get_objconfig(
            self, objtype, name=None, ws=None, base='user', attribute=None):
        """Get configuration of given object as dictionary."""

        if objtype not in self._config['register']:
            raise Warning("""could not get configuration:
                object class '%s' is not supported.""" % objtype)
        if not isinstance(name, str):
            raise Warning("""could not get %s:
                name of object is not valid.""" % objtype)

        # (optional) load workspace of given object
        cur_ws = self._get_workspace()
        cur_base = self._get_base()
        if ws is None:
            ws = cur_ws
            base = cur_base
        elif ws != cur_ws or base != cur_base:
            if not self._set_workspace(ws, base=base):
                raise Warning(
                    "could not get configuration: "
                    f"workspace '{ws}' does not exist.")

        # find object configuration in workspace
        search = [name, '%s.%s.%s' % (base, ws, name),
            name + '.default', 'base.' + name]
        config = None
        for fullname in search:
            if fullname in self._config['register'][objtype]:
                config = self._config['register'][objtype][fullname]
                break

        # (optional) load current workspace
        if cur_ws:
            if ws != cur_ws or base != cur_base:
                self._set_workspace(cur_ws, base=cur_base)

        if not config:
            raise Warning(
                f"{objtype} with name '{name}' is not "
                f"found in {base} workspace '{ws}'")

        if not attribute:
            return config
        if not isinstance(attribute, str):
            raise Warning("attribute is not valid")
        if attribute not in config:
            raise Warning(f"attribute '{attribute}' is not valid")

        return config[attribute]

    def _get_objconfigs(
            self, objtype=None, ws=None, base=None, attribute='name'):
        """Get registered object configurations of given type."""

        if not objtype:
            objs = {}
            for obj in self._config['register']:
                objs[obj] = self._get_objconfigs(objtype=obj, ws=ws, base=base)
            return objs

        if objtype and objtype not in self._config['register']:
            return False

        # create dictionary
        objlist = []
        for key in list(self._config['register'].keys()):
            if objtype and not key == objtype:
                continue
            for obj in self._config['register'][key].values():
                if base and not base == obj['base']:
                    continue
                if ws and not ws == obj['workspace']:
                    continue
                if attribute and not attribute in obj:
                    continue
                if attribute:
                    objlist.append(obj[attribute])
                else:
                    objlist.append(obj)

        if attribute:
            return sorted(objlist)
        return sorted(objlist, key=lambda obj: obj['name'])

    def _get_path(self, key=None, *args, **kwds):
        """Get path of given object or object type."""

        if key == 'basepath':
            return self._get_basepath(*args, **kwds)

        # change current workspace if necessary
        chdir = False
        ws = self._get_workspace()
        base = None
        if 'workspace' in kwds:
            ws = kwds.pop('workspace')
            if ws != self._get_workspace():
                chdir = True
        if 'base' in kwds:
            base = kwds.pop('base')
            if base != self._get_base():
                chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(ws, base=base)

        # get path
        if key is None:
            path = copy.deepcopy(self._config['current']['path'])
        elif key == 'expand':
            if 'workspace' in kwds:
                del kwds['workspace']
            if 'base' in kwds:
                del kwds['base']
            path = self._get_path_expand(*args, **kwds)
        elif key in self._config['current']['path']:
            path = self._config['current']['path'][key]
        elif key in self._config['register']:
            name = kwds.get('name', None) or (args[0] if args else None)
            path = self._get_objconfig(objtype=key, name=name,
                attribute='path')
        else: path = None

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base=current.get('base'))
            else:
                self._set_workspace(None)

        return path or None

    def _get_path_expand(
            self, *args, check: bool = False, create: bool = False):
        """Get expanded path.

        Args:
            path (string or tuple or list):
            check (bool):
            create (bool):

        Returns:
            String containing expanded path.

        """
        path = str(env.join_path(args))

        # expand nemoa environment variables
        base = self._get_base()
        udict = {
            'workspace': self._get_workspace() or 'none',
            'base': self._get_base() or 'none',
            'basepath': str(
                env.join_path(self._config['default']['basepath'][base]))}

        for key, val in self._config['default']['basepath'].items():
            udict[key] = str(env.join_path(val))
        for key, val in self._config['current']['path'].items():
            udict[key] = str(env.join_path(val))

        path = str(env.expand(path, udict=udict))

        # (optional) create directory
        if create:
            env.mkdir(path)

        # (optional) check path
        if check and not os.path.exists(path):
            return None

        return path

    def _get_workspace(self):
        """Get name of current workspace."""
        return self._config['current'].get('workspace', None)

    def log(self, *args, **kwds):
        """Log message to file and console output."""

        if not args:
            return True

        mode = self._get_mode()
        obj = args[0]

        # test if args are given from an exception
        # in this case the arguments are (type, value, traceback)
        if isinstance(obj, type(Exception)):
            etype, value, tb = args[0], args[1], args[2]
            if issubclass(etype, Warning):
                key = 'warning'
            else:
                key = 'error'
            if mode == 'shell':
                clr = stack.get_caller_name(-5)
            else:
                clr = stack.get_caller_name(-4)
            if mode == 'debug':
                msg = ('').join(traceback.format_exception(etype, value, tb))
            else:
                msg = str(args[1]).capitalize()

        # test if args are given as an info message
        # in this case the arguments are (msg)
        elif isinstance(obj, str) and len(args) == 1:
            key, msg = 'info', args[0].capitalize()
            clr = stack.get_caller_name(-3)

        # test if args are given as a message of given type
        # in this case the arguments are (type, msg)
        elif isinstance(obj, str) and len(args) == 2:
            key, msg = args[0], args[1].capitalize()
            clr = stack.get_caller_name(-3)

        else: return True

        # define colors (platform dependent workaround)
        osname = env.get_osname()

        # 2do define colors based on shell not on platform
        if osname.lower() == 'windows' and mode != 'shell':
            color = {'blue': '', 'yellow': '', 'red': '', 'green': '',
                'default': ''}
        else:
            color = {'blue': '\033[94m', 'yellow': '\033[93m',
                'red': '\033[91m', 'green': '\033[92m', 'default': '\033[0m'}

        # get loggers
        loggers = list(logging.Logger.manager.loggerDict.keys())
        tty_log = logging.getLogger(__name__ + '.tty') \
            if __name__ + '.tty' in loggers \
            else logging.getLogger(__name__ + '.null')
        file_log = logging.getLogger(__name__ + '.file') \
            if __name__ + '.file' in loggers \
            else logging.getLogger(__name__ + '.null')

        # format message
        while '  ' in msg:
            msg = msg.replace('  ', ' ')

        file_msg = clr + ' -> ' + msg.strip()

        # create logging records (depending on loglevels)
        if key == 'info':
            if mode == 'debug':
                file_log.info(file_msg)
            if mode == 'silent':
                return True
            if mode == 'shell':
                return True
            else: tty_log.info(msg)
            return None

        if key == 'note':
            if mode == 'debug':
                file_log.info(file_msg)
            if mode == 'silent':
                return True
            if mode == 'shell':
                tty_log.info(msg)
            else: tty_log.info(color['blue'] + msg + color['default'])
            return None

        if key == 'header':
            if mode == 'debug':
                file_log.info(file_msg)
            if mode == 'silent':
                return True
            if mode == 'shell':
                return True
            tty_log.info(color['green'] + msg + color['default'])
            return None

        if key == 'warning':
            ename = etype.__name__
            if mode != 'silent':
                tty_log.warning(
                    f"{color['red']}{ename}:{color['default']} {msg}")
            file_log.warning(file_msg)
            return None

        if key == 'error':
            ename = etype.__name__
            tty_log.error(f"{color['red']}{ename}:{color['default']} {msg}")
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
            if mode == 'debug':
                file_log.error(file_msg)
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

        # initialize null logger, remove all previous handlers
        # and set up null handler
        logger_null = logging.getLogger(__name__ + '.null')
        for h in logger_null.handlers:
            logger_null.removeHandler(h)
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
            logging.Formatter(fmt='%(message)s'))
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
            for h in logger_file.handlers:
                logger_file.removeHandler(h)
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s %(levelname)s %(message)s',
                datefmt='%m/%d/%Y %H:%M:%S'))
            logger_file.addHandler(file_handler)

        return True

    def run(self, script=None, *args, **kwds):
        """Run python script."""
        retval = True

        # change current workspace if necessary
        chdir = False
        ws = self._get_workspace()
        base = None
        if 'workspace' in kwds:
            ws = kwds['workspace']
            del kwds['workspace']
            if ws != self._get_workspace():
                chdir = True
        if 'base' in kwds:
            base = kwds['base']
            del kwds['base']
            if base != self._get_base():
                chdir = True
        if chdir:
            current = self._config.get('workspace', None)
            self._set_workspace(ws, base=base)

        # get configuration and run script
        config = self.get('script', name=script, *args, **kwds)
        if not isinstance(config, dict) or 'path' not in config:
            raise Warning(
                f"could not run script '{script}':"
                "invalid configuration.")
        elif not os.path.isfile(config['path']):
            raise Warning(
                f"could not run script '{script}'"
                "file '{config['path']}' not found.")
        else:
            minst = imp.load_source('script', config['path'])
            minst.main(self._config['workspace'], *args, **kwds)

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(
                    current.get('name'), base=current.get('base'))
            else:
                self._set_workspace(None)

        return retval

    def set(self, key, *args, **kwds):
        """Set configuration parameters and env vars."""

        if key == 'shell':
            return self._set_shell(*args, **kwds)
        if key == 'mode':
            return self._set_mode(*args, **kwds)
        if key == 'workspace':
            return self._set_workspace(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_shell(self, key, *args, **kwds):
        """Set current shell attributes."""

        if key == 'buffmode':
            return self._set_shell_buffmode(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_shell_buffmode(self, mode='line'):
        """Set current key buffer mode."""
        terminal = tty.get_instance() # type: ignore

        if mode == 'key':
            terminal.set_mode('key')
            terminal.start_getch()
            return True

        if mode == 'line':
            terminal.stop_getch()
            terminal.set_mode('line')
            return True

        return False

    def _set_mode(self, mode=None, *args, **kwds):
        """Set session mode."""

        if mode not in ['debug', 'exec', 'shell', 'silent']:
            return None

        self._config['current']['mode'] = mode

        return True

    def _set_workspace(
            self, ws, base=None, update=False, scandir=True, logging=True):
        """Set workspace."""

        # reset workspace if given workspace is None
        if ws is None:
            return self._set_workspace_reset()

        # return if workspace did not change
        cur_ws = self._get_workspace()
        cur_base = self._get_base()
        if ws == cur_ws and base in [None, cur_base]:
            return True

        # detect base if base is not given
        if base is None:
            bases = self._get_list_bases(ws)
            if not bases:
                raise Warning(
                    f"could not open workspace '{workspace}': "
                    "workspace could not be found "
                    "in any searchpath.")
            if len(bases) > 1:
                raise Warning(
                    f"could not open workspace '{workspace}': "
                    "workspace has been found "
                    f"in different searchpaths: {', '.join(bases)}")
            base = bases[0]

        # test if base and workspace are valid
        if ws not in self._get_list_workspaces(base=base):
            basepath = self._get_path_expand(
                self._config['default']['basepath'][base])
            raise Warning(
                f"could not open workspace '{workspace}': "
                f"workspace could not be found in searchpath '{basepath}'")

        # set current workspace name and workspace base name
        self._config['current']['workspace'] = ws
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
            instance = workspace.open(ws, base=base)
            retval &= bool(instance)
            if instance:
                self._config['workspace'] = instance

        # (optional) scan workspace folder for objects / files
        if retval and scandir:
            retval &= self._set_workspace_scandir()

        return retval

    def _set_workspace_reset(self):
        """ """

        c = self._config['current']
        d = self._default['current']
        c['workspace'] = d['workspace']
        c['base'] = d['base']
        c['path'] = d['path'].copy()

        self._config['workspace'] = None

        return self._init_logging()

    def _set_workspace_scandir(self, *args, **kwds):
        """Scan workspace for files."""

        # change current base and workspace (if necessary)
        cur_ws = self._get_workspace()
        cur_base = self._get_base()

        if args:
            ws = args[0]
        else:
            ws = cur_ws
        if 'base' in kwds:
            base = kwds.pop('base')
        else:
            base = cur_base

        if (base, ws) != (cur_base, cur_ws):
            current = self._config.get('workspace', None)
            chdir = self._set_workspace(ws, base=base)
        else:
            chdir = False

        # scan workspace for objects
        for objtype in list(self._config['register'].keys()):
            dirmask = self._config['current']['path'][objtype + 's']
            filemask = self._get_path_expand(dirmask, '*.*')
            if objtype == 'dataset':
                from nemoa.dataset import imports
                filetypes = imports.filetypes()
            elif objtype == 'network':
                from nemoa.network import imports
                filetypes = imports.filetypes()
            elif objtype == 'system':
                from nemoa.system import imports
                filetypes = imports.filetypes()
            elif objtype == 'model':
                from nemoa.model import imports
                filetypes = imports.filetypes()
            elif objtype == 'script':
                filetypes = ['py']

            # scan for files
            objregister = self._config['register'][objtype]
            for filepath in glob.iglob(filemask):
                filetype = env.fileext(filepath)
                if filetype not in filetypes:
                    continue
                basename = env.basename(filepath)
                filespace = self._get_workspace()
                filebase = self._get_base()
                fullname = '%s.%s.%s' % (filebase, filespace, basename)

                if fullname in objregister:
                    continue

                # register object configuration
                objregister[fullname] = {
                    'base': filebase,
                    'fullname': fullname,
                    'name': basename,
                    'path': filepath,
                    'type': objtype,
                    'workspace': filespace}

        # change to previous workspace if necessary
        if chdir:
            if current:
                self._set_workspace(current.get('name'),
                    base=current.get('base'))
            else:
                self._set_workspace(None)

        return True

    def open(self, key=None, *args, **kwds):
        """Open object in current session."""

        if not key:
            return None
        if not args:
            return self._set_workspace(key)
        if len(args) == 1:
            if key == 'workspace':
                return self._set_workspace(args[0])
            if key == 'model':
                return nemoa.model.open(args[0], **kwds)
            if key == 'dataset':
                return nemoa.dataset.open(args[0], **kwds)
            if key == 'network':
                return nemoa.network.open(args[0], **kwds)
            if key == 'system':
                return nemoa.system.open(args[0], **kwds)

        return None
