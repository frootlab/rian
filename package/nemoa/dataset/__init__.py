# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.base
import nemoa.dataset.annotation
import nemoa.dataset.fileimport
import nemoa.dataset.fileexport
import importlib

def open(*args, **kwargs):
    obj_config = nemoa.dataset.fileimport.open(*args, **kwargs)
    if not obj_config: return None
    return new(config = obj_config['config'])

def save(*args, **kwargs):
    ret_val = nemoa.dataset.fileexport.save(*args, **kwargs)
    if not ret_val: return None
    return True

def new(*args, **kwargs):
    """Return dataset instance."""
    if not 'config' in kwargs: return None
    config = kwargs['config']
    if not 'type' in config: return None
    if not '.' in config['type']: return None
    module_name = 'nemoa.dataset.' + config['type'].split('.')[0]
    class_name = config['type'].split('.')[1]
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        dataset = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create dataset:
            unknown dataset type '%s'.""" % (config['type']))
    return dataset
