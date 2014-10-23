# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.classes.base
import importlib

def new(*args, **kwargs):
    """Return model instance."""

    if not kwargs:
        kwargs = {'config': {'type': 'base.Model'}}

    if not 'config' in kwargs \
        or not 'type' in kwargs['config'] \
        or not len(kwargs['config']['type'].split('.')) == 2:
        return nemoa.log('error', """could not create model:
            configuration is not valid.""")

    type = kwargs['config']['type']
    module_name = 'nemoa.model.classes.' + type.split('.')[0]
    class_name = type.split('.')[1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        model = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create model:
            unknown model type '%s'.""" % (type))

    return model
