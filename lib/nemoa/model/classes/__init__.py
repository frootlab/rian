# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.classes.base
import importlib

def new(*args, **kwds):
    """Return model instance."""

    type = kwds.get('config', {}).get('type', 'base.Model')
    module_name = 'nemoa.model.classes.' + type.split('.', 1)[0]
    class_name = type.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        model = getattr(module, class_name)(**kwds)
    except ImportError:
        raise ValueError("""could not create model:
            unknown model type '%s'.""" % (type))

    return model
