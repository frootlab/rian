# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

def evaluate(model, *args, **kwds):
    """Evaluate model."""
    return new(model).evaluate(*args, **kwds)

def new(model, *args, **kwds):
    """Get model evaluation instance."""

    import importlib

    # get type of system
    stype = model.system.type
    mname = 'nemoa.model.evaluation.' + stype.split('.', 1)[0]
    cname = stype.rsplit('.', 1)[-1]

    # import module for evaluation
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname):
            raise ImportError()
    except ImportError:
        raise ValueError(
            "could not evaluate model: "
            "unknown system type '%s'." % stype)

    return getattr(module, cname)(model)
