#!/usr/bin/env python
# -*- coding: utf-8 -*-

__shared = {}

def init():
    """Create and link new configuration instance."""
    import nemoa.workspace.config
    __shared['config'] = nemoa.workspace.config.config()
    __shared['config'].loadCommon()
    return True

# wrap config object instance methods to module

def get(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].get(*args, **kwargs)

def list(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].list(*args, **kwargs)

def path(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].path(*args, **kwargs)

def project(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].project(*args, **kwargs)

def getPath(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].getPath(*args, **kwargs)

def loadProject(*args, **kwargs):
    if not 'config' in __shared:
        init()
    return __shared['config'].loadProject(*args, **kwargs)

def new():
    """Return new workspace instance."""
    import nemoa.workspace.workspace
    return nemoa.workspace.workspace.workspace()

def open(project, quiet = False):
    """Return new workspace instance and open project."""
    import nemoa.workspace.workspace
    return nemoa.workspace.workspace.workspace(project)
