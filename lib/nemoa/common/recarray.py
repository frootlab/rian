# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import numpy.lib.recfunctions

def insert(data, source, columns = None):
    """Append columns from source to data."""

    if not columns: columns = source.dtype.names
    return numpy.lib.recfunctions.rec_append_fields(
        data, columns, [source[col] for col in columns])
