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
"""Plain Text I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import io
from nemoa.io import FileConnector, FileInfo
from nemoa.types import StrList, Iterator, FileRef, OptStr

#
# Module Attributes
#

mime = "text/plain"

#
# Structural Types
#

IterTextIO = Iterator[io.TextIOBase]

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
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            or writing mode.
        mode: String, which characters specify the mode in which the file stream
            is wrapped. The default mode is reading mode. Suported characters
            are:
            'r': Reading mode (default)
            'w': Writing mode

    Yields:
        :term:`text file` in reading or writing mode.

    """
    cman = FileConnector(file)
    if 't' not in mode:
        mode += 't'
    fh = cman.open(mode=mode)
    if not isinstance(fh, io.TextIOBase):
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
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            or writing mode.

    Returns:
        Content of the given file as text.

    """
    with openx(file, mode='r') as fh:
        return fh.read()

def save(text: str, file: FileRef) -> None:
    """Save text to file.

    Args:
        text: Text given as string
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in writing
            mode.

    """
    with openx(file, mode='w') as fh:
        fh.write(text)

def get_comment(file: FileRef) -> str:
    """Read initial comment lines from :term:`text file`.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            mode.

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
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            mode.
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

def get_name(file: FileRef) -> OptStr:
    """Get name of referenced file object.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            or writing mode.

    Returns:
        String containing the name of the referenced file object or None if the
        name could not be determined.

    """
    return FileInfo(file).name
