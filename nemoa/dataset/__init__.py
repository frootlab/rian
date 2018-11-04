# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwds):
    """Create dataset dictionary from building script."""
    from nemoa.dataset import builder
    return builder.build(*args, **kwds)

def copy(dataset, *args, **kwds):
    """Create copy of dataset instance."""
    return new(**dataset.get('copy'))

def create(*args, **kwds):
    """Create dataset instance from building script."""
    return new(**build(*args, **kwds))

def load(*args, **kwds):
    """Import dataset dictionary from file."""
    from nemoa.dataset import imports
    return imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create dataset instance from dataset dictionary."""
    from nemoa.dataset import classes
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import dataset instance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export dataset instance to file."""
    from nemoa.dataset import exports
    return exports.save(*args, **kwds)

def show(*args, **kwds):
    """Show dataset as image."""
    from nemoa.dataset import exports
    return exports.show(*args, **kwds)
