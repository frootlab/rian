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
"""File I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import io
from pathlib import Path
import weakref
from nemoa.base import abc, env
from nemoa.errors import PullError, PushError, ConnectError, DisconnectError
from nemoa.types import Any, Iterator, PathLike, FileLike, FileRef, OptStr
from nemoa.types import ErrMeta, ErrType, ErrStack
from nemoa.types import BinaryFileLike, TextFileLike

#
# File Info Class
#

class FileInfo:
    """File Info Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading or writing mode.

    """

    _file: FileRef

    def __init__(self, file: FileRef):
        self._file = file

    @property
    def name(self) -> OptStr:
        """Name of the referenced :term:`file object`."""
        if isinstance(self._file, str):
            return Path(self._file).name
        if isinstance(self._file, io.IOBase):
            pathstr = getattr(self._file, 'name', None)
            if pathstr:
                return Path(pathstr).name
            return None
        return getattr(self._file, 'name', None)

#
# File Connector Class
#

class FileConnector:
    """File Connector Class."""

    _ref: FileRef
    _info: FileInfo
    _args: tuple
    _kwds: dict
    _children: list

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        super().__init__() # Initialize Container class

        self._ref = file
        self._info = FileInfo(file)
        self._args = args
        self._kwds = kwds
        self._children = []

    def __enter__(self) -> FileLike:
        return self.open(self._ref, *self._args, **self._kwds)

    def __exit__(self, cls: ErrMeta, obj: ErrType, tb: ErrStack) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def open(self, *args: Any, **kwds: Any) -> FileLike:
        """Open file reference as file object."""
        # Get file handler, depending on the type of the given file reference
        ref = self._ref
        if isinstance(ref, (str, Path)):
            return self._open_from_path(ref, *args, **kwds)
        if isinstance(ref, io.TextIOBase):
            return self._open_from_textfile(ref, *args, **kwds)
        if isinstance(ref, io.BufferedIOBase):
            return self._open_from_raw(ref, *args, **kwds)
        if isinstance(ref, abc.FileAccessor):
            return self._open_from_accessor(ref, *args, **kwds)

        raise TypeError(
            "the referenced file is has an invalid type "
            f"'{type(ref).__name__}'")

    def close(self) -> None:
        for file in self._children:
            with contextlib.suppress(ReferenceError):
                file.close()

    @property
    def name(self) -> OptStr:
        """Name of the referenced :term:`file object`."""
        return self._info.name

    def _open_from_path(
            self, path: PathLike, *args: Any, **kwds: Any) -> FileLike:
        # Open file handler from given file path
        file = open(env.expand(path), *args, **kwds)
        # Store weak reference of file handler
        self._children.append(weakref.proxy(file))
        return file

    def _open_from_textfile(
            self, file: TextFileLike, mode: str = 'r') -> FileLike:
        # Check reading / writing mode
        file_mode = getattr(file, 'mode', None)
        if file_mode and file_mode not in mode:
            file_name = getattr(file, 'name', '?')
            raise RuntimeError(
                f"file '{file_name}' in mode '{file_mode}' can not be"
                f"reopened in mode '{mode}'")
        # Check text / binary mode
        if 'b' in mode:
            raise RuntimeError(
                "wrapping text streams to byte streams is not supported")
        return file

    def _open_from_raw(
            self, file: BinaryFileLike, mode: str = 'r') -> FileLike:
        # Check reading / writing mode
        file_mode = getattr(file, 'mode', None)
        if file_mode and file_mode not in mode:
            file_name = getattr(file, 'name', '?')
            raise RuntimeError(
                f"file '{file_name}' in mode '{file_mode}' can not be "
                f"reopened in mode '{mode}'")
        if 'b' in mode: # binary -> binary
            return file
        if 'w' in mode: # binary -> text (write)
            return io.TextIOWrapper(file, write_through=True)
        return io.TextIOWrapper(file) # binary -> text (read)

    def _open_from_accessor(
            self, ref: abc.FileAccessor, *args: Any, **kwds: Any) -> FileLike:
        file = ref.open(*args, **kwds)
        self._children.append(weakref.proxy(file))
        return file

    def _get_name(self) -> OptStr:
        ref = self._ref
        if isinstance(ref, str):
            return Path(ref).name
        return getattr(ref, 'name', None)

#
# File Proxy Class
#

class FileProxy(abc.Proxy):
    """File buffer for referenced files.

    Creates a temporary file within the :func:`tempdir <tempfile.gettempdir>` of
    the system, which acts as a local proxy for a referenced :term:`file
    object`.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading or writing mode.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. If mode contains the character 'r', then a
            :meth:`.pull`-request is executed during the initialisation,
            otherwise any pull-request raises a
            :class:`~nemoa.errors.PullError`. If mode contains the character
            'w', then a :meth:`.push`-request is executed when closing the
            FileProxy instance with :meth:`.close`, otherwise any push-request
            raises a :class:`~nemoa.errors.PushError`. The default mode is 'rw'.

    """

    _connector: FileConnector
    _mode: str
    _children: list
    _path: Path

    def __init__(self, file: FileRef, mode: str = 'rw') -> None:
        """Initialize temporary file."""
        super().__init__()

        self._mode = mode
        self._children = []
        self._connected = False

        # Create temporary file
        self._path = env.get_temp_file()
        self._path.touch()

        # Connect
        self.connect(file)

        # Copy referenced file object to temporary file
        if 'r' in self._mode:
            self.pull()

    def __del__(self) -> None:
        self.close()

    @property
    def name(self) -> OptStr:
        """Name of the referenced :term:`file object`"""
        return self._connector.name

    @property
    def path(self) -> Path:
        """Path to the temporary file in use."""
        return self._path

    def connect(self, file: FileRef) -> None: # type: ignore
        """Connect to given file reference."""
        if self._connected:
            raise ConnectError("the connection already has been established")
        self._connector = FileConnector(file)
        self._connected = True

    def disconnect(self) -> None:
        """Close connection to referenced file."""
        if not self._connected:
            raise DisconnectError("the proxy has not yet been connected")
        self._connector.close()
        self._connected = False

    def push(self) -> None:
        """Copy temporary file to referenced file object."""
        if 'w' not in self._mode:
            raise PushError(
                "file wrappers in reading mode do not support push requests")
        with self.path.open(mode='r') as src:
            lines = src.readlines()
        with self._connector.open(mode='w') as tgt:
            tgt.writelines(lines)

    def pull(self) -> None:
        """Copy referenced file object to temporary file."""
        if 'r' not in self._mode:
            raise PullError(
                "file wrappers in writing mode do not support pull requests")
        with self._connector.open(mode='r') as src:
            lines = src.readlines()
        with self.path.open(mode='w') as tgt:
            tgt.writelines(lines)

    def open(self, *args: Any, **kwds: Any) -> FileLike:
        """Open file handler to temporary file."""
        # Open file handler to temporary file path
        file = self.path.open(*args, **kwds)
        # Store weak reference of file handler
        self._children.append(weakref.proxy(file))
        return file

    def close(self) -> None:
        """Execute push request and release bound resources."""
        if not self.path.is_file():
            return
        for file in self._children: # Close all opened file handlers
            with contextlib.suppress(ReferenceError):
                file.close()
        if 'w' in self._mode: # Copy temporary file to referenced file
            self.push()
        self.path.unlink() # Remove temporary file
        self.disconnect() # Close connection

#
# Constructors
#

@contextlib.contextmanager
def openx(file: FileRef, *args: Any, **kwds: Any) -> Iterator[FileLike]:
    """Open file reference.

    This context manager extends :py:func`open` by allowing the passed `file`
    argument to be an arbitrary :term:`file reference`. If the `file` argument
    is a String or :term:`path-like object`, the given path may contain
    application variables, like `%home%` or `%user_data_dir%`, which are
    extended before returning a file handler. Afterwards, when exiting the
    `with`-statement, the file is closed. If the passes passed `file`, however,
    is a :term:`file object`, the file is not closed, when exiting the
    `with`-statement.

    Args:
        file: :term:`File reference` that points to a valid filename in the
            directory structure of the system, a :term:`file object` or an
            instance of the class :class:`~nemoa.base.abc.FileAccessor`.
        mode: String, which characters specify the mode in which the file stream
            is opened. The default mode is text reading mode. Supported
            characters are:

            :r: Reading mode (default)
            :w: Writing mode
            :t: Text mode
            :b: Binary mode

    Yields:
        :term:`file object` in reading or writing mode.

    """
    # Define enter and exit of context manager
    try:
        connector = FileConnector(file)
        yield connector.open(*args, **kwds)
    finally:
        connector.close()

@contextlib.contextmanager
def tmpfile(file: FileRef) -> Iterator[Path]:
    """Create a temporary file for a given file reference.

    Args:
        file: :term:`File reference` that points to a valid filename in the
            directory structure of the system, a :term:`file object` or an
            instance of the class :class:`~nemoa.base.abc.FileAccessor`.

    Yields:
        :term:`path-like object` that points to a temporary file.

    """
    try:
        proxy = FileProxy(file)
        yield proxy.path
    finally:
        proxy.close()
