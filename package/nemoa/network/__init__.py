# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.base
import nemoa.network.importer

def new(*args, **kwargs):
    """Return new network instance."""
    return nemoa.network.base.Network(*args, **kwargs)

def open(*args, **kwargs):
    obj_config = nemoa.network.importer.open(*args, **kwargs)
    return new(config = obj_config['config'])
