# -*- coding: utf-8 -*-
"""Collection of fequently used functions to access platform information."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

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
    import platform
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
    import platform
    return platform.system()

def username() -> str:
    """Login name of the current user.

    This is a wrapper function to the standard library function
    `getpass.getuser()`_. This function checks the environment variables
    LOGNAME, USER, LNAME and USERNAME, in order, and returns the value of the
    first one which is set to a non-empty string. If none are set, the login
    name from the password database is returned on systems which support the
    pwd module, otherwise, an exception is raised.

    Returns:
        String representing the login name of the current user.

    .. _getpass.getuser():
       https://docs.python.org/3/library/getpass.html#getpass.getuser

    """
    import getpass
    return getpass.getuser()

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
