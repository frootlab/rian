# -*- coding: utf-8 -*-
"""I/O functions for binary-files.

.. References:
.. _binary-file:
    https://docs.python.org/3/glossary.html#term-binary-file
.. _bytes-like object:
    https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _open():
    https://docs.python.org/3/library/functions.html#open
.. _zlib.compress():
    https://docs.python.org/3/library/zlib.html#zlib.compress
.. _zlib.decompress():
    https://docs.python.org/3/library/zlib.html#zlib.decompress
.. _RFC 3548:
    https://tools.ietf.org/html/rfc3548.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib

from nemoa.base import npath, binary
from nemoa.types import (
    BytesIOBaseClass, BytesLikeOrStr, FileOrPathLike,
    IterBytesIOLike, OptInt, OptStr, Path, TextIOBaseClass)

FILEEXTS = ['.gz', '.bin']

@contextlib.contextmanager
def openx(file: FileOrPathLike, mode: str = '') -> IterBytesIOLike:
    """Context manager to provide a unified interface to binary files.

    This context manager extends the standard implementation of `open()`_ by
    allowing the passed *file* argument to be a str or `path-like object`_,
    which points to a valid filename in the directory structure of the system,
    or a `file-like object`_. If the *file* argument is a str or a path-like
    object, the given path may contain application variables, like '%home%' or
    '%user_data_dir%', which are extended before returning a file handler to a
    `binary-file`_. Afterwards, when exiting the *with* statement, the file is
    closed. If the *file* argument, however, is a file-like object, the file is
    not closed, when exiting the *with* statement.

    Args:
        file: String or `path-like object`_ that points to a valid filename in
            the directory structure of the system, or a `file-like object`_.
        mode: String, which characters specify the mode in which the file stream
            is opened or wrapped. The default mode is reading mode. Suported
            characters are:
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
        path = npath.expand(file)
        if 'w' in mode:
            try:
                fd, close = open(path, 'wb'), True
            except IOError as err:
                raise IOError(f"file '{path}' is not writable") from err
        else:
            if not path.is_file():
                raise FileNotFoundError(f"file '{path}' does not exist")
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

def load(
        file: FileOrPathLike, encoding: OptStr = None,
        compressed: bool = False) -> bytes:
    """Load binary data from file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default no encoding is used.
        compressed: Boolean value which determines, if the returned binary
            data shall be decompressed by using `zlib.decompress()`_.

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
        data: BytesLikeOrStr, file: FileOrPathLike, encoding: OptStr = None,
        compression: OptInt = None) -> None:
    """Save binary data to file.

    Args:
        data: Binary data given as `bytes-like object`_ or string
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default no encoding is used.
        compression: Determines the compression level for `zlib.compress()`_.
            By default no zlib compression is used. For an integer ranging from
            -1 to 9, a zlib compression with the respective compression level is
            used. Thereby *-1* is the default zlib compromise between speed and
            compression, *0* deflates the given binary data without attempted
            compression, *1* is the fastest compression with minimum compression
            capability and *9* is the slowest compression with maximum
            compression capability.

    """
    if isinstance(compression, int):
        data = binary.compress(data, level=compression) # Compress data
    if encoding:
        data = binary.encode(data, encoding=encoding) # Encode data
    with openx(file, mode='w') as fh:
        fh.write(binary.asbytes(data)) # Save binary data to file
