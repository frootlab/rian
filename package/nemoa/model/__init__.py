# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.base

def new(*args, **kwargs):
    """Return new model instance."""
    return nemoa.model.base.model(*args, **kwargs)
