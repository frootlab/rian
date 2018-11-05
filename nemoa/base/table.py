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

import abc
import dataclasses

# try:
#     import numpy as np
# except ImportError as err:
#     raise ImportError(
#         "requires package numpy: "
#         "https://pypi.org/project/numpy/") from err

from numpy.lib import recfunctions as nprf
from nemoa.base import check
from nemoa.base.container import DCMContainer, ContentAttr, BaseContainer
from nemoa.base.container import VirtualAttr, TransientAttr, InheritedAttr
from nemoa.types import NpFields, NpRecArray, Tuple, Iterable
from nemoa.types import Union, Optional, StrDict, StrTuple, Iterator, Any
from nemoa.types import OptIntList, OptCallable

# Module specific types
Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
Fields = Iterable[Union[str, Tuple[str, type], Tuple[str, type, Field]]]
FieldLike = Union[Fields, Tuple[str, type, StrDict]]
OptFieldLike = Optional[FieldLike]

# Module specific constants
ROW_STATE_CREATE = 0b001
ROW_STATE_UPDATE = 0b010
ROW_STATE_DELETE = 0b100

class Record(abc.ABC):
    """Record Base Class."""

    id: int
    state: int

    def __post_init__(self, *args: Any, **kwds: Any) -> None:
        self.id = self._create_row_id()
        self.state = ROW_STATE_CREATE

    def delete(self) -> None:
        """Mark record as deleted and remove it's ID from index."""
        if not self.state & ROW_STATE_DELETE:
            self.state |= ROW_STATE_DELETE
            self._delete_hook(self.id)

    def restore(self) -> None:
        """Mark record as not deleted and append it's ID to index."""
        if self.state & ROW_STATE_DELETE:
            self.state &= ~ROW_STATE_DELETE
            self._restore_hook(self.id)

    def update(self, **kwds: Any) -> None:
        """Mark record as updated and write the update to diff table."""
        if not self.state & ROW_STATE_UPDATE:
            self.state |= ROW_STATE_UPDATE
            self._update_hook(self.id, **kwds)

    def revoke(self) -> None:
        """Mark record as not updated and remove the update from diff table."""
        if self.state & ROW_STATE_UPDATE:
            self.state &= ~ROW_STATE_UPDATE
            self._revoke_hook(self.id)

    @abc.abstractmethod
    def _create_row_id(self) -> int:
        pass

    @abc.abstractmethod
    def _delete_hook(self, rowid: int) -> None:
        pass

    @abc.abstractmethod
    def _restore_hook(self, rowid: int) -> None:
        pass

    @abc.abstractmethod
    def _update_hook(self, rowid: int, **kwds: Any) -> None:
        pass

    @abc.abstractmethod
    def _revoke_hook(self, rowid: int) -> None:
        pass

class Cursor(BaseContainer):
    """Cursor Class."""

    _index: property = InheritedAttr(list, default=[])
    func: property = TransientAttr()
    _iter: property = TransientAttr()

    def __init__(
            self, index: OptIntList = None, func: OptCallable = None) -> None:
        super().__init__()
        if index:
            self._index = index
        if func and callable(func):
            self.func = func

    def __iter__(self) -> Iterator:
        self._iter = iter(self._index)
        return self

    def __next__(self) -> Record:
        return self.func[next(self._iter)]

class Table(DCMContainer):
    """Table Class."""

    _store: property = ContentAttr(list, default=[])

    _diff: property = TransientAttr(list, default=[])
    _index: property = TransientAttr(list, default=[])
    _iter_index: property = TransientAttr()
    _Record: property = TransientAttr(type)

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

    def __next__(self) -> Record:
        return self.row(next(self._iter_index))

    def __len__(self) -> int:
        return len(self._index)

    def append(self, *args: Any, **kwds: Any) -> None:
        row = self._create_row(*args, **kwds)
        self._store.append(None)
        self._diff.append(row)
        self._append_row_id(row.id)

    def commit(self) -> None:
        """Apply changes to table."""
        # Delete and update rows in table store. The reversed order is required
        # to keep the position of the list index, when deleting rows
        for rowid in reversed(range(len(self._store))):
            state = self.row(rowid).state
            if state & ROW_STATE_DELETE:
                del self._store[rowid]
            elif state & (ROW_STATE_CREATE | ROW_STATE_UPDATE):
                self._store[rowid] = self._diff[rowid]
                self._store[rowid].state = 0

        # Reassign row IDs and recreate diff table and index
        self._create_index()

    def rollback(self) -> None:
        """Revoke changes in table."""
        # Delete new rows, that have not been commited. The reversed order is
        # required to keep the position of the list index, when deleting rows
        for rowid in reversed(range(len(self._store))):
            state = self.row(rowid).state
            if state & ROW_STATE_CREATE:
                del self._store[rowid]
            else:
                self._store[rowid].state = 0

        # Reassign row IDs and recreate diff table and index
        self._create_index()

    def _create_index(self) -> None:
        self._index = []
        self._diff = []
        for rowid in range(len(self._store)):
            self._store[rowid].id = rowid
            self._diff.append(None)
            self._index.append(rowid)

    def delete(self, rowid: int) -> None:
        self.row(rowid).delete()

    def select(self, columns: StrTuple) -> list:
        cols = lambda row: tuple(getattr(row, col) for col in columns)
        return list(map(cols, [self.row(rowid) for rowid in self._index]))

    def row(self, rowid: int) -> Record:
        return self._diff[rowid] or self._store[rowid]

    # def get_cursor(
    #         self, index: OptIntList = None, func: OptCallable = None) -> Cursor:
    #     return Cursor(index, func)

    def _get_fields(self) -> FieldTuple:
        return dataclasses.fields(self._Record)

    def _get_colnames(self) -> StrTuple:
        return tuple(field.name for field in self.fields)

    def _create_row_id(self) -> int:
        return len(self._store)

    def _append_row_id(self, rowid: int) -> None:
        self._index.append(rowid)

    def _remove_row_id(self, rowid: int) -> None:
        self._index.remove(rowid)

    def _update_row_diff(self, rowid: int, **kwds: Any) -> None:
        row = self.row(rowid)
        new = dataclasses.replace(row, **kwds)
        new.id = rowid
        new.state = row.state
        self._diff[rowid] = new

    def _remove_row_diff(self, rowid: int) -> None:
        self._diff[rowid] = None

    def _create_row(self, *args: Any, **kwds: Any) -> Record:
        return self._Record(*args, **kwds) # pylint: disable=E0110

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

        # Create record namespace with table hooks
        namespace = {
            '_create_row_id': self._create_row_id,
            '_delete_hook': self._remove_row_id,
            '_restore_hook': self._append_row_id,
            '_update_hook': self._update_row_diff,
            '_revoke_hook': self._remove_row_diff}

        # Create Record dataclass and constructor
        self._Record = dataclasses.make_dataclass(
            'Row', fields, bases=(Record, ), namespace=namespace)

        # Create slots
        self._Record.__slots__ = ['id', 'state'] + [
            field.name for field in dataclasses.fields(self._Record)]

        # Bind Record hooks to table methods
        #setattr(self._Record, '_create_row_id', self._create_row_id)
        # setattr(self._Record, '_delete_hook', self._remove_row_id)
        # setattr(self._Record, '_restore_hook', self._append_row_id)
        # setattr(self._Record, '_update_hook', self._update_row_diff)
        # setattr(self._Record, '_revoke_hook', self._remove_row_diff)

        # Reset store, diff and index
        self._store = []
        self._diff = []
        self._index = []

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
