# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.classes.base
import importlib

def new(*args, **kwargs):
    """Create new network instance."""
    if not 'config' in kwargs: return None # TODO: error message
    config = kwargs['config']
    if not 'type' in config: return None
    if not '.' in config['type']: return None
    module_name = 'nemoa.network.classes.' + config['type'].split('.')[0]
    class_name = config['type'].split('.')[1]
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        network = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create network:
            unknown network type '%s'.""" % (config['type']))
    return network
