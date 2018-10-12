# -*- coding: utf-8 -*-
"""I/O functions for gzip compressed files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _bytes-like object:
    https://docs.python.org/3/glossary.html#term-bytes-like-object
.. _RFC3548:
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

FILEEXTS = ['.gz', '.tar.gz', '.zip']

def load(file: FileOrPathLike, encoding: OptStr = 'base64') -> Any:
    """Decode and decompress file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.
        encoding: Encodings specified in `RFC3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.

    Returns:
         Arbitry object hierarchy.

    """
    with binfile.open_read(file) as fd:
        blob = pickle.load(fd) # binary file to bytes
        # blob = fd.read() # binary file to bytes
    return loads(blob, encoding=encoding) # bytes to object

def dump(
        obj: object, file: FileOrPathLike, encoding: OptStr = 'base64',
        level: int = 6) -> None:
    """Compress and encode arbitrary object to file.

    Args:
        obj: Arbitrary object hierarchy
        file: String or `path-like object`_ that points to a writable file in
            the directory structure of the system, or a `file-like object`_ in
            writing mode.
        encoding: Encodings specified in `RFC3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.
        level: Compression level ranging from 0 to 9, with:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    """
    # Pickle object to bytes
    blob = dumps(obj, encoding=encoding, level=level)
    with binfile.open_write(file) as fd:
        pickle.dump(blob, fd) # bytes to file

def loads(blob: BytesLikeOrStr, encoding: OptStr = 'base64') -> Any:
    """Decode and decompress bytes-like object to object hierarchy.

    Args:
        blob: Encoded `bytes-like object`_ or string
        encoding: Encodings specified in `RFC3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.

    Returns:
         Arbitry object hierarchy.

    """
    # Decode bytes
    if not encoding:
        if isinstance(blob, str):
            bb = bytes(blob, encoding=nsysinfo.encoding())
        else:
            bb = bytes(blob)
    elif encoding in ['base64', 'base32', 'base16', 'base85']:
        bb = getattr(base64, f"b{encoding[4:]}decode")(blob)
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
        encoding: Encodings specified in `RFC3548`_. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default 'base64' encoding is used.
        level: Compression level ranging from 0 to 9, with:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    Returns:
        Compressed and encoded byte representation of given object hierachy.

    """
    blob = pickle.dumps(obj) # object to bytes
    blob = zlib.compress(blob, level) # compress bytes

    # Encode bytes
    if not encoding:
        return blob
    if encoding in ['base64', 'base32', 'base16', 'base85']:
        return getattr(base64, f"b{encoding[4:]}encode")(blob)

    raise ValueError(f"encoding '{encoding}' is not supported")
