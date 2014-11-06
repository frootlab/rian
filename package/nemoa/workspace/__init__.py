# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.base

_shared = {}

def configure():
    """Create and link new configuration instance."""
    _shared['config'] = nemoa.workspace.base.Config()
    return True

def new():
    """Return new workspace instance."""
    if not 'config' in _shared: configure()
    return nemoa.workspace.base.Workspace()

def open(*args, **kwargs):
    """Import and return workspace instance."""
    if not 'config' in _shared: configure()
    return nemoa.workspace.base.Workspace(*args, **kwargs)

def get(*args, **kwargs):
    if not 'config' in _shared: configure()
    return _shared['config'].get(*args, **kwargs)

def list(*args, **kwargs):
    if not 'config' in _shared: configure()
    return _shared['config'].list(*args, **kwargs)

def path(*args, **kwargs):
    if not 'config' in _shared: configure()
    return _shared['config'].path(*args, **kwargs)

def name():
    if not 'config' in _shared: configure()
    return _shared['config'].workspace()

def load(*args, **kwargs):
    if not 'config' in _shared: configure()
    return _shared['config'].load(*args, **kwargs)

def find(type = None, config = None, merge = ['params'], **kwargs):
    """Return object configuration as dictionary."""
    if not 'config' in _shared: configure()

    if config == None: return {}
    if isinstance(config, dict): return config.copy()
    if not isinstance(config, basestring) \
        or not isinstance(type, basestring):
        print 'hi'
        return False

    config_name, params = nemoa.common.str_split_params(config)
    if 'params' in kwargs and isinstance(kwargs['params'], dict):
        params = nemoa.common.dict_merge(kwargs['params'], params)

    # get config
    return _shared['config'].get(type = type, name = config_name,
        merge = merge, params = params)

