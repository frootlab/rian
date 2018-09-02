# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def algorithms(**kwargs):
    """Returns list or dict of algorithms, that pass given filters. """

    from nemoa.common import module

    all = lambda a, b: frozenset(a) <= frozenset(b)
    any = lambda a, b: bool(frozenset(a) & frozenset(b))
    filters = {'tags': all, 'classes': any}

    return module.locate_functions(filters = filters, **kwargs)
