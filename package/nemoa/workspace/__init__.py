#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, copy

__shared = {}

# create common configuration instance

def init():
    """Create and link new configuration instance."""
    import nemoa.workspace.config
    __shared['config'] = nemoa.workspace.config.config()
    __shared['config'].loadCommon()
    return True

# create workspace instance

def new():
    """Return new workspace instance."""
    import nemoa.workspace.workspace
    return nemoa.workspace.workspace.workspace()

def open(project):
    """Return new workspace instance and open project."""
    import nemoa.workspace.workspace
    return nemoa.workspace.workspace.workspace(project)

# wrap configuration object instance methods to module dict

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

def getPath(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].getPath(*args, **kwargs)

def loadProject(*args, **kwargs):
    if not 'config' in __shared: init()
    return __shared['config'].loadProject(*args, **kwargs)

def getConfig(type = None, config = None, merge = ['params'], **kwargs):
    """Return object configuration as dictionary."""
    if config == None: return {}
    if isinstance(config, dict): return copy.deepcopy(config)
    elif not isinstance(config, str) or not isinstance(type, str): return False

    name, params = nemoa.common.strSplitParams(config)
    if 'params' in kwargs and isinstance(kwargs['params'], dict):
        params = nemoa.common.dictMerge(kwargs['params'], params)

    config = __shared['config'].get(type = type, name = name,
        merge = merge, params = params)
    if not config: config = __shared['config'].get(type = type,
        name = '%s.%s' % (project(), name), merge = merge, params = params)
    if not config: config = __shared['config'].get(type = type,
        name = 'base.' + name, merge = merge, params = params)
    if not config: return nemoa.log('warning', """
        could not get configuration:
        no %s with name '%s' could be found""" % (type, name))

    return config
