# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.base
import importlib

def new(*args, **kwargs):
    """Return system instance."""

    if not kwargs:
        kwargs = {'config': {'type': 'base.System'}}

    if not 'config' in kwargs \
        or not 'type' in kwargs['config'] \
        or not len(kwargs['config']['type'].split('.')) == 2:
        return nemoa.log('error', """could not create system:
            configuration is not valid.""")

    stype = kwargs['config']['type']
    mname = 'nemoa.system.classes.' + stype.split('.')[0]
    cname = stype.split('.')[1]

    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
        system = getattr(module, cname)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create system:
            unknown system type '%s'.""" % stype) or None

    return system
