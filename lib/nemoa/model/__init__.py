# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def build(*args, **kwargs):
    """Create model dictionary from building script."""
    import nemoa.model.builder
    return nemoa.model.builder.build(*args, **kwargs)

def copy(model, *args, **kwargs):
    """Create copy of model instance."""
    return new(**model.get('copy'))

def create(*args, **kwargs):
    """Create model instance from building script."""
    return new(**build(*args, **kwargs))

def evaluate(*args, **kwargs):
    """Evaluate model instance."""
    import nemoa.model.evaluation
    return nemoa.model.evaluation.evaluate(*args, **kwargs)

def load(*args, **kwargs):
    """Import model dictionary from file."""
    import nemoa.model.imports
    return nemoa.model.imports.load(*args, **kwargs)

def new(*args, **kwargs):
    """Create model instance from model dictionary."""
    import nemoa.model.classes
    return nemoa.model.classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Import model instance from file."""
    return new(**load(*args, **kwargs))

def optimize(*args, **kwargs):
    """Optimize model instance."""
    import nemoa.model.optimizer
    return nemoa.model.optimizer.optimize(*args, **kwargs)

def save(*args, **kwargs):
    """Export model instance to file."""
    import nemoa.model.exports
    return nemoa.model.exports.save(*args, **kwargs)

def show(*args, **kwargs):
    """Show model as image."""
    import nemoa.model.exports
    return nemoa.model.exports.show(*args, **kwargs)
