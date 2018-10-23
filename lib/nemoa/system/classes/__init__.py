# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.base
import importlib

def new(*args, **kwds):
    """Return system instance."""

    if not kwds: kwds = {'config': {'type': 'base.System'}}

    if len(kwds.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid")

    stype = kwds['config']['type']
    mname = 'nemoa.system.classes.' + stype.split('.', 1)[0]
    cname = stype.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
        system = getattr(module, cname)(**kwds)
    except ImportError:
        raise ValueError("""could not create system:
            unknown system type '%s'.""" % stype) or None

    return system
