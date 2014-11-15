# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import base64
import zlib

def dict_merge(d1, d2):
    """Return merged dictionary (right merge d1 over d2)."""
    for k1, v1 in d1.iteritems():
        if not k1 in d2: d2[k1] = v1
        elif isinstance(v1, dict): dict_merge(v1, d2[k1])
        else: d2[k1] = v1
    return d2

def dict_sum(*args):
    """Sum values of common keys in differnet dictionaries."""
    dsum = {}
    for d in args:
        if not isinstance(d, dict): continue
        for key, val in d.items():
            if not key in dsum: dsum[key] = val
            else: dsum[key] += val
    return dsum

def dict_from_array(array, axes):
    """Return dictionary from 2-dimensional numpy array."""
    return {(x, y): array[i, j] \
        for i, x in enumerate(axes[0]) \
        for j, y in enumerate(axes[1])}

def dict_to_array(d, axes):
    """Return 2-dimensional numpy array from dictionary."""
    arr = numpy.zeros(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in emumerate(axes[1]):
            arr[i, j] = d[(x, y)] if (x, y) in dict else 0.
    return arr

def dict_encode_base64(d, level = 9):
    """Encode dictionary to printable ascii-code. """
    string = cPickle.dumps(d)
    string_zlib = zlib.compress(string, level)
    string_base64 = base64.b64encode(string_zlib)
    return string_base64

def dict_decode_base64(string_base64):
    """Decode printable ascii-code to dictionary. """
    string_zlib = base64.b64decode(string_base64)
    string = zlib.decompress(string_zlib)
    d = cPickle.loads(string)
    return d

def dict_convert_string_keys(d):
    """Convert dictionary keys from unicode to string."""
    if not isinstance(d, dict): return d
    d_str = {}
    for key, val in d.items():
        if isinstance(key, tuple):
            new_key = tuple([str(token) for token in key])
        else:
            new_key = str(key)
        d_str[new_key] = dict_convert_string_keys(val)
    return d_str
