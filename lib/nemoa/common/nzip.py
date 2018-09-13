# -*- coding: utf-8 -*-
"""Collection of frequently used functions for gzip compressed data handling."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Optional, Union

import base64
import pickle
import zlib

ByteLike = Union[bytes, bytearray, str]

def load(path: str, encoding: Optional[str] = 'base64') -> dict:
    """Decode and decompress file.

    Args:
        path: Fully qualified filepath
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'

    Returns:
         Reconstituted object specified within the encoded file.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """

    s = pickle.load(open(path, 'rb')) # file to bytes
    obj = loads(s, encoding = encoding) # bytes to object

    return obj

def dump(obj: object, path: str, encoding: Optional[str] = 'base64',
    level: int = 6) -> bool:
    """Compress and encode arbitrary object to file.

    Args:
        obj: Arbitrary object
        path: Fully qualified filepath
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'
        level: compression level ranging from 0 to 9. Thereby:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    Returns:
        True if no exception has been raised.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """

    s = dumps(obj, encoding = encoding, level = level) # object to bytes
    pickle.dump(s, file = open(path, 'wb')) # bytes to file

    return True

def loads(s: ByteLike, encoding: Optional[str] = 'base64') -> Any:
    """Decode and decompress bytes-like object to object hierarchy.

    Args:
        s: Encoded bytes-like structure or string
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'

    Returns:
         Reconstituted object specified within the encoded bytes-like
         object or string.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """

    # decode bytes
    if not encoding: pass
    elif encoding == 'base64': s = base64.b64decode(s)
    elif encoding == 'base32': s = base64.b32decode(s)
    elif encoding == 'base16': s = base64.b16decode(s)
    elif encoding == 'base85': s = base64.b85decode(s)
    else: raise ValueError(f"encoding '{encoding}' is not supported")

    s = zlib.decompress(s) # decompress bytes, level is not required
    obj = pickle.loads(s) # bytes to object

    return obj

def dumps(obj: object, encoding: Optional[str] = 'base64',
    level: int = 6) -> bytes:
    """Compress and encode arbitrary object to bytes.

    Args:
        obj: Arbitrary object
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'
        level: compression level ranging from 0 to 9. Thereby:
            0: no compression
            1: fastest, produces the least compression
            9: slowest, produces the most compression

    Returns:
        Compressed and encoded byte representation of the object.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """

    s = pickle.dumps(obj) # object to bytes
    s = zlib.compress(s, level) # compress bytes

    # encode bytes
    if not encoding: pass
    elif encoding == 'base64': s = base64.b64encode(s)
    elif encoding == 'base32': s = base64.b32encode(s)
    elif encoding == 'base16': s = base64.b16encode(s)
    elif encoding == 'base85': s = base64.b85encode(s)
    else: raise ValueError(f"encoding '{encoding}' is not supported")

    return s
