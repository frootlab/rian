# -*- coding: utf-8 -*-
"""Functions to access OS and platform informations."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.types import OptStr

def encoding() -> str:
    """Preferred encoding used for text data.

    This is a wrapper function to the standard library function
    `locale.getpreferredencoding()`_. This function returns the encoding used
    for text data, according to user preferences. User preferences are expressed
    differently on different systems, and might not be available
    programmatically on some systems, so this function only returns a guess.

    Returns:
        String representing the preferred encoding used for text data.

    .. _locale.getpreferredencoding():
       https://docs.python.org/3/library/locale.html#locale.getpreferredencoding

    """
    import locale
    return locale.getpreferredencoding()

def hostname() -> str:
    """Hostname of the computer.

    This is a wrapper function to the standard library function
    `platform.node()`_. This function returns the computer’s hostname. If the
    value cannot be determined, an empty string is returned.

    Returns:
        String representing the computer’s hostname or None.

    .. _platform.node():
        https://docs.python.org/3/library/platform.html#platform.node

    """
    import platform
    return platform.node()

def osname() -> str:
    """Name of the Operating System.

    This is a wrapper function to the standard library function
    `platform.system()`_. This function returns the OS name, e.g. 'Linux',
    'Windows', or 'Java'. If the value cannot be determined, an empty string is
    returned.

    Returns:
        String representing the OS name or None.

    .. _platform.system():
        https://docs.python.org/3/library/platform.html#platform.system

    """
    import platform
    return platform.system()

def ttylib() -> OptStr:
    """Name of package for tty I/O control.

    Depending on the plattform the module within the standard library, which is
    required for tty I/O control differs. The module `termios`_ provides an
    interface to the POSIX calls for tty I/O control. The module `msvcrt`_
    provides access to some useful capabilities on Windows platforms.

    Returns:
        Name of package for tty I/O control or None, if the package could not
        be determined.

    .. _termios: https://docs.python.org/3/library/termios.html
    .. _msvcrt: https://docs.python.org/3/library/msvcrt.html

    """
    from nemoa.common import nmodule

    libs = ['msvcrt', 'termios']
    for name in libs:
        if nmodule.inst(name):
            return name
    return None

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
