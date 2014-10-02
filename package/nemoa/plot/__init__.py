# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa.plot.base

def new(*args, **kwargs):
    """return new nemoa.plot.[package].[class] instance."""
    if not 'config' in kwargs: return False
    config = kwargs['config']
    if not 'package' in config: return False
    module = importlib.import_module('nemoa.plot.' + config['package'])
    if hasattr(module, config['class']): return \
        getattr(module, config['class'])(*args, **kwargs)
    return False
