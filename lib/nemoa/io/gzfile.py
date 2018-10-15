# -*- coding: utf-8 -*-
"""I/O functions for gzip compressed files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _bytes-like object:
    https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _RFC 3548:
    https://tools.ietf.org/html/rfc3548.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import base64
import pickle
import zlib

from nemoa.core import nsysinfo
from nemoa.io import binfile
from nemoa.types import Any, FileOrPathLike, OptStr, BytesLikeOrStr

FILEEXTS = ['.gz', '.bin']

def load(file: FileOrPathLike, encoding: OptStr = 'base64') -> Any:
    """Decode and decompress file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.

    Returns:
         Arbitry object hierarchy.

    """
    with binfile.openx(file, mode='r') as fh:
        data = pickle.load(fh) # read binary data from file
    return loads(data, encoding=encoding) # bytes to object

def dump(
        obj: object, file: FileOrPathLike, encoding: OptStr = 'base64',
        level: int = 6) -> None:
    """Save object hierarchy to compressed binary file.

    Args:
        obj: Arbitrary object hierarchy
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.
        level: Compression level ranging from 0 to 9, with:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    """
    # Pickle object to binary data
    data = dumps(obj, encoding=encoding, level=level)
    with binfile.openx(file, mode='w') as fd:
        pickle.dump(data, fd) # bytes to file

def loads(data: BytesLikeOrStr, encoding: OptStr = 'base64') -> Any:
    """Decode and decompress bytes-like object to object hierarchy.

    Args:
        data: Binary data given as `bytes-like object`_ or string
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.

    Returns:
         Arbitry object hierarchy.

    """
    # Decode bytes
    if not encoding:
        if isinstance(data, str):
            bb = bytes(data, encoding=nsysinfo.encoding())
        else:
            bb = bytes(data)
    elif encoding in ['base64', 'base32', 'base16', 'base85']:
        bb = getattr(base64, f"b{encoding[4:]}decode")(data)
    else:
        raise ValueError(f"encoding '{encoding}' is not supported")

    # Decompress bytes, level is not required
    bb = zlib.decompress(bb)

    # Bytes to object
    return pickle.loads(bb)

def dumps(obj: object, encoding: OptStr = 'base64', level: int = 6) -> bytes:
    """Compress and encode arbitrary object to bytes.

    Args:
        obj: Arbitrary object hierarchy
        encoding: Encodings specified in `RFC 3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.
        level: Compression level ranging from 0 to 9, with:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    Returns:
        Compressed and encoded byte representation of given object hierachy.

    """
    data = pickle.dumps(obj) # object to bytes
    data = zlib.compress(data, level) # compress bytes

    # Encode bytes
    if not encoding:
        return data
    if encoding in ['base64', 'base32', 'base16', 'base85']:
        return getattr(base64, f"b{encoding[4:]}encode")(data)

    raise ValueError(f"encoding '{encoding}' is not supported")
