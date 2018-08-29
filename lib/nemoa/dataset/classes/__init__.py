# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.classes.base
import importlib

def new(*args, **kwargs):
    """Create new dataset instance."""

    if not kwargs: kwargs = {'config': {'type': 'base.Dataset'}}

    # check validity of configuration
    if len(kwargs.get('config', {}).get('type', '').split('.')) != 2:
        return nemoa.log('error', "configuration is not valid.")

    mname, cname = tuple(kwargs['config']['type'].split('.'))

    try:
        module = importlib.import_module('nemoa.dataset.classes.' + mname)
        if not hasattr(module, cname): raise ImportError()
        dataset = getattr(module, cname)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create dataset:
            unknown dataset type '%s'.""" % (type))

    return dataset
