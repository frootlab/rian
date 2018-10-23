# -*- coding: utf-8 -*-
"""Collection of functions for platform independent filesystem operations.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _pathlib:
    https://docs.python.org/3/library/pathlib.html
.. _Path.is_file():
    https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_file
.. _Path.is_dir():
    https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_dir
.. _os.chmod():
    https://docs.python.org/3/library/os.html#os.chmod

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import fnmatch
import os
import shutil
import string
import sys

from pathlib import Path, PurePath

from nemoa.base import env
from nemoa.types import (
    Any, Iterable, IterAny, NestPath, OptStrDict, PathLikeList)

_RECURSION_LIMIT = sys.getrecursionlimit()

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
            "str, bytes or path-like") from err

    return path

def expand(
        *args: NestPath, udict: OptStrDict = None,
        envdirs: bool = True) -> Path:
    r"""Expand path variables.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.
        udict: dictionary for user variables.
            Thereby the keys in the dictionary are encapsulated
            by the symbol '%'. The user variables may also include references.
        envdirs: Boolen value which determines if environmental path variables
            are expanded. For a full list of valid environmental path variables
            see 'nemoa.base.env.get_dirs'. Default is True

    Returns:
        String containing valid path syntax.

    Examples:
        >>> expand('%var1%/c', 'd', udict = {'var1': 'a/%var2%', 'var2': 'b'})
        'a\\b\\c\\d'

    """
    path = join(*args)
    udict = udict or {}

    # Create mapping with path variables
    pvars = {}
    if envdirs:
        for key, val in env.get_dirs().items():
            pvars[key] = str(val)
    if udict:
        for key, val in udict.items():
            pvars[key] = str(join(val))

    # Itereratively expand directories
    update = True
    i = 0
    while update:
        update = False
        for key, val in pvars.items():
            if '%' + key + '%' not in str(path):
                continue
            try:
                path = Path(str(path).replace('%' + key + '%', val))
            except TypeError:
                del pvars[key]
            update = True
        i += 1
        if i > _RECURSION_LIMIT:
            raise RecursionError('cyclic dependency in variables detected')
        path = Path(path)

    # Expand unix style home path '~'
    if envdirs:
        path = path.expanduser()

    return path

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
    path = expand(*args)
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
    path = expand(*args)
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
    path = expand(*args)
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
    path = expand(*args)
    if path.is_dir():
        return ''
    return str(path.suffix).lstrip('.')

def is_dir(path: NestPath) -> bool:
    """Determine if given path points to a directory.

    Extends `Path.is_dir()`_ from standard library `pathlib`_ by nested paths
    and path variable expansion.

    Args:
        path: Path like structure, which is expandable to a valid path

    Returns:
        True if the path points to a regular file (or a symbolic link pointing
        to a regular file), False if it points to another kind of file.

    """
    return expand(path).is_dir()

def is_file(path: NestPath) -> bool:
    """Determine if given path points to a file.

    Extends `Path.is_file()`_ from standard library `pathlib`_ by nested paths
    and path variable expansion.

    Args:
        path: Path like structure, which is expandable to a valid path.

    Returns:
        True if the path points to a directory (or a symbolic link pointing
        to a directory), False if it points to another kind of file.

    """
    return expand(path).is_file()

def copytree(source: NestPath, target: NestPath) -> None:
    """Copy directory structure from given source to target directory.

    Args:
        source: Path like structure, which comprises the path of a source folder
        target: Path like structure, which comprises the path of a destination
            folder

    Returns:
        True if the operation was successful.

    """
    # Recursive copy function, that allows existing files
    def copy(source: Path, target: Path) -> None:
        if source.is_dir():
            if not target.is_dir():
                target.mkdir()
            for each in source.glob('*'):
                copy(each, target / each.name)
        else:
            shutil.copy(source, target)
    copy(expand(source), expand(target))

def mkdir(*args: NestPath) -> bool:
    """Create directory.

    Args:
        *args: Path like structure, which comprises the path of a new directory

    Returns:
        True if the directory already exists, or the operation was successful.

    """
    path = expand(*args)
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
    path = expand(*args)

    if not path.is_dir():
        return False
    shutil.rmtree(str(path), ignore_errors=True)

    return not path.exists()

def touch(
        path: NestPath, parents: bool = True, mode: int = 0o666,
        exist_ok: bool = True) -> bool:
    """Create an empty file at the specified path.

    Args:
        path: Nested `path-like object`_, which represents a valid filename in
            the directory structure of the operating system.
        parents: Boolean value, which determines if missing parents of the path
            are created as needed.
        mode: Integer value, which specifies the properties if the file. For
            more information see `os.chmod()`_.
        exist_ok: Boolean value which determines, if the function returns False,
            if the file already exists.

    Returns:
        True if the file could be created, else False.

    """
    filepath = expand(path)

    # Check type of 'filepath'
    if not isinstance(filepath, Path):
        return False

    # Check if directory exists and optionally create it
    dirpath = filepath.parent
    if not dirpath.is_dir():
        if not parents:
            return False
        dirpath.mkdir(parents=True, exist_ok=True)
        if not dirpath.is_dir():
            return False

    # Check if file already exsists
    if filepath.is_file() and not exist_ok:
        return False

    # Touch file with given
    filepath.touch(mode=mode, exist_ok=exist_ok)

    return filepath.is_file()
