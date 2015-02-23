# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.base

def open(*args, **kwargs):
    """Import and return workspace instance."""
    return nemoa.workspace.base.Workspace(*args, **kwargs)

