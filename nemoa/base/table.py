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

# try:
#     import numpy as np
# except ImportError as err:
#     raise ImportError(
#         "requires package numpy: "
#         "https://pypi.org/project/numpy/") from err

from numpy.lib import recfunctions as nprf
from nemoa.base import check
from nemoa.base.container import DCMContainer, ContentAttr
from nemoa.base.container import VirtualAttr, TransientAttr
from nemoa.types import NpFields, NpRecArray, Tuple, Iterable, void
from nemoa.types import Union, Optional, StrDict, StrTuple, Iterator, Any

# Module specific types
Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
Fields = Iterable[Union[str, Tuple[str, type], Tuple[str, type, Field]]]
FieldLike = Union[Fields, Tuple[str, type, StrDict]]
OptFieldLike = Optional[FieldLike]

# Module specific constants
ROW_DELETED = 0b01

class DataRow:
    """Row Base Class."""

    id: int
    state: int

    def __post_init__(self, *args: Any, **kwds: Any) -> None:
        self.id = getattr(self, '_create_id', void)()
        self.state = 0

    def delete(self) -> None:
        if not self.state & ROW_DELETED:
            self.state |= ROW_DELETED
            getattr(self, '_remove_id', void)(self.id)

    def restore(self) -> None:
        if self.state & ROW_DELETED:
            self.state = self.state - ROW_DELETED
            getattr(self, '_append_id', void)(self.id)

class DataTable(DCMContainer):
    """Table Class."""

    _store: property = ContentAttr(list, default=[])
    _Row: property = TransientAttr(type)
    _index: property = TransientAttr(list, default=[])
    _iter_index: property = TransientAttr()

    fields: property = VirtualAttr(getter='_get_fields', readonly=True)
    colnames: property = VirtualAttr(getter='_get_colnames', readonly=True)

    def __init__(self, columns: OptFieldLike = None) -> None:
        """ """
        super().__init__()
        if columns:
            self._create_row_class(columns)

    def __iter__(self) -> Iterator:
        self._iter_index = iter(self._index)
        return self

    def __next__(self) -> DataRow:
        return self._store[next(self._iter_index)]

    def __len__(self) -> int:
        return len(self._index)

    def append(self, *args: Any, **kwds: Any) -> None:
        row = self._create_row(*args, **kwds)
        self._store.append(row)
        self._append_id(row.id)

    def delete(self, rowid: int) -> None:
        self.get_row(rowid).delete()

    def _append_id(self, rowid: int) -> None:
        self._index.append(rowid)

    def _remove_id(self, rowid: int) -> None:
        self._index.remove(rowid)

    def _create_id(self) -> int:
        return len(self._store)

    def _create_row(self, *args: Any, **kwds: Any) -> DataRow:
        return self._Row(*args, **kwds)

    def _create_row_class(self, columns: FieldLike) -> None:
        # Check types of fieldlike column descriptors and convert them to field
        # descriptors, that are accepted by dataclasses.make_dataclass()
        fields: list = []
        for each in columns:
            if isinstance(each, str):
                fields.append(each)
                continue
            check.has_type(f"field {each}", each, tuple)
            check.has_size(f"field {each}", each, min_size=2, max_size=3)
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

        # Create Row dataclass
        self._Row = dataclasses.make_dataclass('Row', fields, bases=(DataRow, ))

        # Create slots
        self._Row.__slots__ = ['id', 'state'] + [
            field.name for field in dataclasses.fields(self._Row)]

        # Bind Row methods to table methods
        setattr(self._Row, '_remove_id', self._remove_id)
        setattr(self._Row, '_append_id', self._append_id)
        setattr(self._Row, '_create_id', self._create_id)

        # Reset store
        self._store = []

    def get_row(self, rowid: int) -> DataRow:
        return self._store[rowid]

    def _get_fields(self) -> FieldTuple:
        return dataclasses.fields(self._Row)

    def _get_colnames(self) -> StrTuple:
        return tuple(field.name for field in self.fields)

    def select(self, columns: StrTuple) -> list:
        cols = lambda row: tuple(getattr(row, col) for col in columns)
        return list(map(cols, [self._store[rowid] for rowid in self._index]))

    # def as_tuples(self):
    #     """ """
    #     return [dataclasses.astuple(rec) for rec in self._store]
    #
    # def as_dicts(self):
    #     """ """
    #     return [dataclasses.asdict(rec) for rec in self._store]
    #
    # def as_array(self):
    #     """ """
    #     return np.array(self.as_tuples())

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
