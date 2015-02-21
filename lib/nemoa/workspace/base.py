# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import glob
import imp
import nemoa
import os

class Workspace:
    """Nemoa workspace class."""

    _config = None
    _attr_meta = {'name': 'r', 'about': 'rw', 'path': 'r', 'base': 'r'}

    def __init__(self, workspace = None, base = None):
        """Initialize shared configuration."""

        self._config = {}

        if workspace:
            self.load(workspace, base = base)

    def __getattr__(self, key):
        """Attribute wrapper to getter methods."""

        if key in self._attr_meta:
            if 'r' in self._attr_meta[key]: return self._get_meta(key)
            return nemoa.log('warning',
                "attribute '%s' is not readable.")

        raise AttributeError('%s instance has no attribute %r'
            % (self.__class__.__name__, key))

    def __setattr__(self, key, val):
        """Attribute wrapper to setter methods."""

        if key in self._attr_meta:
            if 'w' in self._attr_meta[key]:
                return self._set_meta(key, val)
            return nemoa.log('warning',
                "attribute '%s' is not writeable." % (key))

        self.__dict__[key] = val

    #def load(self, workspace, base = None):
        #"""Import workspace and update paths and logfile."""

        #if nemoa.load(workspace, base = base):
            #self._config['name'] = workspace
            #self._config['base'] = base
            #return True

        #return nemoa.log('error', """could not load workspace:
            #no workspace '%s' could be found.""" % (workspace))

    def _get_meta(self, key):
        """Get meta information like 'name' or 'path'."""

        if key == 'about': return self._get_about()
        if key == 'base': return self._get_about()
        if key == 'name': return self._get_name()
        if key == 'path': return self._get_path()

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_about(self):
        """Get description.

        Short description of the content of the resource.

        Returns:
            Basestring containing a description of the resource.

        """

        if 'about' in self._config: return self._config['about']

        return None

    def _get_base(self):
        """Get workspace base."""

        if 'base' in self._config: return self._config['base']

        return None

    def _get_name(self):
        """Get name."""

        if 'name' in self._config: return self._config['name']

        return None

    def _get_path(self):
        """Get path."""

        if 'path' in self._config: return self._config['path']

        return None

    def _set_meta(self, key, *args, **kwargs):
        """Set meta information like 'name' or 'path'."""

        if key == 'about': return self._set_about(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_about(self, val):
        """Set description."""

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'about' requires datatype 'basestring'.")
        self._config['about'] = val

        return True

    def list(self, type = None):
        """Return a list of known objects."""

        return nemoa.list(type = type,
            workspace = self._get_name(), base = self._get_base())

    def execute(self, name = None, *args, **kwargs):
        """Execute script."""

        config = nemoa.get('script', name)
        if not config: return False
        if not os.path.isfile(config['path']):
            return nemoa.log('error', """could not run script '%s':
                file '%s' not found.""" % (name, config['path']))

        module = imp.load_source('script', config['path'])
        return module.main(self, *args, **kwargs)
