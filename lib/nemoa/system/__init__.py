# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes
import nemoa.system.commons
import nemoa.system.imports
import nemoa.system.exports

def copy(system, *args, **kwds):
    """Create copy of system instance."""
    return new(**system.get('copy'))

def load(*args, **kwds):
    """Import system dictionary from file."""
    return nemoa.system.imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create system instance from system dictionary."""
    return nemoa.system.classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import system instance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export system instance to file."""
    return nemoa.system.exports.save(*args, **kwds)
