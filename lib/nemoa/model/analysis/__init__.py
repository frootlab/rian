# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def algorithms(**kwargs):
    from nemoa.common.module import search_functions
    subset = lambda a, b: frozenset(a) <= frozenset(b)
    return search_functions(filters = {'tags': subset}, **kwargs)
