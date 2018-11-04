# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.classes.base
import importlib

def new(*args, **kwds):
    """Create new workspace instance."""

    if not kwds:
        kwds = {'config': {'type': 'base.Workspace'}}

    if 'config' not in kwds or 'type' not in kwds['config'] \
        or len(kwds['config']['type'].split('.')) != 2:
        raise ValueError("""could not create workspace:
            configuration is not valid.""")

    type = kwds['config']['type']
    module_name = 'nemoa.workspace.classes.' + type.split('.', 1)[0]
    class_name = type.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):
            raise ImportError()
        workspace = getattr(module, class_name)(**kwds)
    except ImportError:
        raise ValueError("""could not create workspace:
            unknown workspace type '%s'.""" % (type))

    return workspace
