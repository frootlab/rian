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
"""Binary-file I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import io
from nemoa.base import binary
from nemoa.io import FileConnector
from nemoa.types import BytesLikeOrStr
from nemoa.types import OptInt, OptStr, FileRef, Iterator

#
# Structural Types
#

IterBytesIO = Iterator[io.BufferedIOBase]

#
# Functions
#

@contextlib.contextmanager
def openx(file: FileRef, mode: str = 'rb') -> IterBytesIO:
    """Context manager to provide a unified interface to binary files.

    This context manager extends the standard implementation of :py:func`open`
    by allowing the passed `file` argument to be a str or :term:`path-like
    object`, which points to a valid filename in the directory structure of the
    system, or a :term:`file object`. If the `file` argument is a str or a
    path-like object, the given path may contain application variables, like
    `%home%` or `%user_data_dir%`, which are extended before returning a file
    handler to a :term:`binary file`. Afterwards, when exiting the
    `with`-statement, the file is closed. If the *file* argument, however, is a
    :term:`file object`, the file is not closed, when exiting the
    `with`-statement.

    Args:
        file: String or :term:`path-like object` that points to a valid filename
            in the directory structure of the system, or a :term:`file object`.
        mode: String, which characters specify the mode in which the file stream
            is opened or wrapped. The default mode is reading mode. Suported
            characters are:
            'r': Reading mode (default)
            'w': Writing mode

    Yields:
        :term:`binary file` in reading or writing mode.

    """
    cman = FileConnector(file)
    if 'b' not in mode:
        mode += 'b'
    fh = cman.open(mode=mode)
    if not isinstance(fh, io.BufferedIOBase):
        cman.close()
        raise ValueError('the opened stream is not a valid binary file')
    # Define enter and exit of context manager
    try:
        yield fh
    finally:
        cman.close()

def load(
        file: FileRef, encoding: OptStr = None,
        compressed: bool = False) -> bytes:
    """Load binary data from file.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in reading mode.
        encoding: Encodings specified in :RFC:`3548`. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default no encoding is used.
        compressed: Boolean value which determines, if the returned binary
            data shall be decompressed by using :func:zlib.decompress.

    Returns:
        Content of the given file as bytes object.

    """
    with openx(file, mode='r') as fh:
        data = fh.read() # Load binary data from file
    if encoding:
        data = binary.decode(data, encoding=encoding) # Decode data
    if compressed:
        data = binary.decompress(data) # Decompress data
    return data

def save(
        data: BytesLikeOrStr, file: FileRef, encoding: OptStr = None,
        compression: OptInt = None) -> None:
    """Save binary data to file.

    Args:
        data: Binary data given as :term:`bytes-like object` or string
        file: String or :term:`path-like object` that points to a writable file
            in the directory structure of the system, or a :term:`file object`
            in writing mode.
        encoding: Encodings specified in :RFC:`3548`. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default no encoding is used.
        compression: Determines the compression level for
            :func:`zlib.compress`. By default no zlib compression is used.
            For an integer ranging from -1 to 9, a zlib compression with the
            respective compression level is used. Thereby *-1* is the default
            zlib compromise between speed and compression, *0* deflates the
            given binary data without attempted compression, *1* is the fastest
            compression with minimum compression capability and *9* is the
            slowest compression with maximum compression capability.

    """
    if isinstance(compression, int):
        data = binary.compress(data, level=compression) # Compress data
    if encoding:
        data = binary.encode(data, encoding=encoding) # Encode data
    with openx(file, mode='w') as fh:
        fh.write(binary.as_bytes(data)) # Save binary data to file
