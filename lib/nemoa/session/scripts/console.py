# -*- coding: utf-8 -*-
"""nemoa console commands."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def about(*args, **kwargs):
    """Wrapping function to nemoa.about()."""
    nemoa.log('note', nemoa.about(*args, **kwargs))
    return None

def get(*args, **kwargs):
    """Wrapping function to nemoa.get()."""
    nemoa.log('note', nemoa.get(*args, **kwargs))
    return None

def list(*args, **kwargs):
    """Wrapping function to nemoa.list()."""
    retval = nemoa.list(*args, **kwargs)
    if isinstance(retval, dict):
        for key, val in retval.items():
            if not val: continue
            if hasattr(val, '__iter__'):
                nemoa.log('note', '%s: %s' % (key, ', '.join(val)))
            else:
                nemoa.log('note', '%s: %s' % (key, val))
    elif hasattr(retval, '__iter__'):
        nemoa.log('note', ', '.join(retval))

    return None

def open(*args, **kwargs):
    """Wrapping function to nemoa.open()."""
    if not args:
        return None
    if len(args) == 1:
        nemoa.open(args[0])
        return None
    if len(args) == 2:
        if args[0] == 'workspace':
            nemoa.open(args[1])
            return None
        if args[0] == 'model':
            return nemoa.model.open(args[1], **kwargs)
        if args[0] == 'dataset':
            return nemoa.dataset.open(args[1], **kwargs)
        if args[0] == 'network':
            return nemoa.network.open(args[1], **kwargs)
        if args[0] == 'system':
            return nemoa.system.open(args[1], **kwargs)
    return None

def path(*args, **kwargs):
    """Wrapping function to nemoa.path()."""
    nemoa.log('note', nemoa.path(*args, **kwargs))
    return None

def run(*args, **kwargs):
    """Wrapping function to nemoa.run()."""
    nemoa.run(*args, **kwargs)
    return None

def set(*args, **kwargs):
    """Wrapping function to nemoa.set()."""
    nemoa.set(*args, **kwargs)
    return None
