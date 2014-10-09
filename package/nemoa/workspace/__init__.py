# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.base
import importlib
import copy

_shared = {}

def _init():
    """Create and link new configuration instance."""
    if not 'config' in _shared:
        _shared['config'] = nemoa.workspace.base.Config()
    return True

def new():
    """Return new workspace instance."""
    return nemoa.workspace.base.Workspace()

def open(*args, **kwargs):
    """Import and return workspace instance."""
    return nemoa.workspace.base.Workspace(*args, **kwargs)

def get(*args, **kwargs):
    if not 'config' in _shared: _init()
    return _shared['config'].get(*args, **kwargs)

def list(*args, **kwargs):
    if not 'config' in _shared: _init()
    return _shared['config'].list(*args, **kwargs)

def path(*args, **kwargs):
    if not 'config' in _shared: _init()
    return _shared['config'].path(*args, **kwargs)

def name():
    if not 'config' in _shared: _init()
    return _shared['config'].workspace()

def load(*args, **kwargs):
    if not 'config' in _shared: _init()
    return _shared['config'].load(*args, **kwargs)

def _get_config(type = None, config = None,
    merge = ['params'], **kwargs):
    """Return object configuration as dictionary."""
    if config == None: return {}
    if isinstance(config, dict): return copy.deepcopy(config)
    elif not isinstance(config, str) \
        or not isinstance(type, str): return False

    config_name, params = nemoa.common.str_split_params(config)
    if 'params' in kwargs and isinstance(kwargs['params'], dict):
        params = nemoa.common.dict_merge(kwargs['params'], params)

    search = [config_name, '%s.%s' % (name(), config_name),
        config_name + '.default', 'base.' + config_name]
    if isinstance(config, str):
        search += [config, '%s.%s' % (name(), config),
        config + '.default', 'base.' + config]

    # get config
    if not config_name: config_name = name() + '.default'
    found = False
    for cfg_name in search:
        cfg = _shared['config'].get(
            type = type, name = cfg_name, merge = merge, params = params)
        if isinstance(cfg, dict):
            found = True
            break

    if not found:
        return nemoa.log('error', """could not get configuration:
            no %s with name '%s' could be found."""
            % (type, config_name))

    if type == 'network':
        return nemoa.network.load(cfg['path'])['config']

    return cfg



