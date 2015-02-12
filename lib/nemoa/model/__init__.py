# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.builder
import nemoa.model.classes
import nemoa.model.exports
import nemoa.model.imports

def build(*args, **kwargs):
    """Create model dictionary from building script."""
    return nemoa.model.builder.build(*args, **kwargs)

def copy(model, *args, **kwargs):
    """Create copy of model instance."""
    return new(**model.get('copy'))

def create(*args, **kwargs):
    """Create model instance from building script."""
    return new(**build(*args, **kwargs))

def load(*args, **kwargs):
    """Import model dictionary from file."""
    return nemoa.model.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create model instance from model dictionary."""
    return nemoa.model.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import model instance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export model instance to file."""
    return nemoa.model.exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show model as image."""
    return nemoa.model.exports.show(*args, **kwargs)
