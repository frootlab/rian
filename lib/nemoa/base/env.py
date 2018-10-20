# -*- coding: utf-8 -*-
"""Plattform, application and package specific informations.

.. References:
.. _PEP 345:
    https://www.python.org/dev/peps/pep-0345/
.. _RFC 822:
    https://www.w3.org/Protocols/rfc822/
.. _appdirs:
    http://github.com/ActiveState/appdirs
.. _termios:
    https://docs.python.org/3/library/termios.html
.. _msvcrt:
    https://docs.python.org/3/library/msvcrt.html
.. _locale.getpreferredencoding():
    https://docs.python.org/3/library/locale.html#locale.getpreferredencoding
.. _platform.node():
    https://docs.python.org/3/library/platform.html#platform.node
.. _platform.system():
    https://docs.python.org/3/library/platform.html#platform.system
.. _getpass.getuser():
    https://docs.python.org/3/library/getpass.html#getpass.getuser

.. TODO::
    * Add get_file for 'user_package_log', 'temp_log' etc.
    * include encoding, hostname etc. in get_var

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import getpass
import locale
import platform
import re

from distutils import sysconfig
from pathlib import Path

try:
    from appdirs import AppDirs
except ImportError as err:
    raise ImportError(
        "requires package appdirs: "
        "https://pypi.org/project/appdirs/") from err

from nemoa.base import nmodule
from nemoa.types import (
    Any, OptModule, OptStr, OptStrOrBool, OptPathLike, StrDict, StrDictOfPaths)

#
# Private Module Constants
#

_DEFAULT_APPNAME = 'nemoa'
_DEFAULT_APPAUTHOR = 'frootlab'

#
# Public Module Functions
#

def get_var(varname: str, *args: Any, **kwds: Any) -> OptStr:
    """Get application variable by name.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Therfore the variables are independent
    from runtime properties including user and session. For more information
    see `PEP 345`_.

    Args:
        name: Name of application variable. Typical variable names are:
            'name': The name of the distribution
            'version': A string containing the distribution's version number
            'status': Development status of the distributed application.
                Typical values are 'Prototype', 'Development', or 'Production'
            'description': A longer description of the distribution that can
                run to several paragraphs.
            'keywords': A list of additional keywords to be used to assist
                searching for the distribution in a larger catalog.
            'url': A string containing the URL for the distribution's
                homepage.
            'license': Text indicating the license covering the distribution
            'copyright': Notice of statutorily prescribed form that informs
                users of the distribution to published copyright ownership.
            'author': A string containing the author's name at a minimum;
                additional contact information may be provided.
            'email': A string containing the author's e-mail address. It can
                contain a name and e-mail address, as described in `[RFC822]`_.
            'maintainer': A string containing the maintainer's name at a
                minimum; additional contact information may be provided.
            'company': The company, which created or maintains the distribution.
            'organization': The organization, twhich created or maintains the
                distribution.
            'credits': list with strings, acknowledging further contributors,
                Teams or supporting organizations.
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.base.env.update_vars'.
        **kwds: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.base.env.update_vars'.

    Returns:
        String representing the value of the application variable.

    """
    # Check type of 'name'
    if not isinstance(varname, str):
        raise TypeError(
            "'name' requires to be of type 'str' or None"
            f", not '{type(varname).__name__}'")

    # Update variables if not present or if optional arguments are given
    if not '_vars' in globals() or args or kwds:
        update_vars(*args, **kwds)
    appvars = globals().get('_vars', {})

    return appvars.get(varname, None)

def get_vars(*args: Any, **kwds: Any) -> StrDict:
    """Get dictionary with application vaiables.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Therfore the variables are independent
    from runtime properties including user and session. For more information see
    `PEP 345`_.

    Args:
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.base.env.update_vars'.
        **kwds: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.base.env.update_vars'.

    Returns:
        Dictionary containing application variables.

    """
    # Update variables if not present or if optional arguments are given
    if not '_vars' in globals() or args or kwds:
        update_vars(*args, **kwds)
    return globals().get('_vars', {}).copy()

def update_vars(filepath: OptPathLike = None) -> None:
    """Update application variables from module attributes.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. The variables are independent from runtime
    properties like user and session. For more information see `PEP 345`_.

    Args:
        filepath: Valid filepath to python module, that contains the application
            variables as module attributes. By default the current top level
            module is used.

    Returns:
        Dictionary with application variables.

    """
    # By default use the current top level module
    filepath = filepath or nmodule.root().__file__

    # Parse content for module attributes with regular expressions
    rekey = "__([a-zA-Z][a-zA-Z0-9_]*)__"
    reval = r"['\"]([^'\"]*)['\"]"
    pattern = f"^[ ]*{rekey}[ ]*=[ ]*{reval}"
    text = Path(filepath).read_text()
    dvars = {}
    for match in re.finditer(pattern, text, re.M):
        dvars[str(match.group(1))] = str(match.group(2))

    # Set module name of current root module as default value for the
    # application variable 'name'
    dvars['name'] = dvars.get('name', nmodule.curname().split('.')[0])

    globals()['_vars'] = dvars

def get_dir(dirname: str, *args: Any, **kwds: Any) -> Path:
    """Get application specific environmental directory by name.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data storage.

    Args:
        dirname: Environmental directory name. Allowed values are:
            'user_cache_dir': Cache directory of user
            'user_config_dir': Configuration directory of user
            'user_data_dir': Data directory of user
            'user_log_dir': Logging directory of user
            'site_config_dir': Site global configuration directory
            'site_data_dir': Site global data directory
            'site_package_dir': Site global package directory
            'package_dir': Current package directory
            'package_data_dir': Current package data directory
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.base.env.update_dirs'.
        **kwds: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.base.env.update_dirs'.

    Returns:
        String containing path of environmental directory or None if the
        pathname is not supported.

    """
    # Check type of 'dirname'
    if not isinstance(dirname, str):
        raise TypeError(
            "'name' requires to be of type 'str' or None"
            f", not '{type(dirname).__name__}'")

    # Update appdirs if not present or if optional arguments are given
    if not '_dirs' in globals() or args or kwds:
        update_dirs(*args, **kwds)
    dirs = globals().get('_dirs', {})

    # Check value of 'dirname'
    if dirname not in dirs:
        raise ValueError(f"directory name '{dirname}' is not valid")

    return dirs[dirname]

def get_dirs(*args: Any, **kwds: Any) -> StrDict:
    """Get application specific environmental directories.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data storage.

    Args:
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.base.env.update_dirs'.
        **kwds: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.base.env.update_dirs'.

    Returns:
        Dictionary containing paths of application specific environmental
        directories.

    """
    # Update appdirs if not present or if optional arguments are given
    if not '_dirs' in globals() or args or kwds:
        update_dirs(*args, **kwds)
    return globals().get('_dirs', {}).copy()

def update_dirs(
        appname: OptStr = None, appauthor: OptStrOrBool = None,
        version: OptStr = None, **kwds: Any) -> None:
    """Update application specific directories from name, author and version.

    This function retrieves application specific directories from the package
    `appdirs`_. Additionally the directory 'site_package_dir' is retrieved fom
    the standard library package distutils and 'package_dir' and
    'package_data_dir' from the current top level module.

    Args:
        appname: is the name of application. If None, just the system directory
            is returned.
        appauthor: is the name of the appauthor or distributing body for this
            application. Typically it is the owning company name. You may pass
            False to disable it. Only applied in windows.
        version: is an optional version path element to append to the path.
            You might want to use this if you want multiple versions of your
            app to be able to run independently. If used, this would typically
            be "<major>.<minor>". Only applied when appname is present.
        **kwds: Optional directory name specific keyword arguments. For more
            information see `appdirs`_.

    Returns:
        Dictionary containing paths of application specific environmental
        directories.

    """
    dirs: StrDictOfPaths = {}
    appname = appname or get_var('name') or _DEFAULT_APPNAME
    appauthor = appauthor or get_var('author') or _DEFAULT_APPAUTHOR

    # Get application specific directories from appdirs
    appdirs = AppDirs(
        appname=appname, appauthor=appauthor, version=version, **kwds)
    dirnames = [
        'user_cache_dir', 'user_config_dir', 'user_data_dir',
        'user_log_dir', 'site_config_dir', 'site_data_dir']
    for dirname in dirnames:
        dirs[dirname] = Path(getattr(appdirs, dirname))

    # Get distribution specific directories from distutils
    path = Path(sysconfig.get_python_lib(), appname)
    dirs['site_package_dir'] = path

    # Get current package specific directories from top level module
    path = Path(nmodule.root().__file__).parent
    dirs['package_dir'] = path
    dirs['package_data_dir'] = path / 'data'

    globals()['_dirs'] = dirs

def encoding() -> str:
    """Preferred encoding used for text data.

    This is a wrapper function to the standard library function
    `locale.getpreferredencoding()`_. This function returns the encoding used
    for text data, according to user preferences. User preferences are expressed
    differently on different systems, and might not be available
    programmatically on some systems, so this function only returns a guess.

    Returns:
        String representing the preferred encoding used for text data.

    """
    return locale.getpreferredencoding()

def hostname() -> str:
    """Hostname of the computer.

    This is a wrapper function to the standard library function
    `platform.node()`_. This function returns the computer’s hostname. If the
    value cannot be determined, an empty string is returned.

    Returns:
        String representing the computer’s hostname or None.

    """
    return platform.node()

def osname() -> str:
    """Name of the Operating System.

    This is a wrapper function to the standard library function
    `platform.system()`_. This function returns the OS name, e.g. 'Linux',
    'Windows', or 'Java'. If the value cannot be determined, an empty string is
    returned.

    Returns:
        String representing the OS name or None.

    """
    return platform.system()

def ttylib() -> OptModule:
    """Name of package for tty I/O control.

    Depending on the plattform the module within the standard library, which is
    required for tty I/O control differs. The module `termios`_ provides an
    interface to the POSIX calls for tty I/O control. The module `msvcrt`_
    provides access to some useful capabilities on Windows platforms.

    Returns:
        Reference to module for tty I/O control or None, if the module could
        not be determined.

    """
    libs = ['msvcrt', 'termios']
    for name in libs:
        ref = nmodule.inst(name)
        if ref:
            return ref
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

    """
    return getpass.getuser()
