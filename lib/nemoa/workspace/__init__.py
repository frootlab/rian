# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def load(*args, **kwds):
    """Import workspace dictionary from file."""
    from nemoa.workspace import imports
    return imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create workspace instance from workspace dictionary."""
    from nemoa.workspace import classes
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import workspace instance from file."""
    return new(**load(*args, **kwds))
