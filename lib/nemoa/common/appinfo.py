# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Optional, Union

def getvars(filepath = None):
    """Get all __VARIABLE__ from given file."""

    import io
    import re

    # get file content
    path = getpath(filepath)
    with io.open(path, encoding = 'utf8') as file_handler:
        content = file_handler.read()

    # parse variables with regular expressions
    key_regex = """__([a-zA-Z][a-zA-Z0-9]*)__"""
    val_regex = """['\"]([^'\"]*)['\"]"""
    regex = r"^[ ]*%s[ ]*=[ ]*%s" % (key_regex, val_regex)
    variables = {}
    for match in re.finditer(regex, content, re.M):
        key = str(match.group(1))
        val = str(match.group(2))
        variables[key] = val

    return variables

def path(key: str, appname: Optional[str] = None,
    appauthor: Optional[Union[str, bool]] = None,
    version: Optional[str] = None,
    **kwargs: Any) -> Optional[str]:
    """Path of application specific system directory.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage. This is a wrapper
    function to the package 'appdirs' [1].

    [1] http://github.com/ActiveState/appdirs

    Args:
        key (string): Environmental directory key. Allowed values are:
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

    """

    try: import appdirs
    except ImportError as e: raise ImportError(
        "nemoa.common.appinfo requires appdirs: "
        "http://github.com/ActiveState/appdirs") from e

    # todo get appname, appauthor and version from functions
    dkey = {'appname': appname or 'nemoa', 'appauthor': appauthor or 'Froot',
        'version': version}

    if key == 'user_cache_dir':
        return appdirs.user_cache_dir(**dkey, **kwargs)
    if key == 'user_config_dir':
        return appdirs.user_config_dir(**dkey, **kwargs)
    if key == 'user_data_dir':
        return appdirs.user_data_dir(**dkey, **kwargs)
    if key == 'user_log_dir':
        return appdirs.user_log_dir(**dkey, **kwargs)
    if key == 'site_config_dir':
        return appdirs.site_config_dir(**dkey, **kwargs)
    if key == 'site_data_dir':
        return appdirs.site_data_dir(**dkey, **kwargs)

    return None
