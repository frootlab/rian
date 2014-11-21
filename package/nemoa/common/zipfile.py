# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import cPickle
import gzip

def dump(d, f):
    """Dump dictionary to gzip compressed file."""
    h = gzip.open(f, 'wb')
    return cPickle.dump(obj = d, file = h, protocol = 2)

def load(f):
    """Return dictionary from gzip compressed file."""
    h = gzip.open(f, 'rb')
    return cPickle.load(h)
