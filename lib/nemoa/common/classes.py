# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class ClassesBaseClass:
    """Base Class for content specific classes.

    Content specific classes like Dataset, Network, System or Model
    share common properties like metadata about author and license.
    This Base Class is intended to provide a common interface and
    implementation of those common properties.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute.
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute.
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute.
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute.
        path (str): Path to a file containing or referencing the
            resource.
            Hint: Read- & writeable wrapping attribute.
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute.
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute.

    """

    _attr_meta = {
        'fullname': 'r', 'type': 'r', 'about': 'rw',
        'name': 'rw', 'branch': 'rw', 'version': 'rw',
        'author': 'rw', 'email': 'rw', 'license': 'rw',
        'path': 'rw'}

    def __init__(self, *args, **kwargs):
        """Import object configuration and content from dictionary."""
        self._set_copy(**kwargs)

    def __getattr__(self, key):
        """Attribute wrapper to getter methods."""

        if key in self._attr_meta:
            if 'r' in self._attr_meta[key]: return self._get_meta(key)
            return nemoa.log('warning',
                "attribute '%s' is not readable." % (key))
        if key in self._attr:
            if 'r' in self._attr[key]: return self.get(key)
            return nemoa.log('warning',
                "attribute '%s' is not readable." % (key))

        raise AttributeError("%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def __setattr__(self, key, val):
        """Attribute wrapper to setter methods."""

        if key in self._attr_meta:
            if 'w' in self._attr_meta[key]:
                return self._set_meta(key, val)
            return nemoa.log('warning',
                "attribute '%s' is not writeable." % (key))
        if key in self._attr:
            if 'w' in self._attr[key]: return self.set(key, val)
            return nemoa.log('warning',
                "attribute '%s' is not writeable." % (key))

        self.__dict__[key] = val

    def _get_meta(self, key):
        """Get meta information like 'author' or 'version'."""

        if key == 'about':    return self._get_about()
        if key == 'author':   return self._get_author()
        if key == 'branch':   return self._get_branch()
        if key == 'email':    return self._get_email()
        if key == 'fullname': return self._get_fullname()
        if key == 'license':  return self._get_license()
        if key == 'name':     return self._get_name()
        if key == 'path':     return self._get_path()
        if key == 'type':     return self._get_type()
        if key == 'version':  return self._get_version()

        return nemoa.log('warning', "%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def _get_about(self):
        """Get a short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Basestring containing a description of the resource.

        """

        return self._config.get('about', None)

    def _get_author(self):
        """Get the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Basestring containing the name of the author.

        """

        return self._config.get('author', None)

    def _get_branch(self):
        """Get the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Basestring containing the name of the branch.

        """

        return self._config.get('branch', None)

    def _get_email(self):
        """Get an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Basestring containing an email address of the author.

        """

        return self._config.get('email', None)

    def _get_fullname(self):
        """Get full name including 'branch' and 'version'.

        String concatenation of 'name', 'branch' and 'version'. Branch
        and version are only conatenated if they have allready been set.
        The fallname has to be unique for a given class and a given
        workspace.

        Returns:
            Basestring containing fullname of the resource.

        """

        l = [self._get_name(), self._get_branch(), self._get_version()]
        return '.'.join([str(item) for item in l if item])

    def _get_license(self):
        """Get the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Basestring containing the license reference of the resource.

        """

        return self._config.get('license', None)

    def _get_name(self):
        """Get the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            Basestring containing the name of the resource.

        """

        return self._config.get('name', None)

    def _get_path(self):
        """Get filepath.

        Path to a potential file containing or referencing the resource.

        Returns:
            Basestring containing the (potential) path of the resource.

        """

        return self._config.get('path', self._get_path_default())

    def _get_path_default(self):
        """Get default filepath.

        Path to a potential file containing or referencing the resource.

        Returns:
            Basestring containing the potential path of the resource.

        """

        module = self.__module__.split('.')[1]
        fileext = nemoa.get('default', 'filetype', module)
        path = nemoa.path(module + 's') or nemoa.common.ospath.getcwd()
        filename = '%s.%s' % (nemoa.common.ospath.get_clean_filename(
            self._get_fullname()), fileext)

        return nemoa.common.ospath.get_norm_path(path, filename)

    def _get_type(self):
        """Get instance type, using module name and class name.

        String concatenation of module name and class name of the
        instance.

        Returns:
            Basestring containing instance type identifier.

        """

        mname = self.__module__.split('.')[-1]
        cname = self.__class__.__name__
        return mname + '.' + cname

    def _get_version(self):
        """Get the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Integer value used as the version number of the resource.

        """

        return self._config.get('version', None)

    def _set_meta(self, key, *args, **kwargs):
        """Set meta information like 'author' or 'version'."""

        if key == 'about':   return self._set_about(*args, **kwargs)
        if key == 'author':  return self._set_author(*args, **kwargs)
        if key == 'branch':  return self._set_branch(*args, **kwargs)
        if key == 'email':   return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)
        if key == 'name':    return self._set_name(*args, **kwargs)
        if key == 'path':    return self._set_path(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)

        return nemoa.log('warning', "%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def _set_about(self, val):
        """Set short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'about' requires datatype 'basestring'.")
        self._config['about'] = val
        return True

    def _set_author(self, val):
        """Set the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'author' requires datatype 'basestring'.")
        self._config['author'] = val
        return True

    def _set_branch(self, val):
        """Set the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'branch' requires datatype 'basestring'.")
        self._config['branch'] = val
        return True

    def _set_email(self, val):
        """Set an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'email' requires datatype 'basestring'.")
        self._config['email'] = val
        return True

    def _set_license(self, val):
        """Set the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'license' requires datatype 'basestring'.")
        self._config['license'] = val
        return True

    def _set_name(self, val):
        """Set the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'name' requires datatype 'basestring'.")
        self._config['name'] = val
        return True

    def _set_path(self, val):
        """Set filepath.

        Path to a file containing or referencing the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'path' requires datatype 'basestring'.")
        self._config['path'] = val
        return True

    def _set_version(self, val):
        """Set the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, int): return nemoa.log('warning',
            "attribute 'version' requires datatype 'int'.")
        self._config['version'] = val
        return True

class Config:
    """nemoa configuration object."""

    _config = None
    _default = {
        'baseconf': ('%user_config_dir%', 'nemoa.ini'), # base config
        'basepath': { # search paths for workspaces
            'user': ('%user_data_dir%', 'workspaces'),
            'common': ('%site_data_dir%', 'workspaces') },
        'path': {}, # paths for logfile, cachefile, etc.
        'workspace_name': None, # current workspace name
        'workspace_base': None, # current workspace base name
        'workspace_path': { # current workspace paths
            'datasets': ('%workspace%', 'datasets'),
            'networks': ('%workspace%', 'networks'),
            'systems':  ('%workspace%', 'systems'),
            'models':   ('%workspace%', 'models'),
            'scripts':  ('%workspace%', 'scripts'),
            'cache':    ('%workspace%', 'cache'),
            'logfile':  ('%workspace%', 'nemoa.log') },
        'default': {
            'filetype': {
                'dataset': 'csv',
                'network': 'graphml',
                'system': 'npz',
                'model': 'npz',
                'script': 'py' }},
        'register': { # objects register
            'dataset': {},
            'network': {},
            'system': {},
            'model': {},
            'script': {} }}

    def __init__(self, shared = True, **kwargs):
        """ """

        self._config = nemoa.common.dict.merge(kwargs, self._default)

        import os

        # update basepaths from user configuration
        baseconfpath = self._expand_path(self._config['baseconf'])
        if os.path.exists(baseconfpath):
            ini_dict = nemoa.common.inifile.load(
                baseconfpath, {
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
            for workspace in self._get_workspaces(base = 'common'):
                self._set_workspace_scandir(workspace, 'common')

    def path(self, type = None, workspace = None, base = 'user'):
        """Return path."""

        # (optional) load workspace of given object
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()
        if workspace == None:
            workspace = cur_workspace
            base = cur_base
        elif not workspace == cur_workspace or not base == cur_base:
            if not self.load(workspace, base):
                nemoa.log('warning', """could not get path:
                    workspace '%s' does not exist.""" % (workspace))
                return  {}

        # get path
        if type == None: path = self._config['path'].copy()
        elif not isinstance(type, basestring):
            nemoa.log('warning', """could not get path:
                object type is not valid.""")
            path = None
        elif not type in self._config['path'].keys():
            nemoa.log('warning', """could not get path:
                object type '%s' is not valid.""" % (type))
            path = None
        else: path = self._config['path'][type]

        # (optional) load current workspace
        if cur_workspace:
            if not workspace == cur_workspace or not base == cur_base:
                self.load(cur_workspace, cur_base)

        return path

    def load(self, workspace, base = None):
        """Import workspace."""

        return self._set_workspace(workspace, base = base)

    def list(self, type = None, workspace = None, base = None):
        """List known object configurations."""

        if type == 'workspaces':
            return self._get_workspaces(base = base)

        if type == 'bases':
            return self._get_bases(workspace = workspace)

        if type:
            if not type in self._config['register']: return False

        # create dictionary
        objlist = []
        for key in self._config['register'].keys():
            if type and not key == type: continue
            for obj in self._config['register'][key].itervalues():
                if base and not base == obj['base']: continue
                if workspace and not workspace == obj['workspace']:
                    continue
                objlist.append(obj)

        return sorted(objlist, key = lambda obj: obj['name'])

    def get(self, key = 'workspace', *args, **kwargs):
        """Get meta information and content."""

        if key == 'base': return self._get_base()
        if key == 'bases': return self._get_bases(*args, **kwargs)
        if key == 'workspace': return self._get_workspace()
        if key == 'workspaces':
            return self._get_workspaces(*args, **kwargs)
        if key == 'default': return self._get_default(*args, **kwargs)

        # object configuration
        if key in self._config['register']:
            return self._get_objconfig(key, *args, **kwargs)
        if key in [rkey + 's' for rkey in self._config['register']]:
            return self._get_objconfigs(key[:-1], *args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_base(self):
        """Return name of current workspace search path."""

        return self._config.get('workspace_base', None)

    def _get_bases(self, workspace = None):
        """Return list of bases containing given workspace name."""

        if workspace == None:
            return sorted(self._config['basepath'].keys())

        bases = []
        for base in self._config['basepath']:
            if workspace in self._get_workspaces(base = base):
                bases.append(base)

        return sorted(bases)

    def _get_default(self, key = None, *args, **kwargs):
        """Get """
        
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

    def _get_objconfig(self, type, name = None,
        workspace = None, base = 'user'):
        """Get configuration of given object as dictionary."""

        if not type in self._config['register']:
            return nemoa.log('warning', """could not get configuration:
                object class '%s' is not supported.""" % (type))
        if not isinstance(name, basestring):
            return nemoa.log('warning', """could not get %s:
                name of object is not valid.""" % (type))

        # (optional) load workspace of given object
        cur_workspace = self._get_workspace()
        cur_base = self._get_base()
        if workspace == None:
            workspace = cur_workspace
            base = cur_base
        elif not workspace == cur_workspace or not base == cur_base:
            if not self.load(workspace, base):
                nemoa.log('warning', """could not get configuration:
                    workspace '%s' does not exist.""" % (workspace))
                return  {}

        # find object configuration in workspace
        search = [name, '%s.%s.%s' % (base, workspace, name),
            name + '.default', 'base.' + name]
        config = None
        for fullname in search:
            if fullname in self._config['register'][type].keys():
                config = self._config['register'][type][fullname]
                break

        # (optional) load current workspace
        if cur_workspace:
            if not workspace == cur_workspace or not base == cur_base:
                self.load(cur_workspace, cur_base)

        if not config:
            return nemoa.log('warning', """could not get configuration:
                %s with name '%s' is not found in
                %s workspace '%s'.""" % (type, name, base, workspace))

        return config

    def _get_objconfigs(self, type = None, workspace = None,
        base = None, attribute = 'name'):
        """List known object configurations."""

        if not type:
            objs = {}
            for obj in self._config['register']:
                objs[obj] = self._get_objconfigs(type = obj,
                    workspace = workspace, base = base)
            return objs

        if type:
            if not type in self._config['register']: return False

        # create dictionary
        objlist = []
        for key in self._config['register'].keys():
            if type and not key == type: continue
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

    def _get_workspace(self):
        """Return name of current workspace."""

        return self._config.get('workspace_name', None)

    def _get_workspaces(self, base = 'user'):
        """Return list of workspaces in given base."""

        if not base:
            workspaces = {}
            for base in self._config['basepath']:
                workspaces[base] = self._get_workspaces(base = base)
            return workspaces

        elif not base in self._config['basepath']:
            return nemoa.log('error', """could not get workspaces:
                unknown workspace base '%s'.""" % base)

        basepath = self._config['basepath'][base]
        baseglob = self._expand_path((basepath, '*'))

        import glob
        import os

        workspaces = []
        for subdir in glob.iglob(baseglob):
            if not os.path.isdir(subdir): continue

            # 2DO: check for workspace.ini or nemoa.ini etc
            workspaces.append(os.path.basename(subdir))

        return sorted(workspaces)

    def _expand_path(self, path, check = False, create = False):
        """Return string containing expanded path.

        Args:
            path"""

        import os

        path = nemoa.common.ospath.get_norm_path(path)

        # expand nemoa environment variables
        replace = {
            'workspace': self._config['workspace_name'],
            'base': self._config['workspace_base'] }
        for key, val in self._config['path'].iteritems():
            replace[key] = nemoa.common.ospath.get_norm_path(val)
        for key, val in self._config['basepath'].iteritems():
            replace[key] = nemoa.common.ospath.get_norm_path(val)
        for key in ['user_cache_dir', 'user_config_dir',
            'user_data_dir', 'user_log_dir', 'site_config_dir',
            'site_data_dir']:
            replace[key] = nemoa.common.ospath.getstorage(
                key, appname = 'nemoa', appauthor = 'Froot')

        update = True
        while update:
            update = False
            for key, val in replace.iteritems():
                if not '%' + key + '%' in path:
                    continue
                path = path.replace('%' + key + '%', val)
                update = True

        # (optional) create directory
        if create and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # (optional) check path
        if check and not os.path.exists(path):
            return nemoa.log('warning',
                "directory '%s' does not exist!" % (path))

        return path

    def set(self, key = None, *args, **kwargs):
        """Set configuration parameters and env vars."""

        if key == 'workspace':
            return self._set_workspace(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_workspace(self, workspace, base = None,
        refresh = False, scandir = True, setlog = True):
        """Set workspace."""

        if not workspace: return True
        if workspace == self._config['workspace_name'] and not refresh:
            return True
        if not base:
            bases = self._get_bases(workspace)
            if not bases:
                return nemoa.log('error', """could not open workspace
                    '%s': workspace could not be found
                    in any searchpath.""" % workspace)
            if len(bases) > 1:
                return nemoa.log('error', """could not open workspace
                    '%s': workspace found in different searchpaths:
                    %s.""" % (workspace, ', '.join(bases)))
            base = bases[0]
        elif not workspace in self._get_workspaces(base = base):
            basepath = self._expand_path(self._config['basepath'][base])
            return nemoa.log('error', """could not open workspace
                '%s': workspace could not be found in searchpath
                '%s'.""" % (workspace, basepath))

        # update workspace name and workspace base name
        self._config['workspace_name'] = workspace
        self._config['workspace_base'] = base

        # update paths
        for key in self._config['workspace_path']:
            path = self._expand_path(('%' + base + '%',
                self._config['workspace_path'][key]))
            self._config['path'][key] = path

        # (optional) initialise logfile of new workspace
        if setlog:
            logpath = self._expand_path(self._config['path']['logfile'])
            nemoa.log('init', logfile = logpath)

        # (optional) scan workspace folder for objects / files
        if scandir:
            self._set_workspace_scandir()

        return True

    def _set_workspace_scandir(self, workspace = None, base = None):
        """Scan workspace for files."""

        import glob

        # change current workspace
        if workspace:
            cur_workspace = self._config['workspace_name']
            cur_workspace_base = self._config['workspace_base']
            if not self._set_workspace(workspace, base = base,
                setlog = False, scandir = False):
                return False
        else:
            cur_workspace = None
            cur_workspace_base = None
            workspace = self._config['workspace_name']

        for type in self._config['register'].keys():
            filemask = self._expand_path(
                (self._config['path'][type + 's'], '*.*'))
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
            for path in glob.iglob(filemask):
                filetype = nemoa.common.ospath.fileext(path)
                if not filetype in filetypes:
                    continue
                name = nemoa.common.ospath.basename(path)
                workspace = self._get_workspace()
                base = self._get_base()
                fullname = '%s.%s.%s' % (base, workspace, name)
                if fullname in self._config['register'][type]:
                    continue

                # add configuration to object tree
                self._config['register'][type][fullname] = {
                    'name': name,
                    'type': type,
                    'path': path,
                    'workspace': workspace,
                    'base': base,
                    'fullname': fullname }

        # change current workspace and update paths
        if workspace and not workspace == cur_workspace:
            self._set_workspace(cur_workspace,
                base = cur_workspace_base)

        return True
