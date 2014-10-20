# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.base
import nemoa.system.fileimport
import nemoa.system.fileexport
import importlib

def load(*args, **kwargs):
    """Import system configuration and parameters from file."""
    return nemoa.system.fileimport.load(*args, **kwargs)

def save(*args, **kwargs):
    """Export system configuration and parameters to file."""
    return nemoa.system.fileexport.save(*args, **kwargs)

def open(*args, **kwargs):
    """Import system from file and create new system instance."""
    return new(**load(*args, **kwargs))

def new(*args, **kwargs):
    """Return new nemoa.system.[package].[class] instance."""
    if not 'config' in kwargs: return None
    config = kwargs['config']
    module = importlib.import_module('nemoa.system.' + config['package'])
    if hasattr(module, config['class']):
        return getattr(module, config['class'])(*args, **kwargs)
    return None

#def new(*args, **kwargs):
    #"""Return system instance."""
    #if not 'config' in kwargs: return None
    #config = kwargs['config']
    #if 'type' in config and '.' in config['type']:
        #module_name = 'nemoa.system.' + config['type'].split('.')[0]
        #class_name = config['type'].split('.')[1]
    #elif 'package' in config and 'class' in config:
        #module_name = 'nemoa.system.' + config['package']
        #class_name = config['class']
        #config['type'] = config['package'] + '.' + config['class']
    #else: return None
    #try:
        #module = importlib.import_module(module_name)
        #if not hasattr(module, class_name): raise ImportError()
        #system = getattr(module, class_name)(*args, **kwargs)
    #except ImportError:
        #return nemoa.log('error', """could not create system:
            #unknown system type '%s'.""" % (config['type']))
    #return system

def show(*args, **kwargs):
    return save(*args, output = 'display', **kwargs)
