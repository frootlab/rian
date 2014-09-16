#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'

import importlib

def new(*args, **kwargs):
    """Return new nemoa.plot.[package].[class] instance."""
    config = kwargs['config'] if 'config' in kwargs \
        else {'package': 'base', 'class': 'empty'}
    if not 'package' in config: return None
    module = importlib.import_module('nemoa.plot.' + config['package'])
    if hasattr(module, config['class']): return \
        getattr(module, config['class'])(*args, **kwargs)
    return None

def empty():
    """Return new nemoa.plot.base.empty instance."""
    return new()
