# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import os

from pathlib import Path

from typing import Dict, Optional, Union

PathLike = Union['PathLike', tuple, list, str]
PathLikeDict = Dict[str, PathLike]

#
# Path Information
#

def cwd() -> str:
    """Path of current working directory.

    Returns:
        String containing path of current working directory.

    """

    return str(Path.cwd())

def home() -> str:
    """Path of current users home directory.

    Returns:
        String containing path of home directory.

    """

    return str(Path.home())

def clear(fname: str) -> str:
    """Clear filename from invalid characters.

    Args:
        fname (str):

    Returns:
        String containing valid path syntax.

    Examples:
        >>> clear('3/\nE{$5}.e')
        '3E5.e'

    """

    import string

    valid = "-_.() " + string.ascii_letters + string.digits
    fname = ''.join(c for c in fname if c in valid).replace(' ', '_')

    return fname

def join(*args: PathLike) -> str:
    """Join and normalize path like structure.

    Args:
        *args (PathLike): Path like structure, which is given by a tree of
            strings, which can be joined to a path.

    Returns:
        String containing valid path syntax.

    Examples:
        >>> join(('a', ('b', 'c')), 'd')
        'a\\b\\c\\d'

    """

    # flatten tree of strings to list and join list using os path seperators
    if len(args) == 0: return ''
    if len(args) == 1 and isinstance(args[0], str): path = args[0]
    else:
        l = list(args)
        i = 0
        while i < len(l):
            while isinstance(l[i], (list, tuple)):
                if not l[i]:
                    l.pop(i)
                    i -= 1
                    break
                else: l[i:i + 1] = l[i]
            i += 1
        try: path = os.path.sep.join(list(l))
        except Exception as e:
            raise ValueError("Path like tree structure is not valid") from e
    if not path: return ''

    # normalize path
    path = str(Path(path))

    return path

def expand(*args: PathLike, udict: PathLikeDict = {}, expapp: bool = True,
    expenv: bool = True) -> str:
    """Iteratively expand path variables.

    Args:
        *args (PathLike): Path like structure, which is given by a tree of
            strings, which can be joined to a path.
        udict (PathLikeDict, optional): dictionary for user variables.
            Thereby the keys in the dictionary are encapsulated
            by the symbol '%'. The user variables may also include references.
        expapp (bool, optional): determines if application path variables are
            expanded. For a full list of valid application variables see
            'nemoa.common.appinfo.path'. Default is True
        expenv (bool, optional): determines if environmental path variables are
            expanded. For a full list of valid environmental path variables see
            'nemoa.common.ospath'. Default is True

    Returns:
        String containing valid path syntax.

    Examples:
        >>> expand('%var1%/c', 'd', udict = {'var1': 'a/%var2%', 'var2': 'b'})
        'a\\b\\c\\d'

     """

    import sys

    from nemoa.common import appinfo

    path = join(*args)

    # create dictionary with variables
    d = udict.copy()
    for key, val in d.items(): d[key] = join(val)
    if expapp:
        for key in ['user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'home', 'cwd', 'site_config_dir', 'site_data_dir']:
            d[key] = appinfo.path(key)
    if expenv:
        d['home'] = home()
        d['cwd'] = cwd()

    # itereratively expand variables in user dictionary
    update = True
    i = 0
    limit = sys.getrecursionlimit()
    while update:
        update = False
        for key, val in list(d.items()):
            if '%' + key + '%' not in path: continue
            try: path = path.replace('%' + key + '%', val)
            except TypeError: del d[key]
            update = True
        i += 1
        if i > limit:
            raise RecursionError('cyclic dependency in variables detected')
        path = os.path.normpath(path)

    # expand environmental paths
    if not expenv: return path
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    return path

def dirname(*args: PathLike) -> str:
    """Extract directory name from a path like structure.

    Args:
        *args (PathLike): Path like structure, given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> dirname(('a', ('b', 'c'), 'd'), 'base.ext')
        'a\\b\\c\\d'

    """

    path = expand(*args)

    if os.path.isdir(path): return path
    name = os.path.dirname(path)

    return name

def filename(*args: PathLike) -> str:
    """Extract file name from a path like structure.

    Args:
        *args (PathLike): Path like structure, given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base.ext'

    """

    path = expand(*args)

    if os.path.isdir(path): return ''
    name = os.path.basename(path)

    return name

def basename(*args: PathLike) -> str:
    """Extract file basename from a path like structure.

    Args:
        *args (PathLike): Path like structure, given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing basename of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base'

    """

    path = expand(*args)

    if os.path.isdir(path): return ''
    name = os.path.basename(path)
    base = os.path.splitext(name)[0].rstrip('.')

    return base

def fileext(*args: PathLike) -> str:
    """Fileextension of file.

    Args:
        *args (PathLike): Path like structure, given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing fileextension of file.

    Examples:
        >>> fileext(('a', ('b', 'c')), 'base.ext')
        'ext'

    """

    path = expand(*args)

    if os.path.isdir(path): return ''
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lstrip('.')

    return ext

#
# File operations
#

def cp(source: PathLike, target: PathLike) -> bool:
    """Copy sub directories from given source to destination directory.

    Args:
        source (PathLike): Path like structure, which comprises the
            path of a source folder
        target (PathLike): Path like structure, which comprises the
            path of a destination folder

    Returns:
        True if the operation was successful.

    """

    import glob
    import shutil

    sdir, ddir = expand(source), expand(target)

    for s in glob.glob(os.path.join(sdir, '*')):
        t = os.path.join(ddir, basename(s))
        if os.path.exists(t): shutil.rmtree(t)
        try: shutil.copytree(s, t)
        except Exception as e:
            raise OSError("could not copy directory") from e

    return True

def mkdir(*args: PathLike) -> bool:
    """Create directory.

    Args:
        *args (PathLike): Path like structure, which comprises the path of
            a new directory

    Returns:
        True if the directory already exists, or the operation was successful.

    """

    path = expand(*args)
    if os.path.isdir(path): return True

    try: os.makedirs(path)
    except Exception as e:
        raise OSError("could not create directory") from e

    return os.path.isdir(path)

def rmdir(*args: PathLike) -> bool:
    """Remove directory.

    Args:
        *args (PathLike): Path like structure, which identifies the path of
            a directory

    Returns:
        True if the directory could be deleted

    """

    import shutil

    path = expand(*args)

    if not os.path.isdir(path): return False
    shutil.rmtree(path, ignore_errors = True)

    return not os.path.isdir(path)
