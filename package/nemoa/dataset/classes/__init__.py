# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.classes.base
import importlib

def new(*args, **kwargs):
    """Create new dataset instance."""

    if not kwargs:
        kwargs = {'config': {'type': 'base.Dataset'}}

    if not 'config' in kwargs \
        or not 'type' in kwargs['config'] \
        or not len(kwargs['config']['type'].split('.')) == 2:
        return nemoa.log('error', """could not create dataset:
            configuration is not valid.""")

    type = kwargs['config']['type']
    module_name = 'nemoa.dataset.classes.' + type.split('.')[0]
    class_name = type.split('.')[1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        dataset = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create dataset:
            unknown dataset type '%s'.""" % (type))

    return dataset
