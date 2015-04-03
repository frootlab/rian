# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwargs):
    """Create network dictionary from building script."""
    import nemoa.network.builder
    return nemoa.network.builder.build(*args, **kwargs)

def copy(network, *args, **kwargs):
    """Create copy of network instance."""
    return new(**network.get('copy'))

def create(*args, **kwargs):
    """Create network instance from building script."""
    return new(**build(*args, **kwargs))

def load(*args, **kwargs):
    """Import network dictionary from file."""
    import nemoa.network.imports
    return nemoa.network.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create network instance from network dictionary."""
    import nemoa.network.classes
    return nemoa.network.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import network intance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export network intance to file."""
    import nemoa.network.exports
    return nemoa.network.exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show network as image."""
    import nemoa.network.exports
    return nemoa.network.exports.show(*args, **kwargs)
