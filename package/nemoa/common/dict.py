#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cPickle, gzip, pprint

def dictMerge(d1, d2):
    """Return merged dictionary (merge d1 over d2)."""
    for k1,v1 in d1.iteritems():
        if not k1 in d2:
            d2[k1] = v1 # create in d2 if not existent
        elif isinstance(v1, dict):
            dictMerge(v1, d2[k1])
        else:
            d2[k1] = v1 # overwrite in d2 if allready there
    return d2

def dictToFile(dict, file):
    """Dump dictionary to gzip compressed file."""
    return cPickle.dump(obj = dict,
        file = gzip.open(file, "wb"), protocol = 2)

def dictFromFile(file):
    """Return dictionary from gzip compressed file."""
    return cPickle.load(gzip.open(file, 'rb'))

def printDict(dict):
    """Dump dictionary to standard output."""
    return pprint.pprint(dict)
