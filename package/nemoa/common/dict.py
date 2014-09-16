# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import cPickle
import gzip
import pprint

def dictMerge(d1, d2):
    """Return merged dictionary (merge d1 over d2)."""
    for k1,v1 in d1.iteritems():
        if not k1 in d2: d2[k1] = v1 # create in d2 if not existent
        elif isinstance(v1, dict): dictMerge(v1, d2[k1])
        else: d2[k1] = v1 # overwrite in d2 if allready there
    return d2

def dictToFile(dict, file):
    """Dump dictionary to gzip compressed file."""
    return cPickle.dump(obj = dict,
        file = gzip.open(file, "wb"), protocol = 2)

def dictFromFile(file):
    """Return dictionary from gzip compressed file."""
    return cPickle.load(gzip.open(file, 'rb'))

def dictFromArray(array, axes):
    """Return dictionary from 2-dimensional numpy array."""
    return {(x, y): array[i, j] \
        for i, x in enumerate(axes[0]) \
        for j, y in enumerate(axes[1])}

def dictToArray(dict, axes):
    """Return 2-dimensional numpy array from dictionary."""
    arr = numpy.zeros(shape = (len(axes[0]), len(axes[1])))
    for i, x in enumerate(axes[0]):
        for j, y in emumerate(axes[1]): arr[i, j] = dict[(x, y)] \
            if (x, y) in dict else 0.0
    return arr

def printDict(dict):
    """Dump dictionary to standard output."""
    return pprint.pprint(dict)
