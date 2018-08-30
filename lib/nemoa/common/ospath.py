# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import os

from typing import Optional, Union, Any

TreeOfStr = Union['TreeOfStr', tuple, list, str]

def basename(path: str) -> str:
    """Base of filename without filextension.

    Args:
        path (string): path of file

    Returns:
        String containing basename of file.

    """

    fname = os.path.basename(normpath(path))
    fbase = os.path.splitext(fname)[0].rstrip('.')

    return fbase

def copytree(sdir: str, ttdir: str) -> bool:
    """Copy sub directories from given source directory to target directory.

    Args:
        sdir (string): path of source directory
        tdir (string): path of target directory

    Returns:
        True if the operation was successful.

    """

    import glob
    import shutil

    for s in glob.glob(os.path.join(sdirc, '*')):
        t = os.path.join(tdir, basename(s))
        if os.path.exists(t): shutil.rmtree(t)
        try: shutil.copytree(s, t)
        except Exception as e:
            raise OSError("Could not copy directory")

    return True


def dirname(path: str) -> str:
    """Get directory path of file or directory.

    Args:
        path (string): path to file or directory

    Returns:
        String containing normalized directory path of file.

    """

    return os.path.dirname(normpath(path))

def fileext(path: str) -> str:
    """Fileextension of file.

    Args:
        path (string): path of file

    Returns:
        String containing fileextension of file.

    """

    fname = os.path.basename(normpath(path))
    fext = os.path.splitext(fname)[1].lstrip('.')

    return fext

def cwd() -> str:
    """Path of current working directory.

    Returns:
        String containing path of current working directory.

    """

    return os.getcwd() + os.path.sep

def home() -> str:
    """Path of current users home directory.

    Returns:
        String containing path of home directory.

    """

    return os.path.expanduser('~')

def get(key: str, appname: Optional[str] = None,
    appauthor: Optional[Union[str, bool]] = None, version: Optional[str] = None,
    **kwargs: Any) -> Optional[str]:
    """Path of an environmental directory.

    This function returns environmental directories by platform independent
    keys to allow platform independent storage. This is a wrapper function to
    the module 'appdirs' [1].

    [1] http://github.com/ActiveState/appdirs

    Args:
        key (string): Environmental directory key name. Allowed values are:
            'user_cache_dir' -- Cache directory of user
            'user_config_dir' -- Configuration directory of user
            'user_data_dir' -- Data directory of user
            'user_log_dir' -- Logging directory of user
            'user_home' -- Home directory of user
            'user_cwd' -- Current working directory of user
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

    import appdirs

    dkey = {'appname': appname, 'appauthor': appauthor, 'version': version}

    if key == 'user_cache_dir': return appdirs.user_cache_dir(**dkey, **kwargs)
    if key == 'user_config_dir':
        return appdirs.user_config_dir(**dkey, **kwargs)
    if key == 'user_data_dir': return appdirs.user_data_dir(**dkey, **kwargs)
    if key == 'user_log_dir': return appdirs.user_log_dir(**dkey, **kwargs)
    if key == 'user_cwd': return cwd()
    if key == 'user_home': return home()
    if key == 'site_config_dir':
        return appdirs.site_config_dir(**dkey, **kwargs)
    if key == 'site_data_dir':
        return appdirs.site_data_dir(**dkey, **kwargs)

    return None

def clean(fname: str) -> str:
    """Get cleaned filename."""

    import string

    valid = "-_.() " + string.ascii_letters + string.digits
    fname = ''.join(c for c in fname if c in valid).replace(' ', '_')

    return fname

def joinpath(*args: TreeOfStr) -> Optional[str]:
    """Join path.

    Args:
        *args (TreeOfStr): Tree of strings which can be joined to a path.

    Returns:
        String containing valid path.

    Examples:
        >>> joinpath('%user_config_dir%', 'nemoa.ini')
        [0, 1, 2, 3]

    """

    # flatten tuple of tuples etc. to flat path list
    # and join list using os path seperators
    path = args
    if isinstance(path, (list, tuple)):
        path = list(path)
        i = 0
        while i < len(path):
            while isinstance(path[i], (list, tuple)):
                if not path[i]:
                    path.pop(i)
                    i -= 1
                    break
                else: path[i:i + 1] = path[i]
            i += 1
        try:
            path = os.path.sep.join(list(path))
        except Exception as e:
            raise ValueError("argument 'path' is not valid")

    return path

def normpath(*args: TreeOfStr) -> str:
    """Get normalized path.

    Args:
        *args (TreeOfStr): Tree of strings which can be joined to a path.

    Returns:
        String containing normalized path.

    """

    path = joinpath(*args)
    if not path: return ''

    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)

    return path
