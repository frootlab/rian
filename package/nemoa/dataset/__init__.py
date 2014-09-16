# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.annotation
import nemoa.dataset.base

def new(*args, **kwargs):
    """Return new dataset instance."""
    return nemoa.dataset.base.dataset(*args, **kwargs)
