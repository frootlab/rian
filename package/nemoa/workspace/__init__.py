# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.base
import importlib
import copy

__shared = {}

def init():
    """Create and link new configuration instance."""
    __shared['config'] = nemoa.workspace.base.config()
    return True

def new():
    """Return new workspace instance."""
    return nemoa.workspace.base.workspace()

def open(*args, **kwargs):
    """Return new workspace instance and open project."""
    return nemoa.workspace.base.workspace(*args, **kwargs)

def get(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].get(*args, **kwargs)

def list(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].list(*args, **kwargs)

def path(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].path(*args, **kwargs)

def project(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].project(*args, **kwargs)

def load(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].load(*args, **kwargs)

def getConfig(type = None, config = None, merge = ['params'], **kwargs):
    """Return object configuration as dictionary."""
    if config == None: return {}
    if isinstance(config, dict): return copy.deepcopy(config)
    elif not isinstance(config, str) or not isinstance(type, str): return False

    name, params = nemoa.common.strSplitParams(config)
    if 'params' in kwargs and isinstance(kwargs['params'], dict):
        params = nemoa.common.dictMerge(kwargs['params'], params)

    search = [name, '%s.%s' % (project(), name),
        name + '.default', 'base.' + name]
    if isinstance(config, str):
        search += [config, '%s.%s' % (project(), config),
        config + '.default', 'base.' + config]

    # get config
    if not name: name = project() + '.default'
    for cfgName in search:
        cfg = __shared['config'].get(
            type = type, name = cfgName, merge = merge, params = params)
        if isinstance(cfg, dict): return cfg

    return nemoa.log('error', """could not get configuration:
        no %s with name '%s' could be found""" % (type, name))
