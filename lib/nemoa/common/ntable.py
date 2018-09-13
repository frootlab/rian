# -*- coding: utf-8 -*-
"""Collection of frequently used numpy recarray functions."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Optional, Sequence, Union

try: import numpy as np
except ImportError as err: raise ImportError(
    "requires package numpy: "
    "https://scipy.org") from err

Table = np.recarray
Cols = Union[str, Sequence[str]]

def addcols(base: Table, data: Table, cols: Optional[Cols] = None) -> Table:
    """Add columns from source table to target table.

    Wrapper function to numpy's rec_append_fields [1].

    Args:
        base: Numpy record array with table like data
        data: Numpy record array storing the fields to add to the base.
        cols: String or sequence of strings corresponding to the names of the
            new columns.

    Returns:
        Numpy record array containing the base array, as well as the
        appended columns.

    References:
        [1] https://www.numpy.org/devdocs/user/basics.rec.html

    """

    from numpy.lib import recfunctions

    if not cols: cols = data.dtype.names
    elif not isinstance(cols, (tuple, str)): raise TypeError(
        "argument 'cols' requires to be of type 'tuple' or 'str'"
        f", not '{type(cols)}'")

    cols = list(cols) # make cols mutable
    r = recfunctions.rec_append_fields(base, cols, [data[c] for c in cols])

    return r
