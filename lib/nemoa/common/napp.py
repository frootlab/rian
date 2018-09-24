# -*- coding: utf-8 -*-
"""Functions to access application variables and directories."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import cast
from nemoa.types import Any, OptStr, StrDict, OptStrOrBool
from nemoa.common import nmodule

def getvar(varname: str, *args: Any, **kwargs: Any) -> OptStr:
    """Get application variable by name.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Therfore the variables are independent
    from runtime properties including user and session. For more information
    see [PEP345].

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
                contain a name and e-mail address, as described in [RFC822].
            'maintainer': A string containing the maintainer's name at a
                minimum; additional contact information may be provided.
            'company': The company, which created or maintains the distribution.
            'organization': The organization, twhich created or maintains the
                distribution.
            'credits': list with strings, acknowledging further contributors,
                Teams or supporting organizations.
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.common.napp.updvars'.
        **kwargs: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.common.napp.updvars'.

    Returns:
        String representing the value of the application variable.

    References:
        [PEP345] https://www.python.org/dev/peps/pep-0345/
        [RFC822] https://www.w3.org/Protocols/rfc822/

    """
    # Check type of argument 'name'
    if not isinstance(varname, str):
        raise TypeError(
            "argument 'name' requires to be of type 'str' or None"
            f", not '{type(varname)}'")

    # Update variables if not present or if optional arguments are given
    if not '_VARS' in globals() or args or kwargs:
        updvars(*args, **kwargs)
    appvars = globals().get('_VARS', {})

    return appvars.get(varname, None)

def getvars(*args: Any, **kwargs: Any) -> StrDict:
    """Get dictionary with application vaiables.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Therfore the variables are independent
    from runtime properties including user and session. For more information
    see [PEP345].

    Args:
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.common.napp.updvars'.
        **kwargs: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.common.napp.updvars'.

    Returns:
        Dictionary containing application variables.

    References:
        [PEP345] https://www.python.org/dev/peps/pep-0345/

    """
    # update variables if not present or if optional arguments are given
    if not '_VARS' in globals() or args or kwargs:
        updvars(*args, **kwargs)
    return globals().get('_VARS', {}).copy()

def updvars(filepath: OptStr = None) -> None:
    """Update application variables from module attributes.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Therfore the variables are independent
    from runtime properties including user and session. For more information
    see [PEP345].

    Args:
        filepath: Valid path to python module or package, which comprises the
            application variables as module variables in the format '__var__'

    Returns:
        Dictionary with application variables.

    References:
        [PEP345] https://www.python.org/dev/peps/pep-0345/

    """
    import io
    import re

    dvars = {}

    # Use init script of current root module
    if filepath is None:
        mname = nmodule.curname().split('.')[0]
        module = nmodule.inst(mname)
        filepath = getattr(module, '__file__', None)

    # Read file content
    with io.open(cast(str, filepath), encoding='utf8') as file:
        content = file.read()

    # Parse content for module variables with regular expressions
    rkey = "__([a-zA-Z][a-zA-Z0-9]*)__"
    rval = """['\"]([^'\"]*)['\"]"""
    rexp = r"^[ ]*%s[ ]*=[ ]*%s" % (rkey, rval)
    for match in re.finditer(rexp, content, re.M):
        dvars[str(match.group(1))] = str(match.group(2))

    # Set module name of current root module as default value for the
    # application variable 'name'
    dvars['name'] = dvars.get('name', nmodule.curname().split('.')[0])

    globals()['_VARS'] = dvars

def getdir(dirname: str, *args: Any, **kwargs: Any) -> str:
    """Get application specific environmental directory.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data storage.

    Args:
        dirname: Environmental directory name. Allowed values are:
            'user_cache_dir': Cache directory of user
            'user_config_dir': Configuration directory of user
            'user_data_dir': Data directory of user
            'user_log_dir': Logging directory of user
            'site_config_dir': Site specific configuration directory
            'site_data_dir': Site specific data directory
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.common.napp.upddirs'.
        **kwargs: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.common.napp.upddirs'.

    Returns:
        String containing path of environmental directory or None if
        the pathname is not supported.

    """
    # Check type of argument 'dirname'
    if not isinstance(dirname, str):
        raise TypeError(
            "argument 'name' requires to be of type 'str' or None"
            f", not '{type(dirname)}'")

    # Update appdirs if not present or if optional arguments are given
    if not '_DIRS' in globals() or args or kwargs:
        upddirs(*args, **kwargs)
    dirs = globals().get('_DIRS', {})

    # Check value of argument 'dirname'
    if dirname not in dirs:
        raise ValueError(f"directory name '{dirname}' is not valid")

    return dirs[dirname]

def getdirs(*args: Any, **kwargs: Any) -> StrDict:
    """Get application specific environmental directories.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data storage.

    Args:
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.common.napp.upddirs'.
        **kwargs: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.common.napp.upddirs'.

    Returns:
        Dictionary containing paths of application specific environmental
        directories.

    """
    # Update appdirs if not present or if optional arguments are given
    if not '_DIRS' in globals() or args or kwargs:
        upddirs(*args, **kwargs)
    return globals().get('_DIRS', {}).copy()

def upddirs(
        appname: OptStr = None, appauthor: OptStrOrBool = None,
        version: OptStr = None, **kwargs: Any) -> None:
    """Update application specific directories from name, author and version.

    This is a wrapper function to the package 'appdirs' [1].

    Args:
        appname: is the name of application.
            If None, just the system directory is returned.
        appauthor: is the name of the appauthor or distributing body for this
            application. Typically it is the owning company name. You may pass
            False to disable it. Only applied in windows.
        version: is an optional version path element to append to the path.
            You might want to use this if you want multiple versions of your
            app to be able to run independently. If used, this would typically
            be "<major>.<minor>". Only applied when appname is present.
        **kwargs: Optional keyword arguments for the respective directory name.
            For more information see [1].

    Returns:
        Dictionary containing paths of application specific environmental
        directories.

    References:
        [1] http://github.com/ActiveState/appdirs

    """
    try:
        import appdirs
    except ImportError as err:
        raise ImportError(
            "requires package appdirs: "
            "https://pypi.org/project/appdirs/") from err

    dirs = appdirs.AppDirs(
        appname=appname or getvar('name'),
        appauthor=(appauthor or getvar('company')
            or getvar('organization') or getvar('author')),
        version=version, **kwargs)
    keys = [
        'user_cache_dir', 'user_config_dir', 'user_data_dir',
        'user_log_dir', 'site_config_dir', 'site_data_dir']

    globals()['_DIRS'] = {key: getattr(dirs, key) for key in keys}
