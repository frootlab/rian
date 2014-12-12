# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def merge(d1, d2):
    """Return merged dictionary (right merge d1 over d2)."""
    for k1, v1 in d1.iteritems():
        if not k1 in d2: d2[k1] = v1
        elif isinstance(v1, dict): merge(v1, d2[k1])
        else: d2[k1] = v1
    return d2

def keyjoinsum(*args):
    """Sum values of common keys in differnet dictionaries."""
    dsum = {}
    for d in args:
        if not isinstance(d, dict): continue
        for key, val in d.items():
            if not key in dsum: dsum[key] = val
            else: dsum[key] += val
    return dsum

def from_ndarray(array, axes):
    """Return dictionary from 2-dimensional numpy array."""
    return {(x, y): array[i, j] \
        for i, x in enumerate(axes[0]) \
        for j, y in enumerate(axes[1])}

def as_ndarray(d, axes):
    """Return 2-dimensional numpy array from dictionary."""
    arr = numpy.zeros(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in emumerate(axes[1]):
            arr[i, j] = d[(x, y)] if (x, y) in dict else 0.
    return arr

def as_string(d, level = 9, encode = 'base64'):
    """Encode dictionary to printable ascii-code."""

    import zlib

    string = cPickle.dumps(d)
    string_zlib = zlib.compress(string, level)

    if encode == 'base64':
        import base64
        string_encode = base64.b64encode(string_zlib)

    return string_encode

def from_string(string, encode = 'base64'):
    """Decode printable ascii-code to dictionary. """

    if encode == 'base64':
        import base64
        string_decode = base64.b64decode(string)

    import zlib
    string_decompress = zlib.decompress(string_decode)

    return cPickle.loads(string_decompress)

def convert_string_keys(d):
    """Convert dictionary keys from unicode to string."""

    if not isinstance(d, dict): return d
    d_str = {}
    for key, val in d.items():
        if isinstance(key, tuple):
            new_key = tuple([str(token) for token in key])
        else:
            new_key = str(key)
        d_str[new_key] = convert_string_keys(val)

    return d_str
