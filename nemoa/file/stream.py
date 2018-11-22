# -*- coding: utf-8 -*-
"""Stream I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
from io import IOBase, TextIOWrapper
from nemoa.base import env
from nemoa.types import Any, BytesIOBaseClass
from nemoa.types import Path, TextIOBaseClass, Iterator, PathLike
from nemoa.types import ExcType, Exc, Traceback, FileRefBase, FileRef

#
# Stream Connector
#

class Connector:
    """Stream Connector Class."""

    _ref: FileRef
    _file: IOBase
    _close: bool
    _args: tuple
    _kwds: dict

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        self._ref = file
        self._args = args
        self._kwds = kwds

    def __enter__(self) -> IOBase:
        return self.open(self._ref, *self._args, **self._kwds)

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def open(self, *args: Any, **kwds: Any) -> IOBase:
        """Open stream reference as file object."""
        file = self._ref
        if isinstance(file, (str, Path)):
            return self._open_from_path(file, *args, **kwds)
        if isinstance(file, IOBase):
            return self._open_from_file(file, *args, **kwds)
        if isinstance(file, FileRefBase):
            return self._open_from_ref(file, *args, **kwds)
        raise TypeError(
            "'file' is required to be a stream reference, "
            f"not '{type(file).__name__}'")

    def close(self) -> None:
        if hasattr(self, '_close') and self._close:
            self._file.close()

    def _open_from_path(
            self, path: PathLike, *args: Any, **kwds: Any) -> IOBase:
        self._file = open(env.expand(path), *args, **kwds) # type: ignore
        self._close = True
        return self._file

    def _open_from_file(self, file: IOBase, mode: str = 'r') -> IOBase:
        if isinstance(file, TextIOBaseClass):
            if 'b' in mode:
                raise RuntimeError(
                    "wrapping text streams to byte streams is not supported")
            self._file = file
        elif isinstance(file, BytesIOBaseClass):
            if 'b' in mode:
                self._file = file
            elif 'w' in mode:
                self._file = TextIOWrapper( # type: ignore
                    file, write_through=True)
            else:
                self._file = TextIOWrapper(file) # type: ignore
        self._close = False
        return self._file

    def _open_from_ref(
            self, ref: FileRefBase, *args: Any, **kwds: Any) -> IOBase:
        self._file = ref.open(*args, **kwds)
        self._close = True
        return self._file

#
# Functions
#

@contextlib.contextmanager
def openx(file: FileRef, *args: Any, **kwds: Any) -> Iterator[IOBase]:
    """Context manager for stream references.

    This context manager extends :py:func`open` by allowing the passed `file`
    argument to be an arbitrary :term:`stream reference`.
    If the `file` argument is a str or a path-like object, the given path may
    contain application variables, like `%home%` or `%user_data_dir%`, which are
    extended before returning a file handler to a :term:`binary file`.
    Afterwards, when exiting the `with`-statement, the file is closed. If the
    *file* argument, however, is a :term:`file object`, the file is not closed,
    when exiting the `with`-statement.

    Args:
        file: String or :term:`path-like object` that points to a valid filename
            in the directory structure of the system, or a :term:`file object`.
        mode: String, which characters specify the mode in which the file stream
            is opened or wrapped. The default mode is text reading mode.
            Supported characters are:

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
