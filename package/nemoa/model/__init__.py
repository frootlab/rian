# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.classes
import nemoa.model.fileimport
import nemoa.model.fileexport

def load(*args, **kwargs):
    """Import model configuration and parameters from file."""
    return nemoa.model.fileimport.load(*args, **kwargs)

def save(*args, **kwargs):
    """Export model configuration and parameters to file."""
    return nemoa.model.fileexport.save(*args, **kwargs)

def open(*args, **kwargs):
    """Import model from file and create new model instance."""
    return new(**load(*args, **kwargs))

def new(*args, **kwargs):
    """Return model instance."""
    return nemoa.model.classes.new(*args, **kwargs)
