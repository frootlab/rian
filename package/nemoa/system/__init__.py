# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes
import nemoa.system.imports
import nemoa.system.exports

def copy(system, *args, **kwargs):
    """Create copy of system."""
    return new(**system.get('copy'))

def load(*args, **kwargs):
    """Import system configuration and parameters from file."""
    return nemoa.system.imports.load(*args, **kwargs)

def save(*args, **kwargs):
    """Export system configuration and parameters to file."""
    return nemoa.system.exports.save(*args, **kwargs)

def open(*args, **kwargs):
    """Import system from file and create new system instance."""
    return new(**load(*args, **kwargs))

def new(*args, **kwargs):
    """Create new system instance."""
    return nemoa.system.classes.new(*args, **kwargs)
