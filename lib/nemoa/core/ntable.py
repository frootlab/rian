# -*- coding: utf-8 -*-
"""NumPy recarray functions.

.. References:
.. _rec_append_fields:
    https://www.numpy.org/devdocs/user/basics.rec.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.types import NpFields, NpRecArray

def addcols(
        base: NpRecArray, data: NpRecArray,
        cols: NpFields = None) -> NpRecArray:
    """Add columns from source table to target table.

    Wrapper function to numpy's `rec_append_fields`_.

    Args:
        base: Numpy record array with table like data
        data: Numpy record array storing the fields to add to the base.
        cols: String or sequence of strings corresponding to the names of the
            new columns. If cols is None, then all columns of the data table
            are appended. Default: None

    Returns:
        Numpy record array containing the base array, as well as the
        appended columns.

    """
    from numpy.lib import recfunctions as rec

    cols = cols or getattr(data, 'dtype').names
    if not isinstance(cols, (tuple, str)):
        raise TypeError(
            "argument 'cols' requires to be of type 'tuple' or 'str'"
            f", not '{type(cols)}'")

    cols = list(cols) # make cols mutable

    # Append fields
    return rec.rec_append_fields(base, cols, [data[c] for c in cols])
