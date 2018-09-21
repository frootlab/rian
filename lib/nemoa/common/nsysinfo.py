# -*- coding: utf-8 -*-
"""Collection of fequently used functions to access platform information."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import platform

from nemoa.types import OptStr

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

    Returns:
        Returns the OS name, e.g. 'Linux', 'Windows', or 'Java'. If the value
        cannot be determined, an empty string is returned.

    References:
        [1] https://docs.python.org/3/library/platform.html

    """
    return platform.system()

def ttylib() -> OptStr:
    """Name of package for tty I/O control.

    Returns:
        Name of package for tty I/O control or None, if the package could not
        be determined.

    References:
        [1] https://docs.python.org/3/library/termios.html
        [2] https://docs.python.org/3/library/msvcrt.html

    """
    from nemoa.common import nmodule

    libs = ['msvcrt', 'termios']
    for name in libs:
        if nmodule.inst(name):
            return name

    return None
