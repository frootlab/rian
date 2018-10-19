# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def algorithms(*args, **kwds):
    """Returns dictionary of algorithms, that pass given filters. """
    from nemoa.math import algo
    return algo.search(*args, **kwds)
