# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwargs):
    """Create network dictionary from building script."""
    from nemoa.network import builder
    return builder.build(*args, **kwargs)

def copy(network, *args, **kwargs):
    """Create copy of network instance."""
    return new(**network.get('copy'))

def create(*args, **kwargs):
    """Create network instance from building script."""
    return new(**build(*args, **kwargs))

def load(*args, **kwargs):
    """Import network dictionary from file."""
    from nemoa.network import imports
    return imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create network instance from network dictionary."""
    from nemoa.network import classes
    return classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import network intance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export network intance to file."""
    from nemoa.network import exports
    return exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show network as image."""
    from nemoa.network import exports
    return exports.show(*args, **kwargs)
