# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import platform

def hostname() -> str:
    """Hostname of the system.

    Wrapper function to platform.node [1]

    Returns:
        Returns the computer’s hostname. If the value cannot be determined,
        an empty string is returned.

    References:
        [1] https://docs.python.org/3/library/platform.html

    """

    return platform.node()

def osname() -> str:
    """Name of the Operating System.

    Wrapper function to platform.system [1]
    [1] https://docs.python.org/3/library/platform.html

    Returns:
        Returns the OS name, e.g. 'Linux', 'Windows', or 'Java'. If the value
        cannot be determined, an empty string is returned.

    References:
        [1] https://docs.python.org/3/library/platform.html

    """

    return platform.system()
