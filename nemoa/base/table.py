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
from abc import ABC, abstractmethod

# try:
#     import numpy as np
# except ImportError as err:
#     raise ImportError(
#         "requires package numpy: "
#         "https://pypi.org/project/numpy/") from err

from numpy.lib import recfunctions as nprf
from nemoa.base import check
from nemoa.base.container import Container, DataAttr, MetaAttr
from nemoa.base.container import TempAttr, VirtAttr
from nemoa.errors import NemoaError
from nemoa.types import NpFields, NpRecArray, Tuple, Iterable
from nemoa.types import Union, Optional, StrDict, StrTuple, Iterator, Any
from nemoa.types import OptIntList, OptCallable, CallableClasses, Callable
from nemoa.types import OptStrTuple, OptInt, ClassVar, List, OptStr

#
# Module Types
#

Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
Fields = Iterable[Union[str, Tuple[str, type], Tuple[str, type, Field]]]
FieldLike = Union[Fields, Tuple[str, type, StrDict]]
OptFieldLike = Optional[FieldLike]

#
# Module Constants
#

ROW_STATE_CREATE = 0b001
ROW_STATE_UPDATE = 0b010
ROW_STATE_DELETE = 0b100
CURSOR_MODE_DYNAMIC = 0
CURSOR_MODE_FIXED = 1
CURSOR_MODE_STATIC = 2

#
# Module Exceptions
#

class TableError(NemoaError):
    """Default Table Error."""

class RowLookupError(TableError, LookupError):
    """Row Lookup Error."""

    def __init__(self, rowid: int) -> None:
        super().__init__(f"row index {rowid} is not valid")

class ColumnLookupError(TableError, LookupError):
    """Column Lookup Error."""

    def __init__(self, colname: int) -> None:
        super().__init__(f"column name '{colname}' is not valid")

class CursorModeError(TableError, LookupError):
    """Raise when a procedure is not supported by a cursor."""

    def __init__(self, mode: int, proc: OptStr = None) -> None:
        if not proc:
            msg = f"unknown cursor mode {mode}"
        else:
            msg = f"{proc} is not supported in cursor mode {mode}"
        super().__init__(msg)

#
# Record Class
#

class Record(ABC):
    """Record Base Class."""

    #
    # Public Instance Variables
    #

    id: int
    state: int

    #
    # Events
    #

    def __post_init__(self, *args: Any, **kwds: Any) -> None:
        self.id = self._create_row_id()
        self.state = ROW_STATE_CREATE

    #
    # Public Methods
    #

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

    #
    # Protected Methods
    #

    @abstractmethod
    def _create_row_id(self) -> int:
        pass

    @abstractmethod
    def _delete_hook(self, rowid: int) -> None:
        pass

    @abstractmethod
    def _restore_hook(self, rowid: int) -> None:
        pass

    @abstractmethod
    def _update_hook(self, rowid: int, **kwds: Any) -> None:
        pass

    @abstractmethod
    def _revoke_hook(self, rowid: int) -> None:
        pass

#
# Record Types
#

OptRec = Optional[Record]
RecList = List[Record]
RecLike = Union[Record, tuple, dict]
RecLikeList = List[RecLike]

#
# Cursor Class
#

class Cursor(Container):
    """Cursor Class.

    Args:
        index: List of row IDs, that are traversed by the cursor. By default the
            attribute '_index' of the parent object is used.
        mode:
            0: Dynamic Cursor:
                Dynamic cursors are built on-the-fly and therefore comprise any
                changes made to the rows in the result set during it's
                traversal, including new appended rows and the order of it's
                traversal. This behaviour is regardless of whether the changes
                occur from inside the cursor or by other users from outside the
                cursor. Dynamic cursors are threadsafe but do not support
                counting filtered rows or sorting rows.
            1: Fixed Cursor:
                Fixed cursors are built on-the-fly with respect to an initial
                copy of the table index and therefore comprise changes made to
                the rows in the result set during it's traversal, but not new
                appended rows or the order of it's traversal. Dynamic cursors
                are threadsafe but do not support counting filtered rows or
                sorting rows.
            2: Static Cursor:
                Static cursors are buffered and built during it's creation time
                and therfore always display the result set as it was when the
                cursor was first opened. Static cursors are not threadsafe but
                support counting the rows with respect to a given filter and
                sorting the rows.

    """

    #
    # Protected Class Variables
    #

    _default_mode: ClassVar[int] = CURSOR_MODE_FIXED
    _default_batchsize: ClassVar[int] = 1

    #
    # Public Attributes
    #

    mode: property = VirtAttr(getter='_get_mode', readonly=True)
    rowcount: property = VirtAttr(getter='_get_rowcount', readonly=True)
    batchsize: property = MetaAttr(classinfo=int, default=_default_batchsize)

    #
    # Protected Attributes
    #

    _mode: property = MetaAttr(classinfo=int, default=_default_mode)
    _index: property = MetaAttr(classinfo=list, inherit=True)
    _getter: property = TempAttr(classinfo=CallableClasses)
    _filter: property = TempAttr(classinfo=CallableClasses)
    _mapper: property = TempAttr(classinfo=CallableClasses)
    _buffer: property = TempAttr(classinfo=list, default=[])

    #
    # Events
    #

    def __init__(
            self, index: OptIntList = None, getter: OptCallable = None,
            predicate: OptCallable = None, mapper: OptCallable = None,
            parent: Optional[Container] = None, mode: OptInt = None,
            batchsize: OptInt = None) -> None:
        """Initialize Cursor."""
        super().__init__(parent=parent) # Parent is set by container
        if index is not None:
            self._index = index
        self._getter = getter
        self._filter = predicate
        self._mapper = mapper
        if mode is not None:
            self._mode = mode
        if batchsize:
            self.batchsize = batchsize
        if self.mode == CURSOR_MODE_FIXED:
            self._create_index()
        if self.mode == CURSOR_MODE_STATIC:
            self._create_buffer()
        self.reset() # Initialize iterator

    def __iter__(self) -> Iterator:
        self.reset()
        return self

    def __next__(self) -> RecLike:
        return self.next()

    def __len__(self) -> int:
        return self.rowcount

    #
    # Public Methods
    #

    def reset(self) -> None:
        """Reset cursor position before the first record."""
        mode = self._mode
        if mode in [CURSOR_MODE_DYNAMIC, CURSOR_MODE_FIXED]:
            self._iter_index = iter(self._index)
        elif mode == CURSOR_MODE_STATIC:
            self._iter_buffer = iter(self._buffer)
        else:
            raise CursorModeError(mode)

    def next(self) -> RecLike:
        """Return next row that matches the given filter."""
        mode = self._mode
        if mode in [CURSOR_MODE_DYNAMIC, CURSOR_MODE_FIXED]:
            if not self._filter:
                row = self._getter(next(self._iter_index))
                if self._mapper:
                    return self._mapper(row)
                return row
            matches = False
            while not matches:
                row = self._getter(next(self._iter_index))
                matches = self._filter(row)
            if self._mapper:
                return self._mapper(row)
            return row
        if mode == CURSOR_MODE_STATIC:
            return next(self._iter_buffer)
        raise CursorModeError(mode)

    def fetch(self, size: OptInt = None) -> RecLikeList:
        """Fetch rows from the result set.

        Args:
            size: Integer value which represents the number of rows, which are
                to be fetched. For zero or negative values all remaining rows
                are fetched. The default size is given by the cursor's
                *batchsize*.

        """
        if size is None:
            size = self.batchsize
        finished = False
        results: RecLikeList = []
        while not finished:
            try:
                results.append(self.next())
            except StopIteration:
                finished = True
            else:
                finished = 0 < size <= len(results)
        return results

    #
    # Protected Methods
    #

    def _get_mode(self) -> int:
        return self._mode

    def _get_rowcount(self) -> int:
        mode = self._mode
        if mode in [CURSOR_MODE_DYNAMIC, CURSOR_MODE_FIXED]:
            if not self._filter:
                return len(self._index)
            raise CursorModeError(mode, "counting filtered rows")
        if mode == CURSOR_MODE_STATIC:
            return len(self._buffer)
        raise CursorModeError(mode)

    def _create_index(self) -> None:
        self._index = list(self._index)

    def _create_buffer(self) -> None:
        dyn_cur = self.__class__(
            index=self._index, getter=self._getter, predicate=self._filter,
            mapper=self._mapper, mode=CURSOR_MODE_DYNAMIC)
        self._buffer = list(dyn_cur)

class Table(Container):
    """Table Class."""

    #
    # Public Attributes
    #

    fields: property = VirtAttr(getter='_get_fields', readonly=True)
    colnames: property = VirtAttr(getter='_get_colnames', readonly=True)

    #
    # Protected Attributes
    #

    _store: property = DataAttr(classinfo=list, default=[])
    _diff: property = TempAttr(classinfo=list, default=[])
    _index: property = TempAttr(classinfo=list, default=[])
    _iter_index: property = TempAttr()
    _Record: property = TempAttr(classinfo=type)

    def __init__(self, columns: OptFieldLike = None) -> None:
        """ """
        super().__init__()
        if columns:
            self._create_header(columns)

    def __iter__(self) -> Iterator:
        self._iter_index = iter(self._index)
        return self

    def __next__(self) -> Record:
        row = self.get_row(next(self._iter_index))
        while not row:
            row = self.get_row(next(self._iter_index))
        return row

    def __len__(self) -> int:
        return len(self._index)

    def commit(self) -> None:
        """Apply changes to table."""
        # Delete / Update rows in storage table
        for rowid in list(range(len(self._store))):
            row = self.get_row(rowid)
            if not row:
                continue
            state = row.state
            if state & ROW_STATE_DELETE:
                self._store[rowid] = None
                try:
                    self._index.remove(rowid)
                except ValueError:
                    pass
            elif state & (ROW_STATE_CREATE | ROW_STATE_UPDATE):
                self._store[rowid] = self._diff[rowid]
                self._store[rowid].state = 0

        # Flush diff table
        self._diff = [None] * len(self._store)

    def rollback(self) -> None:
        """Revoke changes from table."""
        # Remove newly created rows from index and reset states of already
        # existing rows
        for rowid in list(range(len(self._store))):
            row = self.get_row(rowid)
            if not row:
                continue
            state = row.state
            if state & ROW_STATE_CREATE:
                try:
                    self._index.remove(rowid)
                except ValueError:
                    pass
            else:
                self._store[rowid].state = 0

        # Flush diff table
        self._diff = [None] * len(self._store)

    def get_cursor(
            self, predicate: OptCallable = None, mapper: OptCallable = None,
            mode: OptInt = None) -> Cursor:
        """ """
        return Cursor(
            getter=self.get_row, predicate=predicate, mapper=mapper, mode=mode,
            parent=self)

    def get_row(self, rowid: int) -> OptRec:
        """ """
        return self._diff[rowid] or self._store[rowid]

    def get_rows(
            self, predicate: OptCallable = None, mode: OptInt = None) -> Cursor:
        """ """
        return self.get_cursor(predicate=predicate, mode=mode)

    def append_row(self, *args: Any, **kwds: Any) -> None:
        """ """
        row = self._create_row(*args, **kwds)
        self._store.append(None)
        self._diff.append(row)
        self._append_row_id(row.id)

    def delete_row(self, rowid: int) -> None:
        """ """
        row = self.get_row(rowid)
        if not row:
            raise RowLookupError(rowid)
        row.delete()

    def delete_rows(self, predicate: OptCallable = None) -> None:
        """ """
        for row in self.get_rows(predicate):
            row.delete()

    def update_row(self, rowid: int, **kwds: Any) -> None:
        """ """
        row = self.get_row(rowid)
        if not row:
            raise RowLookupError(rowid)
        row.update(**kwds)

    def update_rows(self, predicate: OptCallable = None, **kwds: Any) -> None:
        """ """
        for row in self.get_rows(predicate):
            row.update(**kwds)

    def select(
            self, columns: OptStrTuple = None, predicate: OptCallable = None,
            fmt: type = tuple, mode: OptInt = None) -> RecLikeList:
        """ """
        if not columns:
            mapper = self._get_mapper(self.colnames, fmt=fmt)
        else:
            check.is_subset(
                "argument 'columns'", set(columns),
                "table column names", set(self.colnames))
            mapper = self._get_mapper(columns, fmt=fmt)
        return self.get_cursor( # type: ignore
            predicate=predicate, mapper=mapper, mode=mode)

    def pack(self) -> None:
        """Remove empty records from storage table and rebuild table index."""
        # Commit pending changes
        self.commit()

        # Remove empty records
        self._store = list(filter(None.__ne__, self._store))

        # Rebuild table index
        self._index = list(range(len(self._store)))
        for rowid in self._index:
            self._store[rowid].id = rowid

        # Rebuild diff table
        self._diff = [None] * len(self._store)

    def _get_mapper(self, columns: StrTuple, fmt: type = tuple) -> Callable:
        def mapper_tuple(row: Record) -> tuple:
            return tuple(getattr(row, col) for col in columns)
        def mapper_dict(row: Record) -> dict:
            return {col: getattr(row, col) for col in columns}
        if fmt == tuple:
            return mapper_tuple
        if fmt == dict:
            return mapper_dict
        raise TableError(f"argument 'fmt' requires to be tuple or dict")

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
        row = self.get_row(rowid)
        if not row:
            raise RowLookupError(rowid)
        upd = dataclasses.replace(row, **kwds)
        upd.id = rowid
        upd.state = row.state
        self._diff[rowid] = upd

    def _remove_row_diff(self, rowid: int) -> None:
        self._diff[rowid] = None

    def _create_row(self, *args: Any, **kwds: Any) -> Record:
        return self._Record(*args, **kwds) # pylint: disable=E0110

    def _create_header(self, columns: FieldLike) -> None:
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

        # Reset store, diff and index
        self._store = []
        self._diff = []
        self._index = []

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
