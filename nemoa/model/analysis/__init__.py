# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import catalog

def algorithms(*args, **kwds):
    """Returns dictionary of algorithms, that pass given filters. """
    return catalog.search_old(*args, **kwds)
