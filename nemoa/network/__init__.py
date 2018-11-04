# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwds):
    """Create network dictionary from building script."""
    from nemoa.network import builder
    return builder.build(*args, **kwds)

def copy(network, *args, **kwds):
    """Create copy of network instance."""
    return new(**network.get('copy'))

def create(*args, **kwds):
    """Create network instance from building script."""
    return new(**build(*args, **kwds))

def load(*args, **kwds):
    """Import network dictionary from file."""
    from nemoa.network import imports
    return imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create network instance from network dictionary."""
    from nemoa.network import classes
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import network intance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export network intance to file."""
    from nemoa.network import exports
    return exports.save(*args, **kwds)

def show(*args, **kwds):
    """Show network as image."""
    from nemoa.network import exports
    return exports.show(*args, **kwds)
