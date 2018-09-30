# -*- coding: utf-8 -*-
"""I/O functions for gzip compressed files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import base64
import pickle
import zlib

from typing import cast
from nemoa.common import npath
from nemoa.types import Any, Obj, OptStr, PathLike, BytesLikeOrStr

FILEEXTS = ['.zip', '.gz', '.tar.gz']

def load(filepath: PathLike, encoding: OptStr = 'base64') -> dict:
    """Decode and decompress file.

    Args:
        filepath: Fully qualified filepath
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'

    Returns:
         Reconstituted object specified within the encoded file.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """
    # Validate filepath
    path = npath.validfile(filepath)
    if not path:
        raise TypeError(f"file '{str(filepath)}' does not exist")

    blob = pickle.load(open(path, 'rb')) # file to bytes
    obj = loads(blob, encoding=encoding) # bytes to object

    return obj

def dump(
        obj: Obj, path: str, encoding: OptStr = 'base64',
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
    blob = dumps(obj, encoding=encoding, level=level) # object to bytes
    pickle.dump(blob, file=open(path, 'wb')) # bytes to file

    return True

def loads(blob: BytesLikeOrStr, encoding: OptStr = 'base64') -> Any:
    """Decode and decompress bytes-like object to object hierarchy.

    Args:
        blob: Encoded byte-like objects
        encoding: Encodings specified in [RFC3548]. Allowed values are:
            'base16', 'base32', 'base64' and 'base85' and None for no encoding.
            Default: 'base64'

    Returns:
         Reconstituted object specified within the encoded bytes-like
         object or string.

    References:
        [RFC3548] https://tools.ietf.org/html/rfc3548.html

    """
    # Decode bytes
    if not encoding:
        bbytes = bytes(cast(bytes, blob))
    elif encoding == 'base64':
        bbytes = base64.b64decode(blob)
    elif encoding == 'base32':
        bbytes = base64.b32decode(blob)
    elif encoding == 'base16':
        bbytes = base64.b16decode(blob)
    elif encoding == 'base85':
        bbytes = base64.b85decode(blob)
    else:
        raise ValueError(f"encoding '{encoding}' is not supported")

    # Decompress bytes, level is not required
    bbytes = zlib.decompress(bbytes)
    obj = pickle.loads(bbytes) # bytes to object

    return obj

def dumps(obj: Obj, encoding: OptStr = 'base64', level: int = 6) -> bytes:
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
    blob = pickle.dumps(obj) # object to bytes
    blob = zlib.compress(blob, level) # compress bytes

    # Encode bytes
    if not encoding:
        pass
    elif encoding == 'base64':
        blob = base64.b64encode(blob)
    elif encoding == 'base32':
        blob = base64.b32encode(blob)
    elif encoding == 'base16':
        blob = base64.b16encode(blob)
    elif encoding == 'base85':
        blob = base64.b85encode(blob)
    else:
        raise ValueError(f"encoding '{encoding}' is not supported")

    return blob
