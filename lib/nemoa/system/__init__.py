# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def copy(system, *args, **kwargs):
    """Create copy of system instance."""
    return new(**system.get('copy'))

def load(*args, **kwargs):
    """Import system dictionary from file."""
    import nemoa.system.imports
    return nemoa.system.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create system instance from system dictionary."""
    import nemoa.system.classes
    return nemoa.system.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import system instance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export system instance to file."""
    import nemoa.system.exports
    return nemoa.system.exports.save(*args, **kwargs)
