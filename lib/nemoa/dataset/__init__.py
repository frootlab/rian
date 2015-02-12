# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.builder
import nemoa.dataset.classes
import nemoa.dataset.commons
import nemoa.dataset.exports
import nemoa.dataset.imports

def build(*args, **kwargs):
    """Create dataset dictionary from building script."""
    return nemoa.dataset.builder.build(*args, **kwargs)

def copy(dataset, *args, **kwargs):
    """Create copy of dataset instance."""
    return new(**dataset.get('copy'))

def create(*args, **kwargs):
    """Create dataset instance from building script."""
    return new(**build(*args, **kwargs))

def load(*args, **kwargs):
    """Import dataset dictionary from file."""
    return nemoa.dataset.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create dataset instance from dataset dictionary."""
    return nemoa.dataset.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import dataset instance from file."""
    return new(**load(*args, **kwargs))

def save(*args, **kwargs):
    """Export dataset instance to file."""
    return nemoa.dataset.exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show dataset as image."""
    return nemoa.dataset.exports.show(*args, **kwargs)
