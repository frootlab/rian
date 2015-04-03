# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa

def optimize(model, *args, **kwargs):
    """Optimize model."""

    # get type of system
    stype = model.system.type
    mname = 'nemoa.model.optimizer.' + stype.split('.')[0]
    cname = stype.split('.')[1]

    # import module for optimizer module
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not create optimizer:
            unknown system type '%s'.""" % stype)

    # create optimizer instance
    optimizer = getattr(module, cname)(model)

    # run optimizer
    return optimizer.optimize(*args, **kwargs)
