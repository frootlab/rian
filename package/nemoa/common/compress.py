# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
   import cPickle as pickle
except:
   import pickle

import zlib

def dump(d, f, *args, **kwargs):
    """Dump dictionary to compressed and encoded file."""

    return pickle.dump(dumps(d, *args, **kwargs), file = open(f, 'wb'))

def dumps(d, level = 9, encode = 'base64'):
    """Dump dictionary to compressed and encoded string."""

    string = pickle.dumps(d)
    string_compress = zlib.compress(string, level)

    if encode == 'base64':
        import base64
        string_encode = base64.b64encode(string_compress)

    return string_encode

def load(f, *args, **kwargs):
    """Decode and decompress file to dictionary. """

    return loads(pickle.load(open(f, 'rb')), *args, **kwargs)

def loads(string, encode = 'base64'):
    """Decode and decompress string to dictionary. """

    if encode == 'base64':
        import base64
        string_decode = base64.b64decode(string)

    string_decompress = zlib.decompress(string_decode)

    return pickle.loads(string_decompress)
