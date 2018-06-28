# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def algorithms():
    from nemoa.common.module import getsubmodules, getmodule, getfunctions
    flist = []
    for mname in getsubmodules():
        minst = getmodule(mname)
        flist = getfunctions(minst)
    print(mlist)

    return True

def evaluate(model, *args, **kwargs):
    """Evaluate model."""
    return new(model).evaluate(*args, **kwargs)

def new(model, *args, **kwargs):
    """Get model evaluation instance."""

    import importlib

    # get type of system
    stype = model.system.type
    mname = 'nemoa.model.evaluation.' + stype.split('.')[0]
    cname = stype.split('.')[1]

    print('hi! - this is model.evaluation.__init__')

    # import module for evaluation
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
    except ImportError:
        return nemoa.log('error',
            "could not evaluate model: "
            "unknown system type '%s'." % stype)

    return getattr(module, cname)(model)
