# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import cPickle
import gzip

def dict_merge(d1, d2):
    """return merged dictionary (merge d1 over d2)."""
    for k1,v1 in d1.iteritems():
        if not k1 in d2: d2[k1] = v1 # create in d2 if not existent
        elif isinstance(v1, dict): dict_merge(v1, d2[k1])
        else: d2[k1] = v1 # overwrite in d2 if allready there
    return d2

def dict_to_file(d, file):
    """Dump dictionary to gzip compressed file."""
    return cPickle.dump(obj = d,
        file = gzip.open(file, "wb"), protocol = 2)

def dict_from_file(file):
    """return dictionary from gzip compressed file."""
    return cPickle.load(gzip.open(file, 'rb'))

def dict_from_array(array, axes):
    """return dictionary from 2-dimensional numpy array."""
    return {(x, y): array[i, j] \
        for i, x in enumerate(axes[0]) \
        for j, y in enumerate(axes[1])}

def dict_to_array(d, axes):
    """return 2-dimensional numpy array from dictionary."""
    arr = numpy.zeros(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in emumerate(axes[1]):
            arr[i, j] = d[(x, y)] if (x, y) in dict else 0.
    return arr
