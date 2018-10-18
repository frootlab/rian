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
__all__ = ['openx', 'load', 'save', 'get_header', 'get_content']

import contextlib

from io import TextIOWrapper

from nemoa.core import npath
from nemoa.types import (
    BytesIOBaseClass, FileOrPathLike, IterStringIOLike, Path,
    StrList, TextIOBaseClass)

FILEEXTS = ['.txt']

@contextlib.contextmanager
def openx(file: FileOrPathLike, mode: str = '') -> IterStringIOLike:
    """Contextmanager to provide a unified interface to text files.

    This context manager extends the standard implementation of `open()`_ by
    allowing the passed *file* argument to be a str or `path-like object`_,
    which points to a valid filename in the directory structure of the system,
    or a `file-like object`_. If the *file* argument is a str or a path-like
    object, the given path may contain application variables, like '%home%' or
    '%user_data_dir%', which are extended before returning a file handler to a
    `text-file`_. Afterwards, when exiting the *with* statement, the file is
    closed. If the *file* argument, however, is a file-like object, the file is
    not closed, when exiting the *with* statement.

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
        fh, close = file, False
    elif isinstance(file, BytesIOBaseClass):
        if 'w' in mode:
            fh = TextIOWrapper(file, write_through=True)
        else:
            fh = TextIOWrapper(file)
        close = False
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        if 'w' in mode:
            try:
                fh = open(path, 'w')
            except IOError as err:
                raise IOError(f"file '{path}' can not be written") from err
        else:
            if not path.is_file():
                raise FileNotFoundError(f"file '{path}' does not exist")
            fh = open(path, 'r')
        close = True
    else:
        raise TypeError(
            "first argument 'file' is required to be of type 'str', "
            f"'path-like' or 'file-like', not '{type(file).__name__}'")

    try: # Enter 'with' statement
        yield fh
    finally: # Exit 'with' statement
        if close:
            fh.close()

def load(file: FileOrPathLike) -> str:
    """Load text from file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        Content of the given file as text.

    """
    with openx(file, mode='r') as fh:
        return fh.read()

def save(text: str, file: FileOrPathLike) -> None:
    """Save text to file.

    Args:
        text: Text given as string
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.

    """
    with openx(file, mode='w') as fh:
        fh.write(text)

def get_header(file: FileOrPathLike) -> str:
    """Read header comment from text-file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        String containing the header of given text-file.

    """
    lines = []
    with openx(file) as fh:
        for line in fh:
            lstrip = line.lstrip() # Left strip line to keep linebreaks
            if not lstrip.rstrip(): # Discard blank lines
                continue
            if not lstrip.startswith('#'): # Stop if line is not a comment
                break
            lines.append(lstrip[1:].lstrip()) # Add comment lines to header
    return ''.join(lines).rstrip()

def get_content(file: FileOrPathLike, lines: int = 0) -> StrList:
    """Read non-blank non-comment lines from text-file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.
        lines: Number of content lines, that are returned. By default all lines
            are returned.

    Returns:
        List of strings containing non-blank non-comment lines.

    """
    content: StrList = []
    with openx(file) as fh:
        for line in fh:
            if lines and len(content) >= lines:
                break
            strip = line.strip()
            if not strip or strip.startswith('#'):
                continue
            content.append(line.rstrip('\r\n'))
    return content
