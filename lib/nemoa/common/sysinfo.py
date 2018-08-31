# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import platform

def hostname():
    """Hostname of system."""
    return platform.node()

def osname():
    """Name of OS of system."""
    return platform.system()
