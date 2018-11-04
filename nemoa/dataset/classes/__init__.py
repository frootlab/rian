# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.classes.base
import importlib

def new(*args, **kwds):
    """Create new dataset instance."""
    kwds = kwds or {'config': {'type': 'base.Dataset'}}

    # check validity of configuration
    if len(kwds.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid.")

    mname, cname = tuple(kwds['config']['type'].split('.'))

    try:
        module = importlib.import_module('nemoa.dataset.classes.' + mname)
        if not hasattr(module, cname): raise ImportError()
        dataset = getattr(module, cname)(**kwds)
    except ImportError:
        raise ValueError("""could not create dataset:
            unknown dataset type '%s'.""" % (type))

    return dataset
