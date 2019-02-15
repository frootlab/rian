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
"""Session management."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
import datetime
from pathlib import Path
from typing import Any, ClassVar, List, Optional
import weakref
from flab.base import abc, attrib, env, errors
from nemoa.core import dcmeta, log, ws
from flab.io import ini, abc as ioabc
from flab.base.types import BytesLike, ErrType, ErrMeta, ErrStack
from flab.base.types import FileLike, OptBytes, OptPath, OptPathLike, OptStr
from flab.base.types import PathLike, StrDict, StrList, StrOrInt

#
# Session Records
#

@dataclasses.dataclass
class Record:
    """Class for Session Records."""
    ref: weakref.ReferenceType
    date: datetime.datetime

#
# Session Store
#

class Store(dict, abc.Singleton):
    """Singleton Class for the Storage of Session Records."""

#
# Session Manager
#

class Manager(abc.Singleton):
    """Singleton Class for Session Manager."""
    _store: Store = Store()

    def list(self) -> List[Record]:
        return sorted(self._store.items()) # type: ignore

    def get(self, sid: Optional[int]) -> 'Session':
        return self._store[sid].ref()

    def add(self, session: object) -> None:
        sid = id(session)
        if sid in self._store:
            raise errors.FoundError(
                f"session with id {sid} does already exist")
        ref = weakref.ref(session)
        date = datetime.datetime.now()
        rec = Record(ref=ref, date=date)
        self._store[sid] = rec

    def remove(self, sid: Optional[int]) -> None:
        del self._store[sid]

#
# Meta Class for Session Base Classes
#

class Meta(abc.MultitonMeta):
    """Metaclass for Session Base Classes.

    Session objects require an instanciation per SessionID, which is closely
    related to the Multiton Pattern.

    """
    _manager: Manager = Manager()

    def __call__(
            cls, *args: Any, sid: Optional[int] = None, **kwds: Any) -> object:
        # Search for SessionID in registry and if found return a reference
        # to the session instance
        try:
            return Meta._manager.get(sid)
        except KeyError:
            pass

        # If the SessionID is given (not None), but could not be found in the
        # registry, then the session ether has been destroyed by the garbage
        # collector or manually been removed by the Session Manager. In any such
        # case a NotFoundError is raised.
        if sid is not None:
            raise errors.NotFoundError(f"session id {sid} is not valid")

        # If the SessionID could not be found, create a new subclass of the
        # session class (for class isolation) and a new instance of the session
        # subclass. Finally add the session to the session store by using the
        # session manager.
        # TODO: Make creation of sessions thread safe!
        subcls = Meta(cls.__name__, (cls, ), {'__slots__': []})
        obj = super(Meta, subcls).__call__(*args, **kwds)
        Meta._manager.add(obj)

        return obj

#
# Abstract Base Class for Sessions
#

class SessionType(metaclass=Meta):
    """Abstract Base Class for Sessions."""
    __slots__: list = []

#
# Session Class
#

class Session(attrib.Group, SessionType):
    """Session Class."""
    __slots__: list = []

    _config_file_path: ClassVar[str] = '%user_config_dir%/nemoa.ini'
    _config_file_struct: ClassVar[ini.SecDict] = {
        'session': {
            'path': Path,
            'restore_on_startup': bool,
            'autosave_on_exit': bool}}
    _default_config: ClassVar[StrDict] = {
        'path': None,
        'restore_on_startup': False,
        'autosave_on_exit': False}
    _default_paths: StrList = [
        '%user_data_dir%', '%site_data_dir%', '%package_data_dir%']

    #
    # Public Attributes and Attribute Groups
    #

    dc: attrib.Group = dcmeta.Group(remote=True)

    config: property = attrib.MetaData(dtype=dict)
    config.__doc__ = """Session configuration."""

    paths: property = attrib.MetaData(dtype=list)
    paths.__doc__ = """Search paths for workspaces."""

    files: property = attrib.Virtual('_get_files')
    files.__doc__ = """Files within the current workspace."""

    folders: property = attrib.Virtual('_get_folders')
    folders.__doc__ = """Folders within the current workspace."""

    path: property = attrib.Virtual('_get_path')
    path.__doc__ = """Filepath of the current workspace."""

    #
    # Protected Attributes
    #

    _logger: property = attrib.Temporary(dtype=log.Logger)
    _file: property = attrib.Content(dtype=ws.Workspace)

    #
    # Special Methods
    #

    def __init__(
            self, workspace: OptPathLike = None, basedir: OptPathLike = None,
            pwd: OptBytes = None) -> None:
        super().__init__() # Initialize Attribute Container

        # Initialize instance variables with default values
        self.config = self._default_config.copy()
        self._file = ws.Workspace()
        self._logger = log.Logger()
        self.paths = [env.expand(path) for path in self._default_paths]

        # Bind session to workspace
        self._set_attr_group_parent(self._file)

        # Load session configuration from file
        if env.is_file(self._config_file_path):
            self._load_config()

        # Load workspace from file
        filepath: OptPath = None
        if workspace and isinstance(workspace, (Path, str)):
            filepath = Path(workspace)
        elif self.config.get('restore_on_startup'):
            cfg_path = self.config.get('path')
            if isinstance(cfg_path, (Path, str)):
                filepath = Path(cfg_path)
        if isinstance(filepath, Path):
            self.load(workspace=filepath, basedir=basedir, pwd=pwd)

    def __enter__(self) -> 'Session':
        return self

    def __exit__(self, cls: ErrMeta, obj: ErrType, tb: ErrStack) -> None:
        self.close() # Close Workspace
        self._save_config() # Save config

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sid={id(self)})'

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
        self._file = ws.Workspace(filepath=path, pwd=pwd)
        self._set_attr_group_parent(self._file)

    def save(self) -> None:
        """Save Workspace to current file."""
        self._file.save()

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file.

        Args:
            filepath: String or :term:`path-like object`, that represents the
                name of a workspace file.

        """
        self._file.saveas(filepath)

    def close(self) -> None:
        """Close current session."""
        if self.config.get('autosave_on_exit') and self._file.changed:
            self.save()
        if hasattr(self._file, 'close'):
            self._file.close()

    def get_file_accessor(self, path: PathLike) -> ioabc.Connector:
        """Get connector to workspace member.

        Args:
            path: String or :term:`path-like object`, that represents a
                workspace member. In reading mode the path has to point to a
                valid workspace file, or a FileNotFoundError is raised. In
                writing mode the path by default is treated as a file path. New
                directories can be written by setting the argument is_dir to
                True.

        Returns:
            Instance of class :class:`~flab.io.abc.Connector`, which
            points to a workspace member.

        """
        return self._file.get_file_accessor(path)

    def open(
            self, filepath: PathLike, workspace: OptPathLike = None,
            basedir: OptPathLike = None, pwd: OptBytes = None, mode: str = '',
            encoding: OptStr = None, is_dir: bool = False) -> FileLike:
        """Open file within current or given workspace.

        Args:
            filepath: String or :term:`path-like object`, that represents a
                workspace member. In reading mode the path has to point to a
                valid workspace file, or a FileNotFoundError is raised. In
                writing mode the path by default is treated as a file path. New
                directories can be written by setting the argument is_dir to
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
            is_dir: Boolean value which determines, if the path is to be treated
                as a directory or not. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        Returns:
            Context manager for :term:`file object` in reading or writing mode.

        """
        if workspace:
            path = self._locate_path(workspace=workspace, basedir=basedir)
            ws_file = ws.Workspace(filepath=path, pwd=pwd)
            return ws_file.open(
                filepath, mode=mode, encoding=encoding, is_dir=is_dir)
        return self._file.open(
            filepath, mode=mode, encoding=encoding, is_dir=is_dir)

    def append(self, source: PathLike, target: OptPathLike = None) -> bool:
        """Append file to the current workspace.

        Args:
            source: String or :term:`path-like object`, that points to a valid
                file in the directory structure if the system. If the file does
                not exist, a FileNotFoundError is raised. If the filepath points
                to a directory, a IsADirectoryError is raised.
            target: String or :term:`path-like object`, that points to a valid
                directory in the directory structure of the workspace. By
                default the root directory is used. If the directory does not
                exist, a FileNotFoundError is raised. If the target directory
                already contains a file, which name equals the filename of the
                source, a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been appended.

        """
        return self._file.append(source, target=target)

    def unlink(self, filepath: PathLike, ignore_missing: bool = True) -> bool:
        """Remove file from the current workspace.

        Args:
            filepath: String or :term:`path-like object`, that points to a file
                in the directory structure of the workspace. If the filapath
                points to a directory, an IsADirectoryError is raised. For the
                case, that the file does not exist, the argument ignore_missing
                determines, if a FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target file does not exist. The default
                behaviour, is to ignore missing files.

        Returns:
            Boolean value, which is True if the given file was removed.

        """
        return self._file.unlink(filepath, ignore_missing=ignore_missing)

    def mkdir(self, dirpath: PathLike, ignore_exists: bool = False) -> bool:
        """Create a new directory in current workspace.

        Args:
            dirpath: String or :term:`path-like object`, that represents a valid
                directory name in the directory structure of the workspace. If
                the directory already exists, the argument ignore_exists
                determines, if a FileExistsError is raised.
            ignore_exists: Boolean value which determines, if FileExistsError is
                raised, if the target directory already exists. The default
                behaviour is to raise an error, if the file already exists.

        Returns:
            Boolean value, which is True if the given directory was created.

        """
        return self._file.mkdir(dirpath, ignore_exists=ignore_exists)

    def rmdir(
            self, dirpath: PathLike, recursive: bool = False,
            ignore_missing: bool = False) -> bool:
        """Remove directory from current workspace.

        Args:
            dirpath: String or :term:`path-like object`, that points to a
                directory in the directory structure of the workspace. If the
                directory does not exist, the argument ignore_missing
                determines, if a FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target directory does not exist. The default
                behaviour, is to raise an error if the directory is missing.
            recursive: Boolean value which determines, if directories are
                removed recursively. If recursive is False, then only empty
                directories can be removed. If recursive, however, is True, then
                all files and subdirectories are alse removed. By default
                recursive is False.

        Returns:
            Boolean value, which is True if the given directory was removed.

        """
        return self._file.rmdir(
            dirpath, recursive=recursive, ignore_missing=ignore_missing)

    def search(self, pattern: OptStr = None) -> StrList:
        """Search for files in the current workspace.

        Args:
            pattern: Search pattern that contains Unix shell-style wildcards:
                '*': Matches arbitrary strings
                '?': Matches single characters
                [seq]: Matches any character in seq
                [!seq]: Matches any character not in seq
                By default a list of all files and directories is returned.

        Returns:
            List of files and directories in the directory structure of the
            workspace, that match the search pattern.

        """
        return self._file.search(pattern)

    def copy(self, source: PathLike, target: PathLike) -> bool:
        """Copy file within current workspace.

        Args:
            source: String or :term:`path-like object`, that points to a file in
                the directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or :term:`path-like object`, that points to a new
                filename or an existing directory in the directory structure of
                the workspace. If the target is a directory the target file
                consists of the directory and the basename of the source file.
                If the target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file was copied.

        """
        return self._file.copy(source, target)

    def move(self, source: PathLike, target: PathLike) -> bool:
        """Move file within current workspace.

        Args:
            source: String or :term:`path-like object`, that points to a file in
                the directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or :term:`path-like object`, that points to a new
                filename or an existing directory in the directory structure of
                the workspace. If the target is a directory the target file
                consists of the directory and the basename of the source file.
                If the target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been moved.

        """
        return self._file.move(source, target)

    def read_text(self, filepath: PathLike, encoding: OptStr = None) -> str:
        """Read text from file in current workspace.

        Args:
            filepath: String or :term:`path-like object`, that points to a valid
                file in the directory structure of the workspace. If the file
                does not exist a FileNotFoundError is raised.
            encoding: Specifies the name of the encoding, which is used to
                decode the stream’s bytes into strings. By default the preferred
                encoding of the operating system is used.

        Returns:
            Contents of the given filepath encoded as string.

        """
        return self._file.read_text(filepath, encoding=encoding)

    def read_bytes(self, filepath: PathLike) -> bytes:
        """Read bytes from file in current workspace.

        Args:
            filepath: String or :term:`path-like object`, that points to a valid
                file in the dirctory structure of the workspace. If the file
                does not exist a FileNotFoundError is raised.

        Returns:
            Contents of the given filepath as bytes.

        """
        return self._file.read_bytes(filepath)

    def write_text(
            self, text: str, filepath: PathLike,
            encoding: OptStr = None) -> int:
        """Write text to file.

        Args:
            text: String, which has to be written to the given file.
            filepath: String or :term:`path-like object`, that represents a
                valid filename in the dirctory structure of the workspace.
            encoding: Specifies the name of the encoding, which is used to
                encode strings into bytes. By default the preferred encoding of
                the operating system is used.

        Returns:
            Number of characters, that are written to the file.

        """
        return self._file.write_text(text, filepath, encoding=encoding)

    def write_bytes(self, data: BytesLike, filepath: PathLike) -> int:
        """Write bytes to file.

        Args:
            data: Bytes, which are to be written to the given file.
            filepath: String or :term:`path-like object`, that represents a
                valid filename in the dirctory structure of the workspace.

        Returns:
            Number of bytes, that are written to the file.

        """
        return self._file.write_bytes(data, filepath)

    def log(self, level: StrOrInt, msg: str, *args: Any, **kwds: Any) -> None:
        """Log event.

        Args:
            level: Integer value or string, which describes the severity of the
                event. Ordered by ascending severity, the allowed level names
                are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. The
                respectively corresponding level numbers are 10, 20, 30, 40 and
                50.
            msg: Message ``format string``_, which may can contain literal text
                or replacement fields delimited by braces. Each replacement
                field contains either the numeric index of a positional
                argument, given by *args, or the name of a keyword argument,
                given by the keyword *extra*.
            *args: Arguments, which can be used by the message format string.
            **kwds: Additional Keywords, used by the function `Logger.log()`_.

        """
        self._logger.log(level, msg, *args, **kwds)

    #
    # Protected Methods
    #

    def _load_config(self) -> None:
        config = ini.load(
            self._config_file_path, scheme=self._config_file_struct)
        if 'session' in config and isinstance(config['session'], dict):
            for key, val in config['session'].items():
                self.config[key] = val

    def _save_config(self) -> None:
        config = {'session': self.config}
        ini.save(config, self._config_file_path)

    def _get_path(self) -> OptPath:
        return self._file.path

    def _get_files(self) -> StrList:
        return self._file.search()

    def _get_folders(self) -> StrList:
        return self._file.folders

    def _locate_path(
            self, workspace: OptPathLike = None,
            basedir: OptPathLike = None) -> OptPath:
        if not workspace:
            return None
        if not basedir:
            # If workspace is a fully qualified file path in the directory
            # structure of the system, ignore the 'paths' list
            if env.is_file(workspace):
                return env.expand(workspace)
            # Use the 'paths' list to find a workspace
            for path in self.paths:
                candidate = Path(path, workspace)
                if candidate.is_file():
                    return candidate
            raise FileNotFoundError(
                f"file {workspace} does not exist")
        return Path(basedir, workspace)

#
# Singleton Accessor Functions
#

def get_instance() -> Session:
    """Get current session instance."""
    if not '_session' in globals():
        globals()['_session'] = Session()
    return globals()['_session']
