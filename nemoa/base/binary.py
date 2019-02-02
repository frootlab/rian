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
"""Binary object functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import base64
import pickle
import zlib
from nemoa.base import env
from nemoa.types import Any, BytesLikeOrStr, OptInt, OptStr

#
# Module Functions
#

def as_bytes(data: BytesLikeOrStr, encoding: OptStr = None) -> bytes:
    """Convert bytes-like object or str to bytes.

    Args:
        data: Binary data given as :term:`bytes-like object` or string

    """
    if isinstance(data, str):
        encoding = encoding or env.get_encoding()
        return bytes(data, encoding=encoding)
    return bytes(data)

def compress(data: BytesLikeOrStr, level: int = -1) -> bytes:
    """Compress binary data using the gzip standard.

    Args:
        data: Binary data given as :term:`bytes-like object` or string.
        level: Compression level ranging from *-1* to *9*, where the default
            value of *-1* is a compromise between speed and compression. For
            level *0* the given binary data is deflated without attempted
            compression, *1* denotes the fastest compression with minimum
            compression capability and *9* the slowest compression with maximum
            compression capability.

    Returns:
         Binary data as bytes.

    """
    return zlib.compress(as_bytes(data), level=level)

def decompress(data: BytesLikeOrStr) -> bytes:
    """Decompress gzip compressed binary data.

    Args:
        data: Binary data given as :term:`bytes-like object` or string.

    Returns:
         Binary data as bytes.

    """
    try:
        data = zlib.decompress(as_bytes(data))
    except zlib.error:
        raise ValueError("'data' is not gzip compressed")

    return data

def encode(data: BytesLikeOrStr, encoding: OptStr = None) -> bytes:
    """Encode bytes-like object or str.

    Args:
        data: Binary data given as :term:`bytes-like object` or string
        encoding: Encodings specified in :rfc:`3548`. Allowed values are:
            *base16*, *base32*, *base64* and *base85* or None for no encoding.
            By default no encoding is used.

    Returns:
         Binary data as bytes.

    """
    # Encode binary data
    if not encoding:
        return as_bytes(data)
    if encoding in ['base64', 'base32', 'base16', 'base85']:
        return getattr(base64, f"b{encoding[4:]}encode")(as_bytes(data))
    raise ValueError(f"encoding '{encoding}' is not supported")

def decode(
        data: BytesLikeOrStr, encoding: OptStr = None,
        compressed: bool = False) -> bytes:
    """Decode bytes-like object or str.

    Args:
        data: Binary data given as :term:`bytes-like object` or string
        encoding: Encodings specified in :rfc:`3548`. Allowed values are:
            *base16*, *base32*, *base64* and *base85* or None for no encoding.
            By default no encoding is used.

    Returns:
         Binary data as bytes.

    """
    if not encoding:
        return as_bytes(data)
    if encoding in ['base64', 'base32', 'base16', 'base85']:
        return getattr(base64, f"b{encoding[4:]}decode")(data)
    raise ValueError(f"encoding '{encoding}' is not supported")

def pack(
        obj: object, encoding: OptStr = None,
        compression: OptInt = None) -> bytes:
    """Compress and encode arbitrary object to bytes.

    Args:
        obj: Any object, that can be pickled
        encoding: Encodings specified in :rfc:`3548`. Allowed values are:
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

    Returns:
        Compressed and encoded byte representation of given object hierachy.

    """
    data = pickle.dumps(obj) # Pickle object to binary data
    if isinstance(compression, int):
        data = compress(data, level=compression) # Compress data
    if encoding:
        data = encode(data, encoding=encoding) # Encode data
    return data

def unpack(
        data: BytesLikeOrStr, encoding: OptStr = None,
        compressed: bool = False) -> Any:
    """Decompress and decode object from binary data.

    Args:
        data: Binary data given as :term:`bytes-like object` or string.
        encoding: Encodings specified in :rfc:`3548`. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' or None for no encoding.
            By default no encoding is used.
        compressed: Boolean value which determines, if the returned binary
            data shall be decompressed by using :func:`zlib.decompress`.

    Returns:
         Arbitry object, that can be pickled.

    """
    if encoding:
        data = decode(data, encoding=encoding) # Decode binary data to bytes
    if compressed:
        data = decompress(data) # Decompress bytes
    return pickle.loads(as_bytes(data)) # Unpickle object from bytes
