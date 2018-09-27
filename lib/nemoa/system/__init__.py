# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes
import nemoa.system.commons
import nemoa.system.imports
import nemoa.system.exports

def copy(system, *args, **kwargs):
    """Create copy of system instance."""
    return new(**system.get('copy'))

def load(*args, **kwargs):
    """Import system dictionary from file."""
    return nemoa.system.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create system instance from system dictionary."""
    return nemoa.system.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import system instance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export system instance to file."""
    return nemoa.system.exports.save(*args, **kwargs)
