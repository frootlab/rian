# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import base64
import pickle
import zlib

def dump(d, f, *args, **kwargs):
    """Compress and encode dictionary to file."""

    return pickle.dump(dumps(d, *args, **kwargs), file = open(f, 'wb'))

def dumps(d, level = 9, encode = 'base64'):
    """Compress and encode dictionary to string."""

    string = pickle.dumps(d)
    compressed = zlib.compress(string, level)

    if encode == 'base64': encoded = base64.b64encode(compressed)
    else: encoded = compressed

    return encoded

def load(f, *args, **kwargs):
    """Decode and decompress file to dictionary."""

    return loads(pickle.load(open(f, 'rb')), *args, **kwargs)

def loads(string, encode = 'base64'):
    """Decode and decompress string to dictionary."""

    if encode == 'base64': decoded = base64.b64decode(string)
    else: decoded = string

    decompressed = zlib.decompress(decoded)

    return pickle.loads(string_decompress)
