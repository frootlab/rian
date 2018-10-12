# -*- coding: utf-8 -*-
"""I/O functions for Text-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _text-file:
    https://docs.python.org/3/glossary.html#term-text-file

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from contextlib import contextmanager
from io import TextIOWrapper

from nemoa.core import npath
from nemoa.types import (
    BytesIOBaseClass, CManStringIOLike, FileOrPathLike, IterStringIOLike, Path,
    StrList, StringIOLike, TextIOBaseClass)

@contextmanager
def wrap(file: FileOrPathLike, mode: str = '') -> IterStringIOLike:
    """Contextmanager to provide a unified interface to text files.

    Args:
        file: String or `path-like object`_ that points to a valid filename in
            the directory structure of the system, or a `file-like object`_.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. The default mode is reading mode. Suported characters
            are:
            'r': Reading mode (default)
            'w': Writing mode

    Yields:
        `text-file`_ in reading or writing mode.

    """
    # Get file handler from file-like or path-like objects
    if isinstance(file, TextIOBaseClass):
        fd, close = file, False
    elif isinstance(file, BytesIOBaseClass):
        if 'w' in mode:
            fd = TextIOWrapper(file, write_through=True)
        else:
            fd = TextIOWrapper(file)
        close = False
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        if 'w' in mode:
            try:
                fd = open(path, 'w')
            except IOError as err:
                raise IOError(f"file '{path}' can not be written") from err
        else:
            if not path.is_file():
                raise FileNotFoundError(f"file '{path}' does not exist")
            fd = open(path, 'r')
        close = True
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

def open_read(file: FileOrPathLike) -> CManStringIOLike:
    """Provide unified interface to read text files.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        Context manager for `text-file`_ in reading mode.

    """
    return wrap(file, mode='r')

def open_write(file: FileOrPathLike) -> CManStringIOLike:
    """Provide unified interface to write text files.

    Args:
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.

    Returns:
        Context manager for `text-file`_ in writing mode.

    """
    return wrap(file, mode='w')

def read_header(file: StringIOLike) -> str:
    """Read header comment from opened text-file.

    Args:
        file: `text-file`_ in read mode.

    Returns:
        String containing the header of given text-file.

    """
    lines = []
    for line in file:
        lstrip = line.lstrip() # Left strip line to keep linebreaks
        if not lstrip.rstrip(): # Discard blank lines
            continue
        if not lstrip.startswith('#'): # Stop if line is not a comment
            break
        lines.append(lstrip[1:].lstrip()) # Add comment lines to header
    return ''.join(lines).rstrip()

def read_content(file: StringIOLike, count: int = 0) -> StrList:
    """Read non empty, non comment lines from opened text-file.

    Args:
        file: `text-file`_ in read mode.
        count: Number of lines, that are returned. By default all lines are
            returned.

    Returns:
        List of strings containing non blank non conmment lines.

    """
    lines: StrList = []
    with open_read(file) as fd:
        for line in fd:
            if count and len(lines) >= count:
                break
            strip = line.strip()
            if not strip or strip.startswith('#'):
                continue
            lines.append(line.rstrip('\r\n'))
    return lines
