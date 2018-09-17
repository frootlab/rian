# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def load(*args, **kwargs):
    """Import workspace dictionary from file."""
    from nemoa.workspace import imports
    return imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create workspace instance from workspace dictionary."""
    from nemoa.workspace import classes
    return classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import workspace instance from file."""
    return new(**load(*args, **kwargs))
