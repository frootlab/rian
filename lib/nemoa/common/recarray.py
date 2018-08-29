# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def insert(data, source, columns = None):
    """Append columns from source to data."""

    from numpy.lib.recfunctions import rec_append_fields

    if not columns: columns = source.dtype.names
    return rec_append_fields(data, columns, [source[col] for col in columns])
