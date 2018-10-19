# -*- coding: utf-8 -*-
"""Session management.

This module implements session management by a singleton design pattern.

.. References:
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path

from nemoa.classes import Attr, ReadOnlyAttr, ReadWriteAttr
from nemoa.core import npath
from nemoa.io import inifile, wsfile
from nemoa.types import (
    CManFileLike, ClassVar, OptBytes, OptPath, OptPathLike, OptStr, PathLike,
    PathList, StrDict2, StrList)

# Module specific types
WsFile = wsfile.WsFile

class Session:
    """Session."""

    #
    # Class Variables
    #

    CONFIG_FILE: ClassVar[str] = '%user_config_dir%/nemoa.ini'
    CONFIG_STRUCT: ClassVar[StrDict2] = {
        'session': {
            'path': 'path',
            'restore': 'bool'}}
    DEFAULT_CONFIG: ClassVar[StrDict2] = {
        'session': {
            'path': None,
            'restore': False}}
    DEFAULT_PATHS: StrList = [
        '%user_data_dir%', '%site_data_dir%', '%package_data_dir%']

    #
    # Instance Variables
    #

    _cfg: StrDict2
    _file: WsFile
    _paths: PathList

    #
    # Attributes
    #

    paths: Attr = ReadWriteAttr(list, key='_paths')
    paths.__doc__ = """Search paths for workspaces."""

    path: Attr = ReadOnlyAttr(Path, getter='_get_path')
    path.__doc__ = """Filepath of the workspace."""

    #
    # Magic
    #

    def __init__(self, workspace: OptPathLike = None,
        basedir: OptPathLike = None, pwd: OptBytes = None) -> None:
        """Initialize instance variables and load workspace from file."""
        # Initialize instance variables with default values
        self._cfg = self.DEFAULT_CONFIG.copy()
        self._file = WsFile()
        self._paths = [npath.expand(path) for path in self.DEFAULT_PATHS]

        # Load configuration from file
        if npath.is_file(self.CONFIG_FILE):
            self._load_config()

        # Load workspace from file
        filepath: OptPath = None
        if workspace and isinstance(workspace, (Path, str)):
            filepath = Path(workspace)
        elif self._cfg.get('restore'):
            cfg_path = self._cfg.get('path')
            if isinstance(cfg_path, (Path, str)):
                filepath = Path(cfg_path)
        if isinstance(filepath, Path):
            self.load(workspace=filepath, basedir=basedir, pwd=pwd)

    #
    # Public Methods
    #

    def load(
            self, workspace: OptPathLike = None, basedir: OptPathLike = None,
            pwd: OptBytes = None) -> None:
        """Load Workspace from file.

        Args:
            workspace:
            basedir:
            pwd: Bytes representing password of workspace file.

        """
        path = self._locate_path(workspace=workspace, basedir=basedir)
        self._file = WsFile(filepath=path, pwd=pwd)

    def save(self) -> None:
        """Save Workspace to current file."""
        self._file.save()

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file.

        Args:
            filepath: String or `path-like object`_, that represents the name of
                a workspace file.

        """
        self._file.saveas(filepath)

    # def list(self) -> None:
    #     return None

    def open(
        self, filepath: PathLike, workspace: OptPathLike = None,
        basedir: OptPathLike = None, pwd: OptBytes = None, mode: str = '',
        encoding: OptStr = None, isdir: bool = False) -> CManFileLike:
        """Open file within current or given workspace.

        Args:
            filepath: String or `path-like object`_, that represents a workspace
                member. In reading mode the path has to point to a valid
                workspace file, or a FileNotFoundError is raised. In writing
                mode the path by default is treated as a file path. New
                directories can be written by setting the argument isdir to
                True.
            workspace:
            basedir:
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is reading in text mode. Suported
                characters are:
                'r': Reading mode (default)
                'w': Writing mode
                'b': Binary mode
                't': Text mode (default)
            encoding: In binary mode encoding has not effect. In text mode
                encoding specifies the name of the encoding, which in reading
                and writing mode respectively is used to decode the stream’s
                bytes into strings, and to encode strings into bytes. By default
                the preferred encoding of the operating system is used.
            isdir: Boolean value which determines, if the path is to be treated
                as a directory or not. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        Returns:
            Context manager for `file-like object`_ in reading or writing mode.

        """
        if workspace:
            path = self._locate_path(workspace=workspace, basedir=basedir)
            ws = WsFile(filepath=path, pwd=pwd)
            return ws.open(
                filepath, mode=mode, encoding=encoding, isdir=isdir)
        return self._file.open(
            filepath, mode=mode, encoding=encoding, isdir=isdir)

    #
    # Private Methods
    #

    def _load_config(self) -> None:
        cfg = inifile.load(self.CONFIG_FILE, self.CONFIG_STRUCT)
        self._cfg = cfg.get('session') or {}

    def _save_config(self) -> None:
        cfg = {'session': self._cfg}
        inifile.save(cfg, self.CONFIG_FILE)

    def _get_path(self) -> OptPath:
        if not isinstance(self._file, WsFile):
            return None
        return self._file.path

    def _locate_path(
            self, workspace: OptPathLike = None,
            basedir: OptPathLike = None) -> OptPath:
        if not workspace:
            return None
        if not basedir:
            # If workspace is a fully qualified file path in the directory
            # structure of the system, ignore the 'paths' list
            if npath.is_file(workspace):
                return npath.expand(workspace)
            # Use the 'paths' list to find a workspace
            for path in self._paths:
                candidate = Path(path, workspace)
                if candidate.is_file():
                    return candidate
            raise FileNotFoundError(
                f"file {workspace} does not exist")
        return Path(basedir, workspace)

# from nemoa.types import Any
#
# def cur():
#     """Get current session instance."""
#     if '_cur' not in globals():
#         globals()['_cur'] = new()
#     return globals()['_cur']
#
# def get(*args: Any, **kwds: Any) -> Any:
#     """Get meta information and content from current session."""
#     return cur().get(*args, **kwds)
#
# def log(*args, **kwds):
#     """Log message in current session."""
#     return cur().log(*args, **kwds)
#
# def new(*args, **kwds):
#     """Create session instance from session dictionary."""
#     from nemoa.session import classes
#     return classes.new(*args, **kwds)
#
# def open(*args, **kwds):
#     """Open object in current session."""
#     return cur().open(*args, **kwds)
#
# def path(*args: Any, **kwds: Any) -> str:
#     """Get path for given object in current session."""
#     return cur().path(*args, **kwds)
#
# def run(*args, **kwds):
#     """Run script in current session."""
#     return cur().run(*args, **kwds)
#
# def set(*args, **kwds):
#     """Set configuration parameter and env var in current session."""
#     return cur().set(*args, **kwds)
