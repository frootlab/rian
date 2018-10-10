# -*- coding: utf-8 -*-
"""I/O functions for Text files.

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

from nemoa.common import npath
from nemoa.types import (
    BytesIOBaseClass, Path, StrList,
    StringIOLike, IterStringIOLike, TextIOBaseClass, FileOrPathLike)

@contextmanager
def open_read(file: FileOrPathLike) -> IterStringIOLike:
    """Contextmanager to provide unified text file reading interface.

    Args:
        file: String, `path-like object`_ or `file-like object`_ that points to
            a valid text-file in the directory structure of the system.

    Yields:
        File descripter for text files in read mode.

    """
    # Get file descriptor from file-like or path-like objects
    if isinstance(file, TextIOBaseClass):
        fd, close = file, False
    elif isinstance(file, BytesIOBaseClass):
        fd, close = TextIOWrapper(file), False
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        if not path.is_file():
            raise FileNotFoundError(f"file '{path}' is does not exist")
        fd, close = open(path, 'r'), True
    else:
        raise TypeError(
            "first argument 'file' is required to be of types 'str', "
            f"'Path' or 'File', not '{type(file).__name__}'")

    # Define enter and exit of contextmanager
    try:
        yield fd
    finally:
        if close:
            fd.close()

@contextmanager
def open_write(file: FileOrPathLike) -> IterStringIOLike:
    """Contextmanager to provide unified text file writing interface.

    Args:
        file: String, `path-like object`_ or `file-like object`_ that points to
            a valid text-file in the directory structure of the system.

    Yields:
        File descripter for text files in write mode.

    """
    # Get file descriptor from file-like or path-like objects
    if isinstance(file, TextIOBaseClass):
        fd, close = file, False
    elif isinstance(file, BytesIOBaseClass):
        fd, close = TextIOWrapper(file, write_through=True), False
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        try:
            fd, close = open(path, 'w'), True
        except IOError as err:
            raise IOError(f"file '{path}' can not be written") from err
    else:
        raise TypeError(
            "first argument 'file' is required to be of types 'str', "
            f"'Path' or 'File', not '{type(file).__name__}'")

    # Define enter and exit of contextmanager
    try:
        yield fd
    finally:
        if close:
            fd.close()

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
        List of strings containing

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
