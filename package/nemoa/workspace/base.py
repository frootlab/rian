# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os
import imp
import glob

class Workspace:
    """Nemoa workspace."""

    _workspace = None

    def __init__(self, workspace = None):
        """initialize shared configuration."""
        #nemoa.workspace._init()
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
        else: names = [item[2] for item in list]
        return names

    def execute(self, name = None, **kwargs):
        """execute nemoa script."""
        script_name = name \
            if '.' in name else '%s.%s' % (self._workspace, name)
        config = nemoa.workspace.find(
            type = 'script', config = script_name, **kwargs)

        if not config and not '.' in name:
            script_name = 'base.' + name
            config = nemoa.workspace.find(
                type = 'script', config = script_name, **kwargs)
        if not config: return False
        if not os.path.isfile(config['path']):
            return nemoa.log('error', """could not run script '%s':
            file '%s' not found!""" % (script_name, config['path']))

        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

class Config:
    """nemoa workspace module internal configuration object."""

    _default = {
        'baseconf': 'nemoa.ini', # base configuration file
        'basepath': { # paths for shared ressources and workspaces
            'user': '~/.nemoa/',
            'common': '/etc/nemoa/common/' },
        'path': {}, # paths for logfile, cachefile, etc.
        'workspace': None, # current workspace
        'workspace_path': { # paths for datasets, networks, models, etc.
            'datasets': '%workspace%/datasets/',
            'networks': '%workspace%/networks/',
            'systems': '%workspace%/systems/',
            'models': '%workspace%/models/',
            'scripts': '%workspace%/scripts/',
            'cache': '%workspace%/cache/',
            'logfile': '%workspace%/nemoa.log' },
        'workspace_base': None,
        'store': { # information storage for known objects
            'dataset': {},
            'network': {},
            'system': {},
            'model': {},
            'script': {} }}
    _config = None

    def __init__(self, shared = True):
        """ """

        self._config = self._default.copy()

        # update basepaths from base configuration
        if os.path.exists(self._config['baseconf']):
            ini_dict = nemoa.common.ini_load(self._config['baseconf'], {
                'folders': {
                    'user': 'str',
                    'cache': 'str',
                    'common': 'str' },
                'files': {
                    'logfile': 'str' }})

            if 'folders' in ini_dict:
                for key, val in ini_dict['folders'].iteritems():
                    path = self._expand_path(val)
                    if path: self._config['basepath'][key] = path

            if 'files' in ini_dict:
                for key, val in ini_dict['files'].iteritems():
                    path = self._expand_path(val)
                    if path: self._config['path'][key] = path

        # import shared resources
        if shared:
            for workspace in self._list_shared_workspaces():
                self._set_workspace_scan_files(workspace, 'common')

    def workspace(self):
        """Return name of current workspace."""

        return self._config['workspace']

    def name(self):
        """Return name of current workspace."""

        return self._config['workspace']

    def path(self, key = None):
        """Return path."""

        if isinstance(key, basestring) \
            and key in self._config['path'].keys():
            if isinstance(self._config['path'][key], dict):
                return self._config['path'][key].copy()
            return self._config['path'][key]

        return self._config['path'].copy()

    def load(self, workspace):
        """Import configuration files from workspace."""

        self._set_workspace(workspace, base = 'user')
        nemoa.log('init', logfile = self._config['path']['logfile'])
        self._set_workspace_scan_files()

        return True

    def list(self, type = None, namespace = None):
        """List known object configurations."""

        if type == 'workspace':
            return sorted(self._list_user_workspaces())

        if type and not type in self._config['store']: return False

        objlist = []
        for key in self._config['store'].keys():
            if type and not key == type: continue
            for name, obj in self._config['store'][key].items():
                if namespace and not namespace == obj['workspace']:
                    continue
                objlist.append((0, obj['type'], obj['name']))
        return sorted(objlist, key = lambda col: col[2])

    def _list_user_workspaces(self):
        """Return list of private workspaces."""
        user_dir = self._expand_path(self._config['basepath']['user'])
        return [os.path.basename(w) for w in glob.iglob(user_dir + '*')
            if os.path.isdir(w)]

    def _list_shared_workspaces(self):
        """Return list of shared resources."""
        shared = self._expand_path(self._config['basepath']['common'])
        return [os.path.basename(w) for w in glob.iglob(shared + '*')
            if os.path.isdir(w)]

    def _get_obj_id_by_name(self, type, name):
        """Return id of object as integer
        calculated as hash from type and name"""
        return nemoa.common.str_to_hash(str(type) + chr(10) + str(name))

    def get(self, type = None, name = None, merge = ['params'],
        params = None):
        """Return configuration as dictionary for given object."""

        if not type in self._config['store'].keys():
            return nemoa.log('warning', """could not get configuration:
                object class '%s' is not supported.""" % type)
        if not isinstance(name, basestring):
            return nemoa.log('warning', """could not get configuration:
                name of object is not known.""")

        search = [name, '%s.%s' % (self._get_workspace(), name),
            name + '.default', 'base.' + name]

        found = False
        for fullname in search:
            if fullname in self._config['store'][type].keys():
                found = True
                break

        if not found:
            return nemoa.log('warning', """could not get configuration:
                name of object is not known.""")

        cfg = self._config['store'][type][fullname].copy()

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

        return cfg

    def _get_workspace(self):
        return self._config['workspace']

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

        replace = {
            'workspace': self._config['workspace'],
            'base': self._config['workspace_base'] }

        update = True
        while update:
            update = False

            # expand path vars
            for key in self._config['path'].keys():
                if '%' + key + '%' in path:
                    path = path.replace('%' + key + '%',
                        self._config['path'][key])
                    path = path.replace('//', '/')
                    update = True

            # expand basepath variables
            for key in self._config['basepath'].keys():
                if '%' + key + '%' in path:
                    path = path.replace('%' + key + '%',
                        self._config['basepath'][key])
                    path = path.replace('//', '/')
                    update = True

            # expand other variables
            for key in replace:
                if '%' + key + '%' in path:
                    path = path.replace('%' + key + '%', replace[key])
                    path = path.replace('//', '/')
                    update = True

        return path

    def _set_workspace(self, workspace, base = 'user', refresh = False):

        if workspace == None: return True
        if workspace == self._config['workspace'] and not refresh:
            return True
        if base == 'user':
            if not workspace in self._list_user_workspaces():
                return nemoa.log('warning', """could not open workspace
                    '%s': folder could not be found in '%s'."""
                    % (workspace, self._basepath['user']))
        elif base == 'common':
            if not workspace in self._list_shared_workspaces():
                return nemoa.log('warning', """could not open workspace
                    '%s': folder could not be found in '%s'."""
                    % (workspace, self._basepath['common']))
        else:
            return nemoa.log('error', """could not open workspace
                '%s': base of workspace is not valid.""" % (workspace))

        # update workspace name, base and paths
        self._config['workspace'] = workspace
        self._config['workspace_base'] = base
        for key in self._config['workspace_path']:
            path = '%' + base + '%/' \
                + self._config['workspace_path'][key]
            self._config['path'][key] \
                = self._expand_path(path, create = False)

        return True

    def _set_workspace_scan_files(self, workspace = None, base = None):
        """Scan workspace for files."""

        # change current workspace
        if workspace:
            cur_workspace = self._config['workspace']
            cur_workspace_base = self._config['workspace_base']
            if not self._set_workspace(workspace, base = base):
                return False
        else:
            cur_workspace = None
            cur_workspace_base = None
            workspace = self._config['workspace']

        for type in self._config['store'].keys():
            files = self._config['path'][type + 's'] + '*.*'
            if type == 'dataset':
                filetypes = nemoa.dataset.imports.filetypes()
            elif type == 'network':
                filetypes = nemoa.network.imports.filetypes()
            elif type == 'system':
                filetypes = nemoa.system.imports.filetypes()
            elif type == 'model':
                filetypes = nemoa.model.imports.filetypes()
            elif type == 'script':
                filetypes = ['py']

            # scan for files
            for path in glob.iglob(self._expand_path(files)):
                filetype = nemoa.common.get_file_extension(path)
                if not filetype in filetypes: continue
                name = nemoa.common.get_file_basename(path)
                workspace = self._config['workspace']
                fullname = '%s.%s' % (workspace, name)
                if fullname in self._config['store'][type]: continue

                # add configuration to object tree
                self._config['store'][type][fullname] = {
                    'name': fullname,
                    'type': type,
                    'path': path,
                    'workspace': workspace }

        # change current workspace and update paths
        if workspace and not workspace == cur_workspace:
            self._set_workspace(cur_workspace,
                base = cur_workspace_base)

        return True
