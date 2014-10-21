# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.annotation
import nemoa.dataset.classes
import nemoa.dataset.exports
import nemoa.dataset.imports

def load(*args, **kwargs):
    """Import dataset configuration and parameters from file."""
    return nemoa.dataset.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create new dataset instance."""
    return nemoa.dataset.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import dataset from file and create new dataset instance."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export dataset configuration and parameters to file."""
    return nemoa.dataset.exports.save(*args, **kwargs)

def show(*args, **kwargs):
    return save(*args, output = 'display', **kwargs)
