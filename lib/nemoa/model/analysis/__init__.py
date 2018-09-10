# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def algorithms(**kwargs):
    """Returns dictionary of algorithms, that pass given filters. """

    from nemoa.common import nmodule

    all = lambda a, b: set(a) <= set(b)
    any = lambda a, b: bool(set(a) & set(b))
    filters = {'tags': all, 'classes': any}

    return nmodule.findfuncs(filters = filters, **kwargs)
