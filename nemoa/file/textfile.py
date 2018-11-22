# -*- coding: utf-8 -*-
"""Text-file I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
from nemoa.file import stream
from nemoa.types import StrList, TextIOBaseClass, Iterator, FileRef

#
# Structural Types
#

IterTextIO = Iterator[TextIOBaseClass]

#
# Functions
#

@contextlib.contextmanager
def openx(file: FileRef, mode: str = 'rt') -> IterTextIO:
    """Contextmanager to provide a unified interface to text files.

    This context manager extends the standard implementation of :func:`open`
    by allowing the passed argument `file` to be a str or :term:`path-like
    object`, which points to a valid filename in the directory structure of the
    system, or a :term:`file object`. If the *file* argument is a str or a
    path-like object, the given path may contain application variables, like
    '%home%' or '%user_data_dir%', which are extended before returning a file
    handler to a :term:`text file`. Afterwards, when exiting the *with*
    statement, the file is closed. If the argument `file`, however, is a
    :term:`file-like object`, the file is not closed, when exiting the *with*
    statement.

    Args:
        file: String or :term:`path-like object` that points to a valid filename
            in the directory structure of the system, or a :term:`file object`.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. The default mode is reading mode. Suported characters
            are:
            'r': Reading mode (default)
            'w': Writing mode

    Yields:
        :term:`text file` in reading or writing mode.

    """
    cman = stream.Connector(file)
    if 't' not in mode:
        mode += 't'
    fh = cman.open(mode=mode)
    if not isinstance(fh, TextIOBaseClass):
        cman.close()
        raise ValueError('the opened stream is not a valid text file')
    # Define enter and exit of context manager
    try:
        yield fh
    finally:
        cman.close()

def load(file: FileRef) -> str:
    """Load text from file.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in reading mode.

    Returns:
        Content of the given file as text.

    """
    with openx(file, mode='r') as fh:
        return fh.read()

def save(text: str, file: FileRef) -> None:
    """Save text to file.

    Args:
        text: Text given as string
        file: String or :term:`path-like object` that points to a writable file
            in the directory structure of the system, or a :term:`file object`
            in writing mode.

    """
    with openx(file, mode='w') as fh:
        fh.write(text)

def get_comment(file: FileRef) -> str:
    """Read initial comment lines from :term:`text file`.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in reading mode.

    Returns:
        String containing the header of given text file.

    """
    lines = []
    with openx(file, mode='r') as fh:
        for line in fh:
            lstrip = line.lstrip() # Left strip line to keep linebreaks
            if not lstrip.rstrip(): # Discard blank lines
                continue
            if not lstrip.startswith('#'): # Stop if line is not a comment
                break
            lines.append(lstrip[1:].lstrip()) # Add comment lines to header
    return ''.join(lines).rstrip()

def get_content(file: FileRef, lines: int = 0) -> StrList:
    """Read non-blank non-comment lines from :term:`text file`.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in reading mode.
        lines: Number of content lines, that are returned. By default all lines
            are returned.

    Returns:
        List of strings containing non-blank non-comment lines.

    """
    content: StrList = []
    with openx(file, mode='r') as fh:
        for line in fh:
            if lines and len(content) >= lines:
                break
            strip = line.strip()
            if not strip or strip.startswith('#'):
                continue
            content.append(line.rstrip('\r\n'))
    return content
