# -*- coding: utf-8 -*-
"""Collection of functions for platform independent filesystem operations.

.. References:
.. _pathlib:
    https://docs.python.org/3/library/pathlib.html
.. _Path.is_file():
    https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_file
.. _Path.is_dir():
    https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_dir

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import fnmatch
import os

from pathlib import Path, PurePath
from nemoa.types import (
    Any, Iterable, IterAny, NestPath, OptStrDict, PathLike, PathLikeList)

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
    r"""Clear filename from invalid characters.

    Args:
        fname: Arbitrary string, which is be cleared from invalid filename
            characters.

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

def match(paths: PathLikeList, pattern: str) -> PathLikeList:
    """Filter pathlist to matches with wildcard pattern.

    Args:
        paths: List of paths, which is filtered to matches with pattern.
        pattern: String pattern, containing Unix shell-style wildcards:
            '*': matches arbitrary strings
            '?': matches single characters
            [seq]: matches any character in seq
            [!seq]: matches any character not in seq

    Returns:
        Filtered list of paths.

    Examples:
        >>> match([Path('a.b'), Path('b.a')], '*.b')
        [Path('a.b')]

    """
    # Normalize path and pattern representation using POSIX standard
    mapping = {PurePath(path).as_posix(): path for path in paths}
    pattern = PurePath(pattern).as_posix()
    # Match normalized paths with normalized pattern
    names = list(mapping.keys())
    matches = fnmatch.filter(names, pattern)
    # Return original paths
    return [mapping[name] for name in matches]

def join(*args: NestPath) -> Path:
    r"""Join nested iterable path-like structure to single path object.

    Args:
        *args: Arguments containing nested iterable paths of strings and
            PathLike objects.

    Returns:
        Single Path comprising all arguments.

    Examples:
        >>> join(('a', ('b', 'c')), 'd')
        Path('a\\b\\c\\d')

    """
    # Generate flat structure
    def flatten(tower: Any) -> IterAny:
        for token in tower:
            if not isinstance(token, Iterable):
                yield token
            elif isinstance(token, str):
                yield token
            else:
                yield from flatten(token)
    flat = [token for token in flatten(args)]

    # Create path from flat structure
    try:
        path = Path(*flat)
    except TypeError as err:
        raise TypeError(
            "the tokens of nested paths require to be of types "
            "str, bytes or pathlike") from err

    return path

def expand(
        *args: NestPath, udict: OptStrDict = None, expapp: bool = True,
        expenv: bool = True) -> str:
    r"""Expand path variables.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.
        udict: dictionary for user variables.
            Thereby the keys in the dictionary are encapsulated
            by the symbol '%'. The user variables may also include references.
        expapp: determines if application specific environmental
            directories are expanded. For a full list of valid application
            variables see
            'nemoa.core.napp.get_dir'. Default is True
        expenv: determines if environmental path variables are expanded.
            For a full list of valid environmental path variables see
            'nemoa.core.npath'. Default is True

    Returns:
        String containing valid path syntax.

    Examples:
        >>> expand('%var1%/c', 'd', udict = {'var1': 'a/%var2%', 'var2': 'b'})
        'a\\b\\c\\d'

    """
    import sys

    from nemoa.core import napp

    udict = udict or {}
    path = join(*args)

    # Create dictionary with variables
    d = {}
    if udict:
        for key, val in udict.items():
            d[key] = str(join(val))
    if expapp:
        for key, val in napp.get_dirs().items():
            d[key] = str(val)
    if expenv:
        d['cwd'] = cwd()
        d['home'] = home()

    # Itereratively expand variables in user dictionary
    update = True
    i = 0
    limit = sys.getrecursionlimit()
    while update:
        update = False
        for key, val in list(d.items()):
            if '%' + key + '%' not in str(path):
                continue
            try:
                path = Path(str(path).replace('%' + key + '%', val))
            except TypeError:
                del d[key]
            update = True
        i += 1
        if i > limit:
            raise RecursionError('cyclic dependency in variables detected')
        path = Path(path)

    # Expand environmental paths
    if expenv:
        path = path.expanduser()

    return str(path)

def getpath(path: PathLike, unpack: bool = True) -> Path:
    """Get path from string or PathLike structure."""
    if unpack:
        return Path(expand(path))
    return join(path)

def dirname(*args: NestPath) -> str:
    r"""Extract directory name from a path like structure.

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
    if path.is_dir():
        return str(path)
    return str(path.parent)

def filename(*args: NestPath) -> str:
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
    if path.is_dir():
        return ''
    return str(path.name)

def basename(*args: NestPath) -> str:
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
    if path.is_dir():
        return ''
    return str(path.stem)

def fileext(*args: NestPath) -> str:
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
    if path.is_dir():
        return ''
    return str(path.suffix).lstrip('.')

def isdir(path: NestPath) -> bool:
    """Determine if given path points to a directory.

    Extends `Path.is_dir()`_ from standard library `pathlib`_ by nested paths
    and path variables.

    Args:
        path: Path like structure, which is expandable to a valid path

    Returns:
        True if the path points to a regular file (or a symbolic link pointing
        to a regular file), False if it points to another kind of file.

    """
    return Path(expand(path)).is_dir()

def isfile(path: NestPath) -> bool:
    """Determine if given path points to a file.

    Extends `Path.is_file()`_ from standard library `pathlib`_ by nested paths
    and path variables.

    Args:
        path: Path like structure, which is expandable to a valid path.

    Returns:
        True if the path points to a directory (or a symbolic link pointing
        to a directory), False if it points to another kind of file.

    """
    return Path(expand(path)).is_file()

def cp(source: NestPath, target: NestPath) -> bool:
    """Copy sub directories from given source to destination directory.

    Args:
        source: Path like structure, which comprises the path of a source folder
        target: Path like structure, which comprises the path of a destination
            folder

    Returns:
        True if the operation was successful.

    """
    import shutil

    sdir, ddir = Path(expand(source)), Path(expand(target))

    for s in sdir.glob('*'):
        t = Path(ddir, basename(s))
        if t.exists():
            shutil.rmtree(str(t))
        try:
            shutil.copytree(str(s), str(t))
        except Exception as err:
            raise OSError("could not copy directory") from err

    return True

def mkdir(*args: NestPath) -> bool:
    """Create directory.

    Args:
        *args: Path like structure, which comprises the path of a new directory

    Returns:
        True if the directory already exists, or the operation was successful.

    """
    path = Path(expand(*args))
    if path.is_dir():
        return True

    try:
        os.makedirs(path)
    except Exception as err:
        raise OSError("could not create directory") from err

    return path.is_dir()

def rmdir(*args: NestPath) -> bool:
    """Remove directory.

    Args:
        *args: Path like structure, which identifies the path of a directory

    Returns:
        True if the directory could be deleted

    """
    import shutil

    path = Path(expand(*args))

    if not path.is_dir():
        return False
    shutil.rmtree(str(path), ignore_errors=True)

    return not path.exists()
