# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwargs):
    """Create dataset dictionary from building script."""
    from nemoa.dataset import builder
    return builder.build(*args, **kwargs)

def copy(dataset, *args, **kwargs):
    """Create copy of dataset instance."""
    return new(**dataset.get('copy'))

def create(*args, **kwargs):
    """Create dataset instance from building script."""
    return new(**build(*args, **kwargs))

def load(*args, **kwargs):
    """Import dataset dictionary from file."""
    from nemoa.dataset import imports
    return imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create dataset instance from dataset dictionary."""
    from nemoa.dataset import classes
    return classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import dataset instance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export dataset instance to file."""
    from nemoa.dataset import exports
    return exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show dataset as image."""
    from nemoa.dataset import exports
    return exports.show(*args, **kwargs)
