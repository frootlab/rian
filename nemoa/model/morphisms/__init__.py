# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

def optimize(model, *args, **kwds):
    """Optimize model."""

    return new(model).optimize(*args, **kwds)

def new(model, *args, **kwds):
    """Get model transformation instance."""

    import importlib

    # get type of system
    stype = model.system.type
    mname = 'nemoa.model.morphisms.' + stype.split('.', 1)[0]
    cname = stype.rsplit('.', 1)[-1]

    # import module for transformation
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
    except ImportError:
        raise ValueError(
            "could not apply transformation: "
            "unknown system type '%s'." % stype)

    # create transformation instance and apply transformation to model
    return getattr(module, cname)(model)
