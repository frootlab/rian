# -*- coding: utf-8 -*-
"""Raw stream I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import io
from pathlib import Path
import weakref
from nemoa.base import env
from nemoa.errors import PullError, PushError
from nemoa.types import Any, Iterator, PathLike, FileLike, FileRef
from nemoa.types import ExcType, Exc, Traceback, FileAccessorBase
from nemoa.types import BinaryFileLike, TextFileLike, IterFileLike

#
# Stream Connector Class
#

class Connector:
    """File Connector Class."""

    _ref: FileRef
    _args: tuple
    _kwds: dict
    _children: list

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        self._ref = file
        self._args = args
        self._kwds = kwds
        self._children = []

    def __enter__(self) -> FileLike:
        return self.open(self._ref, *self._args, **self._kwds)

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
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
            return self._open_from_binfile(ref, *args, **kwds)
        if isinstance(ref, FileAccessorBase):
            return self._open_from_accessor(ref, *args, **kwds)

        raise TypeError(
            "the referenced file is has an invalid type "
            f"'{type(ref).__name__}'")

    def close(self) -> None:
        for file in self._children:
            with contextlib.suppress(ReferenceError):
                file.close()

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

    def _open_from_binfile(
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
            self, ref: FileAccessorBase, *args: Any, **kwds: Any) -> FileLike:
        file = ref.open(*args, **kwds)
        self._children.append(weakref.proxy(file))
        return file

#
# File Wrapper Class
#

class FileWrapper:
    """File wrapper for referenced streams.

    Creates a temporary file within the :func:`tempdir <tempfile.gettempdir>` of
    the system which acts as a local proxy for a referenced file stream.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.types.FileAccessorBase>` or an opened file object in reading
            or writing mode.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. If mode contains the character 'r', then a
            :meth:`.pull`-request is executed during the initialisation,
            otherwise any pull-request raises a
            :class:`~nemoa.errors.PullError`. If mode contains the character
            'w', then a :meth:`.push`-request is executed when closing the
            FileWrapper ibtance with :meth:`.close`, otherwise any push-request
            raises a :class:`~nemoa.errors.PushError`. The default mode is 'rw'.

    """

    _connector: Connector
    _mode: str
    _children: list

    path: Path

    def __init__(self, file: FileRef, mode: str = 'rw') -> None:
        """Initialize temporary file."""
        self._connector = Connector(file)
        self._mode = mode
        self._children = []

        # Create temporary file
        self.path = env.get_temp_file()
        self.path.touch()

        # Copy referenced file object to temporary file
        if 'r' in self._mode:
            self.pull()

    def __del__(self) -> None:
        self.close()

    def open(self, *args: Any, **kwds: Any) -> FileLike:
        """Open file handler to temporary file."""
        # Open file handler to temporary file path
        file = self.path.open(*args, **kwds)
        # Store weak reference of file handler
        self._children.append(weakref.proxy(file))
        return file

    def pull(self) -> None:
        """Copy referenced file object to temporary file."""
        if 'r' not in self._mode:
            raise PullError(
                "file wrappers in writing mode do not support pull requests")
        with self._connector.open(mode='r') as src:
            lines = src.readlines()
        with self.path.open(mode='w') as tgt:
            tgt.writelines(lines)

    def push(self) -> None:
        """Copy temporary file to referenced file object."""
        if 'w' not in self._mode:
            raise PushError(
                "file wrappers in reading mode do not support push requests")
        with self.path.open(mode='r') as src:
            lines = src.readlines()
        with self._connector.open(mode='w') as tgt:
            tgt.writelines(lines)

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
        self._connector.close() # Close connector

#
# Constructors
#

@contextlib.contextmanager
def openx(file: FileRef, *args: Any, **kwds: Any) -> IterFileLike:
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
            directory structure of the system, a :term:`file object` or a
            generic :class:`file accessor <nemoa.types.FileAccessorBase>`.
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
        connector = Connector(file)
        yield connector.open(*args, **kwds)
    finally:
        connector.close()

@contextlib.contextmanager
def tmpfile(file: FileRef) -> Iterator[Path]:
    """Create a temporary file for a given file reference.

    Args:
        file: :term:`File reference` that points to a valid filename in the
            directory structure of the system, a :term:`file object` or a
            generic :class:`file accessor <nemoa.types.FileAccessorBase>`.

    Yields:
        :term:`path-like object` that points to a temporary file.

    """
    try:
        wrapper = FileWrapper(file)
        yield wrapper.path
    finally:
        wrapper.close()
