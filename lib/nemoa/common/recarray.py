# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as E: raise ImportError(
    "nemoa.common.recarray requires numpy: https://scipy.org") from E

def insert(data, source, columns = None):
    """Append columns from source to data."""

    from numpy.lib import recfunctions

    if not columns: columns = source.dtype.names
    return recfunctions.rec_append_fields(data, columns,
        [source[col] for col in columns])
