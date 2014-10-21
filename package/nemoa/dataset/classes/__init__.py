# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.classes.base
import importlib

def new(*args, **kwargs):
    """Create new dataset instance."""
    if not 'config' in kwargs: return None
    config = kwargs['config']
    if not 'type' in config: return None
    if not '.' in config['type']: return None
    module_name = 'nemoa.dataset.classes.' + config['type'].split('.')[0]
    class_name = config['type'].split('.')[1]
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        dataset = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create dataset:
            unknown dataset type '%s'.""" % (config['type']))
    return dataset
