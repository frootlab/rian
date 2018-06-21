# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def optimize(model, *args, **kwargs):
    """Optimize model."""

    return new(model).optimize(*args, **kwargs)

def new(model, *args, **kwargs):
    """Get model transformation instance."""

    import importlib

    # get type of system
    stype = model.system.type
    mname = 'nemoa.model.morphisms.' + stype.split('.')[0]
    cname = stype.split('.')[1]

    # import module for transformation
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
    except ImportError:
        return nemoa.log('error',
            "could not apply transformation: "
            "unknown system type '%s'." % stype)

    # create transformation instance and apply transformation to model
    return getattr(module, cname)(model)
