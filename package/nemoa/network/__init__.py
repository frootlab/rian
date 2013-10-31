#!/usr/bin/env python
# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """Return new nemoa.network.[package].[class] instance."""
    config = kwargs['config'] if 'config' in kwargs \
        else {'package': 'base', 'class': 'empty'}
    import importlib
    module = importlib.import_module('nemoa.network.' + config['package'])
    if hasattr(module, config['class']):
        return getattr(module, config['class'])(*args, **kwargs)
    return None

def empty():
    """Return new nemoa.network.base.empty instance."""
    import nemoa.network.base
    return nemoa.network.base.network()
