# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.base

def new(*args, **kwargs):
    """Return new network instance."""
    return nemoa.network.base.network(*args, **kwargs)
