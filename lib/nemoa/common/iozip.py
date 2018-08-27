# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import base64
import pickle
import zlib

def load(f: str, *args, **kwargs) -> dict:
    """Decode and decompress file to dictionary."""

    return loads(pickle.load(open(f, 'rb')), *args, **kwargs)

def dump(d: dict, f: str, *args, **kwargs) -> None:
    """Compress and encode dictionary to file."""

    s = dumps(d, *args, **kwargs)

    return pickle.dump(s, file = open(f, 'wb'))

def loads(s: str, encode: str = 'base64') -> dict:
    """Decode and decompress string to dictionary."""

    if encode == 'base64': decode = base64.b64decode(s)
    else: decode = s

    return pickle.loads(zlib.decompress(decode))

def dumps(d: dict, level: int = 9, encode: str = 'base64') -> str:
    """Compress and encode dictionary to string."""

    s = pickle.dumps(d)
    compressed = zlib.compress(s, level)

    if encode == 'base64': encoded = base64.b64encode(compressed)
    else: encoded = compressed

    return encoded
