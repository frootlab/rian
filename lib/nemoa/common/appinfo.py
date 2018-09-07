# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Optional, Union

def get(name: Optional['str'] = None,
    path: Optional['str'] = None) -> Optional[Union[dict, str]]:
    """Get application variable by name.

    Application variables are intended to describe the application distribution
    by authorship information, bibliographic information, status, formal
    conditions and notes or warnings. Consequently the variables are independent
    from runtime properties including user and session. For more information
    see [PEP345].

    Args:
        name: Name of application variable. Typical variable names are:
            'name' -- The name of the distribution
            'version' -- A string containing the distribution's version number
            'status' -- Development status of the distributed application.
                Typical values are 'Prototype', 'Development', or 'Production'
            'description' -- A longer description of the distribution that can
                run to several paragraphs.
            'keywords' -- A list of additional keywords to be used to assist
                searching for the distribution in a larger catalog.
            'url' -- A string containing the URL for the distribution's
                home page
            'license' -- Text indicating the license covering the distribution
            'copyright' -- Notice of statutorily prescribed form that informs
                users of the distribution to published copyright ownership.
            'author' -- A string containing the author's name at a minimum;
                additional contact information may be provided.
            'email' -- A string containing the author's e-mail address. It can
                contain a name and e-mail address, as described in [RFC822]
            'maintainer' -- A string containing the maintainer's name at a
                minimum; additional contact information may be provided.
            'company' -- The company, that created or maintains the
                distribution.
            'organization' -- The organization, that created or maintains the
                distribution.
            'credits' -- list with strings, acknowledging further contributors,
                Teams or supporting organizations
        path: Valid path to python module, which comprises


    Returns:
        String representing the value of the application variable.

    References:
        [PEP345] https://www.python.org/dev/peps/pep-0345/
        [RFC822] https://www.w3.org/Protocols/rfc822/

    """

    def updatevars(path: Optional['str'] = None) -> None:
        """Update application variables from module attributes."""

        if not path:

            # use init script of current root module
            from nemoa.common import module
            name = module.curname().split('.')[0]
            path = module.get_module(name).__file__

        # read file content
        import io
        with io.open(path, encoding = 'utf8') as f: content = f.read()

        # parse content for module variables with regular expressions
        import re
        rkey = """__([a-zA-Z][a-zA-Z0-9]*)__"""
        rval = """['\"]([^'\"]*)['\"]"""
        rexp = r"^[ ]*%s[ ]*=[ ]*%s" % (rkey, rval)
        dvars = {}
        for match in re.finditer(rexp, content, re.M):
            dvars[str(match.group(1))] = str(match.group(2))

        # supplement missing entries
        if not 'name' in dvars:

            # use name of current root module
            from nemoa.common import module
            dvars['name'] = module.curname().split('.')[0]

        globals()['_VARS'] = dvars

    # update variables if not present or path is given
    if '_VARS' not in globals() or path: updatevars(path = path)

    d = globals()['_VARS']
    if not name: return d.copy()
    if not isinstance(name, str):
        raise TypeError(
            "argument 'name' requires types 'str' or 'None', "
            f"not '{type(name)}'")

    return d.get(name, None)

def path(name: Optional[str] = None, appname: Optional[str] = None,
    appauthor: Optional[Union[str, bool]] = None,
    version: Optional[str] = None,
    **kwargs: Any) -> Optional[Union[dict, str]]:
    """Get application specific paths for caching, configuration etc.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data. This is a wrapper function to
    the package 'appdirs' [1].

    Args:
        name: Environmental directory name. Allowed values are:
            'user_cache_dir' -- Cache directory of user
            'user_config_dir' -- Configuration directory of user
            'user_data_dir' -- Data directory of user
            'user_log_dir' -- Logging directory of user
            'site_config_dir' -- Site specific configuration directory
            'site_data_dir' -- Site specific data directory
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
        String containing path of environmental directory or None if
        the pathname is not supported.

    References:
        [1] http://github.com/ActiveState/appdirs

    """

    def upddirs(appname: Optional[str] = None,
        appauthor: Optional[Union[str, bool]] = None,
        version: Optional[str] = None, **kwargs: Any) -> None:
        """Update application paths from name, author and version."""

        try: from appdirs import AppDirs
        except ImportError as e:
            raise ImportError(
                "requires package appdirs: "
                "https://pypi.org/project/appdirs/") from e

        app = {
            'appname': appname or get('name'),
            'appauthor': appauthor or get('company') \
                or get('organization') or get('author'),
            'version': version
        }

        Paths = AppDirs(**app, **kwargs)
        d = {}
        keys = ['user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        for key in keys: d[key] = getattr(Paths, key)

        globals()['_DIRS'] = d

    if '_DIRS' not in globals():
        upddirs(appname = appname, appauthor = appauthor, version = version,
            **kwargs)
    d = globals()['_DIRS']
    if not name: return d.copy()
    if not isinstance(name, str):
        raise TypeError("argument 'name' requires types 'str' or 'None', "
            f"not '{type(name)}'")
    if not name in d:
        raise KeyError(f"pathname '{name}' is not valid")

    return d[name]
