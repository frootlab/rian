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

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://pypi.org/project/numpy/") from err

from numpy.lib import recfunctions as nprf
from nemoa.base import check
from nemoa.base.container import BaseContainer, ContentAttr, VirtualAttr
from nemoa.types import Any, NpFields, NpRecArray, StrTuple

# class Table(BaseContainer):
#     """Table Class."""
#
#     _rows: property = ContentAttr(list)
#     _columns: property = MetadataAttr(tuple)
#
#     def __init__(self, columns: tuple) -> None:
#         super().__init__()

    # def create

#    colnames: property = VirtualAttr(getter='_get_colnames', readonly=True)
    #
    # def __new__(cls, *args, **kwds):
    #     # Create the ndarray instance of our type, given the usual
    #     # ndarray input arguments. This will call the standard
    #     # ndarray constructor, but return an object of our type.
    #     # It also triggers a call to InfoArray.__array_finalize__
    #     obj = super().__new__(cls, *args, **kwds)
    #     # set the new 'info' attribute to the value passed
    #     obj.info = 'hi'
    #     # Finally, we must return the newly created object:
    #     return obj
    #
    # def _get_colnames(self) -> StrTuple:
    #     return nprf.get_names(self.dtype)
    #
    # def __array_finalize__(self, obj):
    #     # ``self`` is a new object resulting from
    #     # ndarray.__new__(InfoArray, ...), therefore it only has
    #     # attributes that the ndarray.__new__ constructor gave it -
    #     # i.e. those of a standard ndarray.
    #     #
    #     # We could have got to the ndarray.__new__ call in 3 ways:
    #     # From an explicit constructor - e.g. InfoArray():
    #     #    obj is None
    #     #    (we're in the middle of the InfoArray.__new__
    #     #    constructor, and self.info will be set when we return to
    #     #    InfoArray.__new__)
    #     if obj is None:
    #         return
    #     # From view casting - e.g arr.view(InfoArray):
    #     #    obj is arr
    #     #    (type(obj) can be InfoArray)
    #     # From new-from-template - e.g infoarr[:3]
    #     #    type(obj) is InfoArray
    #     #
    #     # Note that it is here, rather than in the __new__ method,
    #     # that we set the default value for 'info', because this
    #     # method sees all creation of default objects - with the
    #     # InfoArray.__new__ constructor, but also with
    #     # arr.view(InfoArray).
    #     self.info = getattr(obj, 'info', None)
    #     # We do not need to return anything
    #
    #
    # def append_fields(self, *args, **kwds):
    #     """Add new fields to an existing array.
    #
    #     The names of the fields are given with the `names` arguments,
    #     the corresponding values with the `data` arguments.
    #     If a single field is appended, `names`, `data` and `dtypes` do not have
    #     to be lists but just values.
    #     """
    #     return nprf.append_fields(self, *args, **kwds)

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
    cols = cols or getattr(data, 'dtype').names
    check.has_type("argument 'cols'", cols, (tuple, str))
    cols = list(cols) # make cols mutable

    # Append fields
    return nprf.rec_append_fields(base, cols, [data[c] for c in cols])
