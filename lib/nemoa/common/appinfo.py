# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Optional, Union

def get(key: Optional['str'] = None,
    path: Optional['str'] = None) -> Union[dict, str]:
    """Get named application variable."""

    if not 'vars' in globals(): _update_vars(path = path)

    d = globals()['vars']
    if not key: return d.copy()
    if not isinstance(key, str):
        raise TypeError(
            "argument 'key' requires types 'str' or 'None', "
            f"not '{type(key)}'")
    if not key in d:
        raise KeyError(f"key '{key}' is not valid")

    return d[key]

def _update_vars(path: Optional['str'] = None) -> bool:
    """Update application variable from given file."""

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

    globals()['vars'] = dvars

    return True

def path(key: Optional[str] = None, appname: Optional[str] = None,
    appauthor: Optional[Union[str, bool]] = None,
    version: Optional[str] = None,
    **kwargs: Any) -> Optional[Union[dict, str]]:
    """Get named application path.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data. This is a wrapper function to
    the package 'appdirs' [1].

    Args:
        key (str or None, optional): Environmental directory key.
            Allowed values are:
                'user_cache_dir' -- Cache directory of user
                'user_config_dir' -- Configuration directory of user
                'user_data_dir' -- Data directory of user
                'user_log_dir' -- Logging directory of user
                'site_config_dir' -- Site specific configuration directory
                'site_data_dir' -- Site specific data directory
        appname (str, optional): is the name of application.
            If None, just the system directory is returned.
        appauthor (str, optional): is the name of the appauthor or distributing
            body for this application. Typically it is the owning company name.
            You may pass False to disable it. Only applied in windows.
        version (str, optional): is an optional version path element to append
            to the path. You might want to use this if you want multiple
            versions of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        **kwargs (Any, optional): Optional additional keyword arguments,
            that depend on the given key. For more information see [1].

    Returns:
        String containing path of environmental directory or None if
        the key is not supported.

    References:
        [1] http://github.com/ActiveState/appdirs

    """

    if not 'dirs' in globals():
        _update_dirs(appname = appname, appauthor = appauthor,
            version = version, **kwargs)
    d = globals()['dirs']
    if not key: return d.copy()
    if not isinstance(key, str):
        raise TypeError(
            "argument 'key' requires types 'str' or 'None', "
            f"not '{type(key)}'")
    if not key in d:
        raise KeyError(f"key '{key}' is not valid")

    return d[key]

def _update_dirs(appname: Optional[str] = None,
    appauthor: Optional[Union[str, bool]] = None, version: Optional[str] = None,
    **kwargs: Any) -> bool:
    """ """

    try:
        from appdirs import AppDirs
    except ImportError as E:
        raise ImportError(
            "requires package appdirs: "
            "https://pypi.org/project/appdirs/") from E

    app = {
        'appname': appname or get('name'),
        'appauthor': appauthor or get('company') or get('author'),
        'version': version
    }

    Paths = AppDirs(**app, **kwargs)
    d = {}
    keys = ['user_cache_dir', 'user_config_dir', 'user_data_dir',
        'user_log_dir', 'site_config_dir', 'site_data_dir']
    for key in keys: d[key] = getattr(Paths, key)

    globals()['dirs'] = d

    return True
