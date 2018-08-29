# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.session.classes.base
import importlib

def new(*args, **kwargs):
    """Create new session instance."""

    if not kwargs: kwargs = {'config': {'type': 'base.Session'}}

    if len(kwargs.get('config', {}).get('type', '').split('.')) != 2:
        return nemoa.log('error', "configuration is not valid")

    type = kwargs['config']['type']
    module_name = 'nemoa.session.classes.' + type.split('.')[0]
    class_name = type.split('.')[1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        session = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not create session:
            unknown session type '%s'.""" % (type))

    return session
