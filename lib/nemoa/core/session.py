# -*- coding: utf-8 -*-
"""Session management.

This module implements session management by a singleton design pattern.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path

from nemoa.core import npath
from nemoa.io import wsfile
from nemoa.types import (
    ClassStrList, CManFileLike, OptBytes, OptPathLike, OptStr, PathLike,
    StrList)

# Module specific types
WsFile = wsfile.WsFile

class Session:
    """Session."""

    # Class Constants
    DEFAULT_PATHS: ClassStrList = [
        '%user_data_dir%', '%site_data_dir%']

    # Instance Variables
    _paths: StrList
    _ws: WsFile

    def __init__(self, workspace: OptPathLike = None,
        basedir: OptPathLike = None, pwd: OptBytes = None) -> None:
        """Initialize instance variables and load Workspace from file."""
        self._paths = self.DEFAULT_PATHS
        self._ws = self.load_workspace(
            workspace=workspace, basedir=basedir, pwd=pwd)

    def load_workspace(self, workspace: OptPathLike = None,
        basedir: OptPathLike = None, pwd: OptBytes = None) -> WsFile:
        """Load Workspace from file.

        Examples:
            >>> load_workspace('%home%/myworkspace.ws.zip')

        """
        if not workspace:
            return WsFile()
        if not basedir:
            # If workspace is a fully qualified file path in the directory
            # structure of the system, ignore the 'paths' list
            if npath.isfile(workspace):
                return WsFile(filepath=workspace, pwd=pwd)
            # Use the 'paths' list to find a workspace
            for path in self._paths:
                candidate = Path(path, workspace)
                if npath.isfile(candidate):
                    return WsFile(filepath=candidate, pwd=pwd)
            return WsFile(filepath=workspace, pwd=pwd)
        return WsFile(filepath=Path(basedir, workspace), pwd=pwd)

    def open_file(
        self, filepath: PathLike, workspace: OptPathLike = None,
        basedir: OptPathLike = None, pwd: OptBytes = None, mode: str = '',
        encoding: OptStr = None, isdir: bool = False) -> CManFileLike:
        """Open file within current or given workspace.

        Args:
            path: String or `path-like object`_, that represents a workspace
                member. In reading mode the path has to point to a valid
                workspace file, or a FileNotFoundError is raised. In writing
                mode the path by default is treated as a file path. New
                directories can be written by setting the argument isdir to
                True.
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
        """
        if workspace:
            ws = self.load_workspace(
                workspace=workspace, basedir=basedir, pwd=pwd)
            return ws.open(
                filepath, mode=mode, encoding=encoding, isdir=isdir)
        return self._ws.open(
            filepath, mode=mode, encoding=encoding, isdir=isdir)

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
