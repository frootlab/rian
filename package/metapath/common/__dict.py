# -*- coding: utf-8 -*-

def dictMerge(d1, d2):
    """Return merged dictionary."""
    for k1,v1 in d1.iteritems():
        if not k1 in d2:
            d2[k1] = v1 # create in d2 if not existent
        elif isinstance(v1, dict):
            dictMerge(v1, d2[k1])
        else:
            d2[k1] = v1 # overwrite in d2 if allready there
    return d2
