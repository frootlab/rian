# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import platform

def systype():
    """."""
    return platform.system().lower()

def sysname():
    """."""
    return platform.node()
