#!/usr/bin/env python
# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """Return new metapath.system.[package].[class] instance."""
    config = kwargs['config'] if 'config' in kwargs \
        else {'package': 'base', 'class': 'empty'}
    import importlib
    module = importlib.import_module('metapath.system.' + config['package'])
    if hasattr(module, config['class']):
        return getattr(module, config['class'])(*args, **kwargs)
    return None

def empty():
    """Return new metapath.system.base.empty instance."""
    import metapath.system.base
    return metapath.system.base.empty()
