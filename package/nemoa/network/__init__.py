# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.classes
import nemoa.network.fileexport
import nemoa.network.fileimport

def load(*args, **kwargs):
    """Import network from file."""
    return nemoa.network.fileimport.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create new network instance."""
    return nemoa.network.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import network from file and create new network instance."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export network to file."""
    return nemoa.network.fileexport.save(*args, **kwargs)

def show(*args, **kwargs):
    return save(*args, output = 'display', **kwargs)
