# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.classes
import nemoa.dataset.annotation
import nemoa.dataset.fileimport
import nemoa.dataset.fileexport

def load(*args, **kwargs):
    """Import dataset configuration and parameters from file."""
    return nemoa.dataset.fileimport.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create new dataset instance."""
    return nemoa.dataset.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import dataset from file and create new dataset instance."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export dataset configuration and parameters to file."""
    return nemoa.dataset.fileexport.save(*args, **kwargs)

def show(*args, **kwargs):
    return save(*args, output = 'display', **kwargs)
