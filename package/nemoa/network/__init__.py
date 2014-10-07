# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.base
import nemoa.network.fileimport

def new(*args, **kwargs):
    """Return new network instance."""
    return nemoa.network.base.Network(*args, **kwargs)

def open(*args, **kwargs):
    obj_config = nemoa.network.fileimport.open(*args, **kwargs)
    if obj_config: return new(config = obj_config['config'])
    return None
