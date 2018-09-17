# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def algorithms(*args, **kwargs):
    """Returns dictionary of algorithms, that pass given filters. """

    from nemoa.common import nalgorithm
    return nalgorithm.search(*args, **kwargs)
