# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Environmentan information and functions for filesystem operations.

.. References:
.. _appdirs:
    http://github.com/ActiveState/appdirs

.. TODO::
    * Add get_file for 'user_package_log', 'temp_log' etc.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from distutils import sysconfig
import fnmatch
import getpass
import locale
import os
import pathlib
import platform
import re
import shutil
import string
import sys
import tempfile
from typing import Any, Iterable, Sequence, Union
import appdirs
from nemoa.base import check, pkg
from nemoa.types import  IterAny, OptStrDict
from nemoa.types import PathLikeList, OptStr, OptStrOrBool, OptPathLike
from nemoa.types import PathLike, StrDict, StrDictOfPaths

#
# Structural Types
#

# Nested paths for tree structured path references
# TODO (patrick.michl@gmail.com): currently (Python 3.7.1) recursive type
# definition is not fully supported by the typing module. When recursive type
# definition is available replace the following lines by their respective
# recursive definitions
PathLikeSeq = Sequence[PathLike]
PathLikeSeq2 = Sequence[Union[PathLike, PathLikeSeq]]
PathLikeSeq3 = Sequence[Union[PathLike, PathLikeSeq, PathLikeSeq2]]
NestPath = Union[PathLike, PathLikeSeq, PathLikeSeq2, PathLikeSeq3]
#NestPath = Sequence[Union[str, Path, 'NestPath']]

#
# Module variables
#

_default_appname = 'nemoa'
_default_appauthor = 'frootlab'
_recursion_limit = sys.getrecursionlimit()

#
# Public Module Functions
#

def get_var(varname: str, *args: Any, **kwds: Any) -> OptStr:
    """Get environment or application variable.

    Environment variables comprise static and runtime properties of the
    operating system like 'username' or 'hostname'. Application variables in
    turn, are intended to describe the application distribution by authorship
    information, bibliographic information, status, formal conditions and notes
    or warnings. For mor information see :PEP:`345`.

    Args:
        varname: Name of environment variable. Typical application variable
            names are:
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
                contain a name and e-mail address, as described in :rfc:`822`.
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
    # Check type of 'varname'
    check.has_type("'varname'", varname, str)

    # Update variables if not present or if optional arguments are given
    if not '_vars' in globals() or args or kwds:
        update_vars(*args, **kwds)
    appvars = globals().get('_vars', {})

    return appvars.get(varname, None)

def get_vars(*args: Any, **kwds: Any) -> StrDict:
    """Get dictionary with environment and application variables.

    Environment variables comprise static and runtime properties of the
    operating system like 'username' or 'hostname'. Application variables in
    turn, are intended to describe the application distribution by authorship
    information, bibliographic information, status, formal conditions and notes
    or warnings. For mor information see :PEP:`345`.

    Args:
        *args: Optional arguments that specify the application, as required by
            :func:`~nemoa.base.env.update_vars`.
        **kwds: Optional keyword arguments that specify the application, as
            required by :func:`~nemoa.base.env.update_vars`.

    Returns:
        Dictionary containing application variables.

    """
    # Update variables if not present or if optional arguments are given
    if not '_vars' in globals() or args or kwds:
        update_vars(*args, **kwds)
    return globals().get('_vars', {}).copy()

def update_vars(filepath: OptPathLike = None) -> None:
    """Update environment and application variables.

    Environment variables comprise static and runtime properties of the
    operating system like 'username' or 'hostname'. Application variables in
    turn, are intended to describe the application distribution by authorship
    information, bibliographic information, status, formal conditions and notes
    or warnings. For mor information see :PEP:`345`.

    Args:
        filepath: Valid filepath to python module, that contains the application
            variables as module attributes. By default the current top level
            module is used.

    """
    # Get package specific environment variables by parsing a given file for
    # module attributes. By default the file of the current top level module
    # is taken. If name is not given, then use the name of the current top level
    # module.
    filepath = filepath or pkg.get_root().__file__
    text = pathlib.Path(filepath).read_text()
    rekey = "__([a-zA-Z][a-zA-Z0-9_]*)__"
    reval = r"['\"]([^'\"]*)['\"]"
    pattern = f"^[ ]*{rekey}[ ]*=[ ]*{reval}"
    info = {}
    for match in re.finditer(pattern, text, re.M):
        info[str(match.group(1))] = str(match.group(2))
    info['name'] = info.get('name', pkg.get_root().__name__)

    # Get plattform specific environment variables
    info['encoding'] = get_encoding()
    info['hostname'] = get_hostname()
    info['osname'] = get_osname()
    info['username'] = get_username()

    # Update globals
    globals()['_vars'] = info

def get_dir(dirname: str, *args: Any, **kwds: Any) -> pathlib.Path:
    """Get application specific environmental directory by name.

    This function returns application specific system directories by platform
    independent names to allow platform independent storage for caching,
    logging, configuration and permanent data storage.

    Args:
        dirname: Environmental directory name. Allowed values are:

            :user_cache_dir: Cache directory of user
            :user_config_dir: Configuration directory of user
            :user_data_dir: Data directory of user
            :user_log_dir: Logging directory of user
            :site_config_dir: Site global configuration directory
            :site_data_dir: Site global data directory
            :site_package_dir: Site global package directory
            :site_temp_dir: Site global directory for temporary files
            :package_dir: Current package directory
            :package_data_dir: Current package data directory
        *args: Optional arguments that specify the application, as required by
            the function 'nemoa.base.env.update_dirs'.
        **kwds: Optional keyword arguments that specify the application, as
            required by the function 'nemoa.base.env.update_dirs'.

    Returns:
        String containing path of environmental directory or None if the
        pathname is not supported.

    """
    # Check type of 'dirname'
    check.has_type("'dirname'", dirname, str)

    # Update derectories if not present or if any optional arguments are given
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

    """
    dirs: StrDictOfPaths = {}

    # Get system directories
    dirs['home'] = get_home()
    dirs['cwd'] = get_cwd()

    # Get application directories from appdirs
    appname = appname or get_var('name') or _default_appname
    appauthor = appauthor or get_var('author') or _default_appauthor
    app_dirs = appdirs.AppDirs(
        appname=appname, appauthor=appauthor, version=version, **kwds)
    dirnames = [
        'user_cache_dir', 'user_config_dir', 'user_data_dir',
        'user_log_dir', 'site_config_dir', 'site_data_dir']
    for dirname in dirnames:
        dirs[dirname] = pathlib.Path(getattr(app_dirs, dirname))

    # Get distribution directories from distutils
    path = pathlib.Path(sysconfig.get_python_lib(), appname)
    dirs['site_package_dir'] = path

    # Tempdir from module tempfile
    tempdir = pathlib.Path(tempfile.gettempdir())
    dirs['site_temp_dir'] = tempdir

    # Get current package directories from top level module
    path = pathlib.Path(pkg.get_root().__file__).parent
    dirs['package_dir'] = path
    dirs['package_data_dir'] = path / 'data'
    dirs['package_temp_dir'] = tempdir / appname

    # Create package temp dir if it does not exist
    dirs['package_temp_dir'].mkdir(parents=True, exist_ok=True) # type: ignore

    globals()['_dirs'] = dirs

def get_temp_file(suffix: OptStr = None) -> pathlib.Path:
    """Get path to temporary file within the package temp directory."""
    apptemp = get_dir('package_temp_dir')
    pathname = tempfile.NamedTemporaryFile(dir=apptemp).name # type: ignore
    filepath = pathlib.Path(pathname)
    if suffix:
        return filepath.with_suffix(suffix)
    return filepath

def get_temp_dir() -> pathlib.Path:
    """Get path to temporary file within the package temp directory."""
    apptemp = get_dir('package_temp_dir')
    pathname = tempfile.TemporaryDirectory(dir=apptemp).name # type: ignore
    dirpath = pathlib.Path(pathname)
    return dirpath

def get_encoding() -> str:
    """Get preferred encoding used for text data.

    This is a wrapper function to the standard library function
    :func:`locale.getpreferredencoding`. This function returns the encoding
    used for text data, according to user preferences. User preferences are
    expressed differently on different systems, and might not be available
    programmatically on some systems, so this function only returns a guess.

    Returns:
        String representing the preferred encoding used for text data.

    """
    return locale.getpreferredencoding(False)

def get_hostname() -> str:
    """Get hostname of the computer.

    This is a wrapper function to the standard library function
    :func:`platform.node`. This function returns the computer’s hostname. If
    the value cannot be determined, an empty string is returned.

    Returns:
        String representing the computer’s hostname or None.

    """
    return platform.node()

def get_osname() -> str:
    """Get name of the Operating System.

    This is a wrapper function to the standard library function
    :func:`platform.system`. This function returns the OS name, e.g. 'Linux',
    'Windows', or 'Java'. If the value cannot be determined, an empty string is
    returned.

    Returns:
        String representing the OS name or None.

    """
    return platform.system()

def get_username() -> str:
    """Login name of the current user.

    This is a wrapper function to the standard library function
    :func:`getpass.getuser`. This function checks the environment variables
    LOGNAME, USER, LNAME and USERNAME, in order, and returns the value of the
    first one which is set to a non-empty string. If none are set, the login
    name from the password database is returned on systems which support the
    pwd module, otherwise, an exception is raised.

    Returns:
        String representing the login name of the current user.

    """
    return getpass.getuser()

def get_cwd() -> pathlib.Path:
    """Get path of current working directory.

    Returns:
        Path of current working directory.

    """
    return pathlib.Path.cwd()

def get_home() -> pathlib.Path:
    """Get path of current users home directory.

    Returns:
        Path of current users home directory.

    """
    return pathlib.Path.home()

def clear_filename(fname: str) -> str:
    r"""Clear filename from invalid characters.

    Args:
        fname: Arbitrary string, which is be cleared from invalid filename
            characters.

    Returns:
        String containing valid path syntax.

    Examples:
        >>> clear_filename('3/\nE{$5}.e')
        '3E5.e'

    """
    valid = "-_.() " + string.ascii_letters + string.digits
    fname = ''.join(c for c in fname if c in valid).replace(' ', '_')
    return fname

def match_paths(paths: PathLikeList, pattern: str) -> PathLikeList:
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
        >>> match_paths([Path('a.b'), Path('b.a')], '*.b')
        [Path('a.b')]

    """
    # Normalize path and pattern representation using POSIX standard
    mapping = {pathlib.PurePath(path).as_posix(): path for path in paths}
    pattern = pathlib.PurePath(pattern).as_posix()

    # Match normalized paths with normalized pattern
    names = list(mapping.keys())
    matches = fnmatch.filter(names, pattern)

    # Return original paths
    return [mapping[name] for name in matches]

def join_path(*args: NestPath) -> pathlib.Path:
    r"""Join nested iterable path-like structure to single path object.

    Args:
        *args: Arguments containing nested iterable paths of strings and
            PathLike objects.

    Returns:
        Single Path comprising all arguments.

    Examples:
        >>> join_path(('a', ('b', 'c')), 'd')
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
        path = pathlib.Path(*flat)
    except TypeError as err:
        raise TypeError(
            "the tokens of nested paths require to be of types "
            "str, bytes or path-like") from err

    return path

def expand(
        *args: NestPath, udict: OptStrDict = None,
        envdirs: bool = True) -> pathlib.Path:
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
    path = join_path(*args)
    udict = udict or {}

    # Create mapping with path variables
    pvars = {}
    if envdirs:
        for key, val in get_dirs().items():
            pvars[key] = str(val)
    if udict:
        for key, val in udict.items():
            pvars[key] = str(join_path(val))

    # Itereratively expand directories
    update = True
    i = 0
    while update:
        update = False
        for key, val in pvars.items():
            if '%' + key + '%' not in str(path):
                continue
            try:
                path = pathlib.Path(str(path).replace('%' + key + '%', val))
            except TypeError:
                del pvars[key]
            update = True
        i += 1
        if i > _recursion_limit:
            raise RecursionError('cyclic dependency in variables detected')
        path = pathlib.Path(path)

    # Expand unix style home path '~'
    if envdirs:
        path = path.expanduser()

    return path

def get_dirname(*args: NestPath) -> str:
    r"""Extract directory name from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> get_dirname(('a', ('b', 'c'), 'd'), 'base.ext')
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

    Extends :meth:`pathlib.Path.is_dir` by nested paths and path variable
    expansion.

    Args:
        path: Path like structure, which is expandable to a valid path

    Returns:
        True if the path points to a regular file (or a symbolic link pointing
        to a regular file), False if it points to another kind of file.

    """
    return expand(path).is_dir()

def is_file(path: NestPath) -> bool:
    """Determine if given path points to a file.

    Extends :meth:`pathlib.Path.is_file` by nested paths and path variable
    expansion.

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
    def copy(source: pathlib.Path, target: pathlib.Path) -> None:
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
        path: Nested :term:`path-like object`, which represents a valid filename
            in the directory structure of the operating system.
        parents: Boolean value, which determines if missing parents of the path
            are created as needed.
        mode: Integer value, which specifies the properties if the file. For
            more information see :func:`os.chmod`.
        exist_ok: Boolean value which determines, if the function returns False,
            if the file already exists.

    Returns:
        True if the file could be created, else False.

    """
    filepath = expand(path)

    # Check type of 'filepath'
    if not isinstance(filepath, pathlib.Path):
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
