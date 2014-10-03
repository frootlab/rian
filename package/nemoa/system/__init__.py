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
