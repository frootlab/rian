# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.classes.base
import importlib

def new(*args, **kwargs):
    """Create new network instance."""

    if not 'config' in kwargs \
        or not 'type' in kwargs['config'] \
        or not len(kwargs['config']['type'].split('.')) == 2:
        return nemoa.log('error', """could not create network:
            configuration is not valid.""")

    type = kwargs['config']['type']
    module_name = 'nemoa.network.classes.' + type.split('.')[0]
    class_name = type.split('.')[1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        network = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create network:
            unknown network type '%s'.""" % (type))

    return network
