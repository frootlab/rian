# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.base
import nemoa.dataset.annotation
import nemoa.dataset.fileimport
import nemoa.dataset.fileexport
import importlib

def load(*args, **kwargs):
    """Import dataset configuration and parameters from file."""
    return nemoa.dataset.fileimport.load(*args, **kwargs)

def save(*args, **kwargs):
    """Export dataset configuration and parameters to file."""
    return nemoa.dataset.fileexport.save(*args, **kwargs)

def open(*args, **kwargs):
    copy = nemoa.dataset.fileimport.load(*args, **kwargs)
    if not copy: return None
    dataset = new(config = copy['config'])
    dataset.set('copy', **copy)
    return dataset

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

def show(*args, **kwargs):
    return save(*args, output = 'display', **kwargs)
