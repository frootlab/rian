# -*- coding: utf-8 -*-
"""I/O functions for binary-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _binary-file:
    https://docs.python.org/3/glossary.html#term-binary-file

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from contextlib import contextmanager

from nemoa.core import npath
from nemoa.types import (
    BytesIOBaseClass, CManBytesIOLike, FileOrPathLike, IterBytesIOLike, Path,
    TextIOBaseClass)

@contextmanager
def wrap(file: FileOrPathLike, mode: str = '') -> IterBytesIOLike:
    """Contextmanager to provide a unified interface to binary files.

    Args:
        file: String or `path-like object`_ that points to a valid filename in
            the directory structure of the system, or a `file-like object`_.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. The default mode is reading mode. Suported characters
            are:
            'r': Reading mode (default)
            'w': Writing mode

    Yields:
        `binary-file`_ in reading or writing mode.

    """
    # Get file handler from file-like or path-like objects
    if isinstance(file, TextIOBaseClass):
        raise RuntimeError(
            "wrapping text streams to byte streams is currently not supported")
    elif isinstance(file, BytesIOBaseClass):
        fd, close = file, False
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        if 'w' in mode:
            try:
                fd, close = open(path, 'wb'), True
            except IOError as err:
                raise IOError(f"file '{path}' can not be written") from err
        else:
            if not path.is_file():
                raise FileNotFoundError(f"file '{path}' is does not exist")
            fd, close = open(path, 'rb'), True
    else:
        raise TypeError(
            "first argument 'file' is required to be of types 'str', "
            f"'path-like' or 'file-like', not '{type(file).__name__}'")

    # Define enter and exit of context manager
    try:
        yield fd
    finally:
        if close:
            fd.close()

def open_read(file: FileOrPathLike) -> CManBytesIOLike:
    """Provide unified interface to read binary files.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        Context manager for `binary-file`_ in reading mode.

    """
    return wrap(file, mode='r')

def open_write(file: FileOrPathLike) -> CManBytesIOLike:
    """Provide unified interface to write binary files.

    Args:
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.

    Returns:
        Context manager for `binary-file`_ in writing mode.

    """
    return wrap(file, mode='w')
