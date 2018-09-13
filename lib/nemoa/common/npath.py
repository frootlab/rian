# -*- coding: utf-8 -*-
"""Collection of functions for platform independent filesystem operations."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Dict, Optional, Sequence, Union
from pathlib import Path

PathLike = Sequence[Union['PathLike', str, Path]]
PathLikeDict = Dict[str, PathLike]

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
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing valid path syntax.

    Examples:
        >>> join(('a', ('b', 'c')), 'd')
        'a\\b\\c\\d'

    """

    # flatten tree of strings to list and join list using os path seperators
    if len(args) == 0:
        return ''
    if len(args) == 1 and isinstance(args[0], (str, Path)):
        path = args[0]
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
        try:
            path = Path(*l)
        except Exception as e:
            raise ValueError("path like tree structure is invalid") from e
    if not path: return ''

    # normalize path
    path = str(Path(path))

    return path


def expand(*args: PathLike, udict: PathLikeDict = {}, expapp: bool = True,
    expenv: bool = True) -> str:
    """Iteratively expand path variables.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.
        udict: dictionary for user variables.
            Thereby the keys in the dictionary are encapsulated
            by the symbol '%'. The user variables may also include references.
        expapp: determines if application path variables are expanded.
            For a full list of valid application variables see
            'nemoa.common.nappinfo.path'. Default is True
        expenv: determines if environmental path variables are expanded.
            For a full list of valid environmental path variables see
            'nemoa.common.npath'. Default is True

    Returns:
        String containing valid path syntax.

    Examples:
        >>> expand('%var1%/c', 'd', udict = {'var1': 'a/%var2%', 'var2': 'b'})
        'a\\b\\c\\d'

    """

    import os
    import sys

    from nemoa.common import nappinfo

    path = Path(join(*args))

    # create dictionary with variables
    d = {}
    if udict:
        for key, val in udict.items(): d[key] = join(val)
    if expapp:
        for key, val in nappinfo.path().items(): d[key] = val
    if expenv:
        d['home'], d['cwd'] = home(), cwd()

    # itereratively expand variables in user dictionary
    update = True
    i = 0
    limit = sys.getrecursionlimit()
    while update:
        update = False
        for key, val in list(d.items()):
            if '%' + key + '%' not in str(path): continue
            try: path = Path(str(path).replace('%' + key + '%', val))
            except TypeError: del d[key]
            update = True
        i += 1
        if i > limit:
            raise RecursionError('cyclic dependency in variables detected')
        path = Path(path)

    # expand environmental paths
    if not expenv: return str(path)
    path = path.expanduser()
    path = os.path.expandvars(path)

    return str(path)

def dirname(*args: PathLike) -> str:
    """Extract directory name from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> dirname(('a', ('b', 'c'), 'd'), 'base.ext')
        'a\\b\\c\\d'

    """

    path = Path(expand(*args))
    if path.is_dir(): return str(path)
    return str(path.parent)

def filename(*args: PathLike) -> str:
    """Extract file name from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base.ext'

    """

    path = Path(expand(*args))
    if path.is_dir(): return ''
    return str(path.name)

def basename(*args: PathLike) -> str:
    """Extract file basename from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing basename of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base'

    """

    path = Path(expand(*args))
    if path.is_dir(): return ''
    return str(path.stem)

def fileext(*args: PathLike) -> str:
    """Fileextension of file.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing fileextension of file.

    Examples:
        >>> fileext(('a', ('b', 'c')), 'base.ext')
        'ext'

    """

    path = Path(expand(*args))
    if path.is_dir(): return ''
    return str(path.suffix).lstrip('.')

def cp(source: PathLike, target: PathLike) -> bool:
    """Copy sub directories from given source to destination directory.

    Args:
        source: Path like structure, which comprises the
            path of a source folder
        target: Path like structure, which comprises the
            path of a destination folder

    Returns:
        True if the operation was successful.

    """

    import shutil

    sdir, ddir = Path(expand(source)), Path(expand(target))

    for s in sdir.glob('*'):
        t = Path(ddir, basename(s))
        if t.exists(): shutil.rmtree(str(t))
        try: shutil.copytree(str(s), str(t))
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

    import os

    path = Path(expand(*args))
    if path.is_dir(): return True

    try: os.makedirs(path)
    except Exception as e:
        raise OSError("could not create directory") from e

    return path.is_dir()

def rmdir(*args: PathLike) -> bool:
    """Remove directory.

    Args:
        *args (PathLike): Path like structure, which identifies the path of
            a directory

    Returns:
        True if the directory could be deleted

    """

    import shutil

    path = Path(expand(*args))

    if not path.is_dir(): return False
    shutil.rmtree(str(path), ignore_errors = True)

    return not path.exists()
