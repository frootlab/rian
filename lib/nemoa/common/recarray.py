# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as e: raise ImportError(
    "nemoa.common.recarray requires numpy: https://scipy.org") from e

def insert(data, source, columns = None):
    """Append columns from source to data."""

    from numpy.lib.recfunctions import rec_append_fields

    if not columns: columns = source.dtype.names
    return rec_append_fields(data, columns, [source[col] for col in columns])
