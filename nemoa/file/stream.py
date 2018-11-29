# -*- coding: utf-8 -*-
"""Raw stream I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import io
from pathlib import Path
import tempfile
from nemoa.base import env
from nemoa.errors import PullError, PushError
from nemoa.types import Any, Iterator, PathLike
from nemoa.types import ExcType, Exc, Traceback, FileAccessorBase, FileRef

#
# Stream Connector Class
#

class Connector:
    """File Connector Class."""

    _ref: FileRef
    _file: io.IOBase
    _close: bool
    _args: tuple
    _kwds: dict

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        self._ref = file
        self._args = args
        self._kwds = kwds

    def __enter__(self) -> io.IOBase:
        return self.open(self._ref, *self._args, **self._kwds)

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def open(self, *args: Any, **kwds: Any) -> io.IOBase:
        """Open file reference as file object."""
        file = self._ref
        if isinstance(file, (str, Path)):
            return self._open_from_path(file, *args, **kwds)
        if isinstance(file, io.TextIOBase):
            return self._open_from_textfile(file, *args, **kwds)
        if isinstance(file, io.BufferedIOBase):
            return self._open_from_binfile(file, *args, **kwds)
        if isinstance(file, FileAccessorBase):
            return self._open_from_ref(file, *args, **kwds)
        raise TypeError(
            "'file' is required to be a valid file reference, "
            f"not '{type(file).__name__}'")

    def close(self) -> None:
        if hasattr(self, '_close') and self._close:
            self._file.close()

    def _open_from_path(
            self, path: PathLike, *args: Any, **kwds: Any) -> io.IOBase:
        self._file = open(env.expand(path), *args, **kwds) # type: ignore
        self._close = True
        return self._file

    def _open_from_textfile(
            self, file: io.TextIOBase, mode: str = 'r') -> io.IOBase:
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
        self._file = file
        self._close = False
        return file

    def _open_from_binfile(
            self, file: io.BufferedIOBase, mode: str = 'r') -> io.IOBase:
        # Check reading / writing mode
        file_mode = getattr(file, 'mode', None)
        if file_mode and file_mode not in mode:
            file_name = getattr(file, 'name', '?')
            raise RuntimeError(
                f"file '{file_name}' in mode '{file_mode}' can not be "
                f"reopened in mode '{mode}'")

        # Check text / binary mode
        if 'b' in mode:
            self._file = file
        elif 'w' in mode:
            self._file = io.TextIOWrapper( # type: ignore
                file, write_through=True)
        else:
            self._file = io.TextIOWrapper(file) # type: ignore
        self._close = False
        return self._file

    def _open_from_ref(
            self, ref: FileAccessorBase, *args: Any, **kwds: Any) -> io.IOBase:
        self._file = ref.open(*args, **kwds)
        self._close = True
        return self._file

#
# File Wrapper Class
#

class FileWrapper:
    """File wrapper for referenced streams.

    Creates a temporary file within the :func:`tempdir <tempfile.gettempdir>` of
    the system which acts as a local proxy for a referenced file stream.

    """

    _connector: Connector
    _mode: str

    path: Path

    def __init__(self, file: FileRef, mode: str = 'rw') -> None:
        """Initialize temporary file.

        Args:
            file: :term:`File reference` that points to a valid filename in the
                directory structure of the system, a :term:`file object` or a
                generic :class:`file accessor <nemoa.types.FileAccessorBase>`.
            mode: String, which characters specify the mode in which the file
                stream is wrapped. If mode contains the character 'r', then a
                :meth:`.pull`-request is executed during the initialisation,
                otherwise any pull-request raises a
                :class:`~nemoa.errors.PullError`. If mode contains the character
                'w', then a :meth:`.push`-request is executed when closing the
                FileWrapper ibtance with :meth:`.close`, otherwise any
                push-request raises a :class:`~nemoa.errors.PushError`. The
                default mode is 'rw'.

        """
        self._connector = Connector(file)
        self._mode = mode

        # Create temporary file
        self.path = Path(tempfile.NamedTemporaryFile().name)
        self.path.touch()

        # Copy referenced file object to temporary file
        if 'r' in self._mode:
            self.pull()

    def __del__(self) -> None:
        self.close()

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

        # Copy temporary file to referenced stream
        if 'w' in self._mode:
            self.push()

        # Remove temporary file and close
        self.path.unlink()
        self._connector.close()

#
# Constructors
#

@contextlib.contextmanager
def openx(file: FileRef, *args: Any, **kwds: Any) -> Iterator[io.IOBase]:
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
