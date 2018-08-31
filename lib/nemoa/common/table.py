# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as E: raise ImportError(
    "nemoa.common.table requires numpy: https://scipy.org") from E

from typing import Optional, Tuple

Table = numpy.recarray

def addcols(base: Table, data: Table,
    cols: Optional[Tuple[str]] = None) -> Table:
    """Add columns from source table to target table.

    Wrapper function to numpy.lib.recfunctions.rec_append_fields:
    https://www.numpy.org/devdocs/user/basics.rec.html

    Args:
        base (recarray): Numpy record array with table like data
        data (recarray): Numpy record array storing the fields
            to add to the base.
        cols (tuple of string or None, optional): String or sequence
            of strings corresponding to the names of the new columns.

    Returns:
        Numpy record array containing the base array, as well as the
        appended columns.

    """

    from numpy.lib import recfunctions

    if not cols: cols = data.dtype.names
    if isinstance(cols, (tuple, str)): cols = list(cols)
    else:
        raise TypeError("cols requires type 'tuple' or 'str', "
            f"not '{type(names)}'")

    r = recfunctions.rec_append_fields(base, cols, [data[c] for c in cols])

    return r
