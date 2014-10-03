# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.base
import importlib

def new(*args, **kwargs):
    """Return new nemoa.system.[package].[class] instance."""
    if not 'config' in kwargs: return None
    config = kwargs['config']
    module = importlib.import_module('nemoa.system.' + config['package'])
    if hasattr(module, config['class']):
        return getattr(module, config['class'])(*args, **kwargs)
    return None

def _update_system_config(obj_conf):
    """Update system configuration"""

    config = obj_conf['config']

    # system module
    if not 'package' in config:
        return nemoa.log('warning', """skipping system '%s':
            missing parameter 'package'.""" % (name))
    try:
        module_name = 'nemoa.system.%s' % (config['package'])
        system_module = importlib.import_module(module_name)
    except:
        return nemoa.log('warning', """skipping system '%s':
            python module 'nemoa.system.%s' could not be imported.
            (parameter 'package').""" % (name, config['package']))

    # system class
    if not 'class' in config:
        return nemoa.log('warning', """skipping system '%s':
            missing parameter 'class'.""" % (name))
    if not hasattr(system_module, config['class']):
        return nemoa.log('warning', """skipping system '%s':
            python module 'nemoa.system.%s' does not contain class
            '%s'. (parameter 'class')."""
            % (name, config['class'], config['package']))
    else:
        system_class = getattr(system_module, config['class'])

    # update system description
    if not 'description' in config:
        obj_conf['config']['description'] = system_class.__doc__
    else:
        obj_conf['config']['description'] = \
            nemoa.common.str_doc_trim(config['description'])

    # cleanup
    del system_class
    del system_module

    return obj_conf
