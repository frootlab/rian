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

import dataclasses

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://pypi.org/project/numpy/") from err

from numpy.lib import recfunctions as nprf
from nemoa.base import check
from nemoa.base.container import DCMContainer, ContentAttr
from nemoa.base.container import MetadataAttr, VirtualAttr
from nemoa.types import NpFields, NpRecArray, Tuple, Iterable
from nemoa.types import Union, Optional, StrDict

# Module specific types
Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
Fields = Iterable[Union[str, Tuple[str, type], Tuple[str, type, Field]]]
FieldLike = Union[Fields, Tuple[str, type, StrDict]]
OptFieldLike = Optional[FieldLike]

class Table(DCMContainer):
    """Table Class."""

    _Record: property = MetadataAttr(type)
    _store: property = ContentAttr(list)

    _iter: property = MetadataAttr()

    fields: property = VirtualAttr(getter='_get_fields', readonly=True)

    def __init__(self, columns: OptFieldLike = None) -> None:
        """ """
        super().__init__()
        if columns:
            self._create_header(columns)

    def __iter__(self):
        self._iter = iter(self._store)
        return self._iter

    def __next__(self):
        return self._iter.next()

    def append(self, values: tuple) -> None:
        self._store.append(self._Record(*values))

    def _create_header(self, columns: FieldLike) -> None:
        """Create Record class for table."""
        # Check types of fieldlike column descriptors and convert them to field
        # descriptors, that are accepted by dataclasses.make_dataclass()
        fields: list = []
        for each in columns:
            if isinstance(each, str):
                fields.append(each)
                continue
            check.has_type(f"field {each}", each, tuple)
            # check.has_len(f"field {field}", field, min = 2, max = 3)
            check.has_type("first arg", each[0], str)
            check.has_type("second arg", each[1], type)
            if len(each) == 2:
                fields.append(each)
                continue
            check.has_type("third arg", each[2], (Field, dict))
            if isinstance(each[2], Field):
                fields.append(each)
                continue
            field = dataclasses.field(**each[2])
            fields.append(each[:2] + (field,))

        self._Record = dataclasses.make_dataclass('Record', fields)

        # Reset store
        self._store = []

    def as_tuples(self):
        """ """
        return [dataclasses.astuple(rec) for rec in self._store]

    def as_dicts(self):
        """ """
        return [dataclasses.asdict(rec) for rec in self._store]

    def as_array(self):
        """ """
        return np.array(self.as_tuples())

    def _get_fields(self) -> FieldTuple:
        return dataclasses.fields(self._Record)

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
