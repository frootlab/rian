# -*- coding: utf-8 -*-
"""Table and Table Proxy Class for Data Integration."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import abc
import random
import dataclasses
from nemoa.base import attrib, check, pattern
from nemoa.errors import TableError, RowLookupError
from nemoa.errors import CursorModeError, ProxyError
from nemoa.types import Tuple, Iterable, Union, Optional, StrDict, StrTuple
from nemoa.types import OptIntList, OptCallable, CallableClasses, Callable
from nemoa.types import OptStrTuple, OptInt, ClassVar, List, OptStr
from nemoa.types import Iterator, Any, OptDict, Mapping, MappingProxy

#
# Structural Types
#

Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
Fields = Iterable[Union[str, Tuple[str, type], Tuple[str, type, Field]]]
FieldLike = Union[Fields, Tuple[str, type, StrDict]]
OptFieldLike = Optional[FieldLike]
OptRow = Optional['Record']
RowList = List[tuple]
RowLike = Union['Record', tuple, dict]
RowLikeList = List[RowLike]

#
# Constants
#

RECORD_STATE_FLAG_CREATE = 0b0001
RECORD_STATE_FLAG_UPDATE = 0b0010
RECORD_STATE_FLAG_DELETE = 0b0100

CURSOR_MODE_FLAG_BUFFERED = 0b0001
CURSOR_MODE_FLAG_INDEXED = 0b0010
CURSOR_MODE_FLAG_SCROLLABLE = 0b0100
CURSOR_MODE_FLAG_RANDOM = 0b1000

PROXY_MODE_FLAG_CACHE = 0b0001
PROXY_MODE_FLAG_INCREMENTAL = 0b0010
PROXY_MODE_FLAG_READONLY = 0b0100

#
# Record Base Class
#

class Record(abc.ABC):
    """Abstract Base Class for Records."""

    _id: int
    state: int

    def __post_init__(self, *args: Any, **kwds: Any) -> None:
        self.validate()
        self._id = self._create_row_id()
        self.state = RECORD_STATE_FLAG_CREATE

    def validate(self) -> None:
        """Check types of fields."""
        fields = getattr(self, '__dataclass_fields__', {})
        for name, field in fields.items():
            value = getattr(self, name)
            check.has_type(f"field '{name}'", value, field.type)

    def delete(self) -> None:
        """Mark record as deleted and remove it's ID from index."""
        if not self.state & RECORD_STATE_FLAG_DELETE:
            self.state |= RECORD_STATE_FLAG_DELETE
            self._delete_hook(self._id)

    def restore(self) -> None:
        """Mark record as not deleted and append it's ID to index."""
        if self.state & RECORD_STATE_FLAG_DELETE:
            self.state &= ~RECORD_STATE_FLAG_DELETE
            self._restore_hook(self._id)

    def update(self, **kwds: Any) -> None:
        """Mark record as updated and write the update to diff table."""
        if not self.state & RECORD_STATE_FLAG_UPDATE:
            self.state |= RECORD_STATE_FLAG_UPDATE
            self._update_hook(self._id, **kwds)

    def revoke(self) -> None:
        """Mark record as not updated and remove the update from diff table."""
        if self.state & RECORD_STATE_FLAG_UPDATE:
            self.state &= ~RECORD_STATE_FLAG_UPDATE
            self._revoke_hook(self._id)

    @abc.abstractmethod
    def _create_row_id(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def _delete_hook(self, rowid: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _restore_hook(self, rowid: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _update_hook(self, rowid: int, **kwds: Any) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _revoke_hook(self, rowid: int) -> None:
        raise NotImplementedError()

#
# Cursor Class
#

class Cursor(attrib.Container):
    """Cursor Class.

    Args:
        index: List of row IDs, that are traversed by the cursor. By default the
            attribute '_index' of the parent object is used.
        mode: Named string identifier for the cursor :py:attr:`.mode`. The
            default cursor mode is 'forward-only indexed'. Note: After
            initializing the curser, it's mode can not be changed anymore.

    """

    #
    # Protected Class Variables
    #

    _default_mode: ClassVar[int] = CURSOR_MODE_FLAG_INDEXED

    #
    # Public Attributes
    #

    mode: property = attrib.Virtual(fget='_get_mode')
    mode.__doc__ = """
    The read-only string attribute *cursor mode* specifies the space separated
    *scrolling type* and the *operation mode* of the cursor. Supported scrolling
    types are:

    :forward-only: The default scrolling type of cursors is called a
        forward-only cursor and can move only forward through the result set. A
        forward-only cursor does not support scrolling but only fetching rows
        from the start to the end of the result set.
    :scrollable: A scrollable cursor is commonly used in screen-based
        interactive applications, like spreadsheets, in which users are allowed
        to scroll back and forth through the result set. However, applications
        should use scrollable cursors only when forward-only cursors will not do
        the job, as scrollable cursors are generally more expensive, than
        forward-only cursors.
    :random: Random cursors move randomly through the result set. In difference
        to a randomly sorted cursor, the rows are not unique and the number of
        fetched rows is not limited to the size of the result set. If the method
        :meth:`.fetch` is called with a zero value for size, a
        CursorModeError is raised.

    Supported operation modes are:

    :dynamic: A **dynamic cursor** is built on-the-fly and therefore comprises
        any changes made to the rows in the result set during it's traversal,
        including new appended rows and the order of it's traversal. This
        behaviour is regardless of whether the changes occur from inside the
        cursor or by other users from outside the cursor. Dynamic cursors are
        threadsafe but do not support counting filtered rows or sorting rows.
    :indexed: Indexed cursors (aka Keyset-driven cursors) are built on-the-fly
        with respect to an initial copy of the table index and therefore
        comprise changes made to the rows in the result set during it's
        traversal, but not new appended rows nor changes within their order.
        Keyset driven cursors are threadsafe but do not support sorting rows or
        counting filtered rows.
    :static: Static cursors are buffered and built during it's creation time and
        therfore always display the result set as it was when the cursor was
        first opened. Static cursors are not threadsafe but support counting the
        rows with respect to a given filter and sorting the rows.

    """

    batchsize: property = attrib.MetaData(classinfo=int, default=1)
    """
    The read-writable integer attribute *batchsize* specifies the default number
    of rows which is to be fetched by the method :meth:`.fetch`. It defaults
    to 1, meaning to fetch a single row at a time. Whether and which batchsize
    to use depends on the application and should be considered with care. The
    batchsize can also be adapted during the lifetime of the cursor, which
    allows dynamic performance optimization.
    """

    rowcount: property = attrib.Virtual(fget='_get_rowcount')
    """
    The read-only integer attribute *rowcount* specifies the current number of
    rows within the cursor.
    """

    #
    # Protected Attributes
    #

    _mode: property = attrib.MetaData(classinfo=int, default=_default_mode)
    _index: property = attrib.MetaData(classinfo=list, inherit=True)
    _getter: property = attrib.Temporary(classinfo=CallableClasses)
    _filter: property = attrib.Temporary(classinfo=CallableClasses)
    _mapper: property = attrib.Temporary(classinfo=CallableClasses)
    _buffer: property = attrib.Temporary(classinfo=list, default=[])

    #
    # Events
    #

    def __init__(
            self, index: OptIntList = None, getter: OptCallable = None,
            predicate: OptCallable = None, mapper: OptCallable = None,
            batchsize: OptInt = None, mode: OptStr = None,
            parent: Optional[attrib.Container] = None) -> None:
        """Initialize Cursor."""
        super().__init__(parent=parent) # Parent is set by container
        if index is not None:
            self._index = index
        self._getter = getter
        self._filter = predicate
        self._mapper = mapper
        if mode:
            self._set_mode(mode)
        if batchsize:
            self.batchsize = batchsize
        if self._mode & CURSOR_MODE_FLAG_INDEXED:
            self._create_index()
        if self._mode & CURSOR_MODE_FLAG_BUFFERED:
            self._create_buffer()
        self.reset() # Initialize iterator

    def __iter__(self) -> Iterator:
        self.reset()
        return self

    def __next__(self) -> RowLike:
        return self.next()

    def __len__(self) -> int:
        return self.rowcount

    #
    # Public Methods
    #

    def reset(self) -> None:
        """Reset cursor position before the first record."""
        mode = self._mode
        if mode & CURSOR_MODE_FLAG_BUFFERED: # Iterate over fixed result set
            self._iter_buffer = iter(self._buffer)
        elif mode & CURSOR_MODE_FLAG_INDEXED: # Iterate over fixed index
            self._iter_index = iter(self._index)
        else: # TODO: handle case for dynamic cursors by self._iter_table
            self._iter_index = iter(self._index)

    def next(self) -> RowLike:
        """Return next row that matches the given filter."""
        mode = self._mode
        if mode & CURSOR_MODE_FLAG_BUFFERED:
            return self._get_next_from_buffer()
        if mode & CURSOR_MODE_FLAG_INDEXED:
            return self._get_next_from_fixed_index()
        # TODO: For dynamic cursors implement _get_next_from_dynamic_index()
        return self._get_next_from_fixed_index()

    def fetch(self, size: OptInt = None) -> RowLikeList:
        """Fetch rows from the result set.

        Args:
            size: Integer value, which represents the number of rows, which is
                fetched from the result set. For the given size 0 all remaining
                rows from the result set are fetched. By default the number of
                rows is given by the cursors batchsize.

        """
        if size is None:
            size = self.batchsize
        if self._mode & CURSOR_MODE_FLAG_RANDOM and size <= 0:
            raise CursorModeError(self.mode, 'fetching all rows')
        finished = False
        results: RowLikeList = []
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

    def _get_next_from_fixed_index(self) -> RowLike:
        is_random = self._mode & CURSOR_MODE_FLAG_RANDOM
        matches = False
        while not matches:
            if is_random:
                row_id = random.randrange(len(self._index))
            else:
                row_id = next(self._iter_index)
            row = self._getter(row_id)
            if self._filter:
                matches = self._filter(row)
            else:
                matches = True
        if self._mapper:
            return self._mapper(row)
        return row

    def _get_next_from_buffer(self) -> RowLike:
        if self._mode & CURSOR_MODE_FLAG_RANDOM:
            row_id = random.randrange(len(self._buffer))
            return self._buffer[row_id]
        return next(self._iter_buffer)

    def _get_mode(self) -> str:
        mode = self._mode
        tokens = []
        # Add name of traversal mode
        if mode & CURSOR_MODE_FLAG_RANDOM:
            tokens.append('random')
        elif mode & CURSOR_MODE_FLAG_SCROLLABLE:
            tokens.append('scrollable')
        # Add name of operation mode
        if mode & CURSOR_MODE_FLAG_BUFFERED:
            tokens.append('static')
        elif mode & CURSOR_MODE_FLAG_INDEXED:
            tokens.append('indexed')
        else:
            tokens.append('dynamic')
        return ' '.join(tokens)

    def _set_mode(self, name: str) -> None:
        mode = 0
        name = name.strip(' ').lower()

        # Set traversal mode flags
        if 'random' in name:
            mode |= CURSOR_MODE_FLAG_RANDOM
        elif 'scrollable' in name:
            mode |= CURSOR_MODE_FLAG_SCROLLABLE

        # Set operation mode flags
        if 'static' in name:
            mode |= CURSOR_MODE_FLAG_BUFFERED | CURSOR_MODE_FLAG_INDEXED
        elif 'indexed' in name:
            mode |= CURSOR_MODE_FLAG_INDEXED
        self._mode = mode

    def _get_rowcount(self) -> int:
        mode = self._mode
        if mode & CURSOR_MODE_FLAG_RANDOM:
            raise CursorModeError(self.mode, 'counting rows')
        if mode & CURSOR_MODE_FLAG_BUFFERED:
            return len(self._buffer)
        if self._filter:
            raise CursorModeError(self.mode, 'counting filtered rows')
        return len(self._index)

    def _create_index(self) -> None:
        if isinstance(self._index, list):
            self._index = self._index.copy()
        else:
            self._index = []

    def _create_buffer(self) -> None:
        cur = self.__class__( # Create new dynamic cursor
            index=self._index, getter=self._getter, predicate=self._filter,
            mapper=self._mapper)
        self._buffer = cur.fetch(0) # Fetch all from result set

#
# Table Class
#

class Table(attrib.Container):
    """Table Class."""

    #
    # Public Attributes
    #

    name: property = attrib.Virtual(fget='_get_name', fset='_set_name')
    metadata: property = attrib.Virtual(fget='_get_metadata')
    fields: property = attrib.Virtual(fget='_get_fields')
    colnames: property = attrib.Virtual(fget='_get_colnames')

    #
    # Protected Attributes
    #

    _store: property = attrib.Content(classinfo=list, default=[])
    _name: property = attrib.MetaData(classinfo=str)
    _metadata: property = attrib.MetaData(classinfo=Mapping)
    _metadata_proxy: property = attrib.Temporary(classinfo=MappingProxy)
    _diff: property = attrib.Temporary(classinfo=list, default=[])
    _index: property = attrib.Temporary(classinfo=list, default=[])
    _iter_index: property = attrib.Temporary()
    _Record: property = attrib.Temporary(classinfo=type)

    #
    # Events
    #

    def __init__(
            self, name: OptStr = None, metadata: OptDict = None,
            fields: OptFieldLike = None) -> None:
        """Initialize Table.

        Args:
            name: Table name, given as a valid identifier, defined in [UAX31]_.
            metadata: Optioanl dictinary with arbitrary metadata.
            fields:

        """
        super().__init__()
        if name:
            check.is_identifier(f"'name'", name)
            self._name = name
        if fields:
            self._create_header(fields)
        self._metadata = {}
        self._metadata_proxy = MappingProxy(self._metadata)
        if metadata:
            check.has_type("'metadata'", metadata, Mapping)
            self._metadata.update(metadata)

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

    #
    # Public Methods
    #

    def commit(self) -> None:
        """Apply changes to table."""
        # Delete / Update rows in storage table
        for rowid in list(range(len(self._store))):
            row = self.get_row(rowid)
            if not row:
                continue
            state = row.state
            if state & RECORD_STATE_FLAG_DELETE:
                self._store[rowid] = None
                try:
                    self._index.remove(rowid)
                except ValueError:
                    pass
            elif state & (RECORD_STATE_FLAG_CREATE | RECORD_STATE_FLAG_UPDATE):
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
            if state & RECORD_STATE_FLAG_CREATE:
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
            mode: OptStr = None) -> Cursor:
        """ """
        return Cursor(
            getter=self.get_row, predicate=predicate, mapper=mapper,
            mode=mode, parent=self)

    def get_row(self, rowid: int) -> OptRow:
        """ """
        return self._diff[rowid] or self._store[rowid]

    def get_rows(
            self, predicate: OptCallable = None,
            mode: OptStr = None) -> Cursor:
        """ """
        return self.get_cursor(predicate=predicate, mode=mode)

    def append_row(self, *args: Any, **kwds: Any) -> None:
        """ """
        row = self._create_row(*args, **kwds)
        self._store.append(None)
        self._diff.append(row)
        self._append_row_id(row._id) # pylint: disable=W0212

    def append_rows(self, rows: RowList) -> None:
        """Append multiple rows."""
        for row in rows:
            self.append_row(*row)

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
            fmt: type = tuple, mode: OptStr = None) -> RowLikeList:
        """ """
        if not columns:
            mapper = self._get_mapper(self.colnames, fmt=fmt)
        else:
            check.is_subset(
                "'columns'", set(columns),
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
            self._store[rowid]._id = rowid # pylint: disable=W0212

        # Rebuild diff table
        self._diff = [None] * len(self._store)

    #
    # Protected Methods
    #

    def _append_row_id(self, rowid: int) -> None:
        self._index.append(rowid)

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

    def _create_row(self, *args: Any, **kwds: Any) -> Record:
        return self._Record(*args, **kwds) # pylint: disable=E0110

    def _create_row_id(self) -> int:
        return len(self._store)

    def _get_colnames(self) -> StrTuple:
        return tuple(field.name for field in self.fields)

    def _get_fields(self) -> FieldTuple:
        return dataclasses.fields(self._Record)

    def _get_mapper(self, columns: StrTuple, fmt: type = tuple) -> Callable:
        def mapper_tuple(row: Record) -> tuple:
            return tuple(getattr(row, col) for col in columns)
        def mapper_dict(row: Record) -> dict:
            return {col: getattr(row, col) for col in columns}
        if fmt == tuple:
            return mapper_tuple
        if fmt == dict:
            return mapper_dict
        raise TableError(f"'fmt' requires to be tuple or dict")

    def _get_name(self) -> str:
        return self._name

    def _set_name(self, name: str) -> None:
        self._name = name

    def _get_metadata(self) -> MappingProxy:
        return self._metadata_proxy

    def _remove_row_diff(self, rowid: int) -> None:
        self._diff[rowid] = None

    def _remove_row_id(self, rowid: int) -> None:
        self._index.remove(rowid)

    def _update_row_diff(self, rowid: int, **kwds: Any) -> None:
        row = self.get_row(rowid)
        if not row:
            raise RowLookupError(rowid)
        new_row = dataclasses.replace(row, **kwds)
        new_row._id = rowid # pylint: disable=W0212
        new_row.state = row.state
        self._diff[rowid] = new_row

#
# Table Proxy Base Class
#

class ProxyBase(Table, pattern.Proxy):
    """Table Proxy Base Class."""

    _proxy_mode: property = attrib.MetaData(classinfo=int, default=1)

    def __init__(
            self, *args: Any, proxy_mode: OptInt = None, **kwds: Any) -> None:
        """Initialize Table Proxy.

        Args:
            proxy_mode:
            *args:
            **kwds:

        """
        pattern.Proxy.__init__(self) # Init Proxy
        Table.__init__(self, *args, **kwds) # Init Table

        # Set default proxy mode
        if proxy_mode is None:
            proxy_mode = PROXY_MODE_FLAG_CACHE
        self._proxy_mode = proxy_mode

    def _post_init(self) -> None:
        # Retrieve all rows from source if table is cached
        if self._proxy_mode & PROXY_MODE_FLAG_CACHE:
            self.pull()

    def commit(self) -> None:
        """Push changes to source table and apply changes to local table."""
        if self._proxy_mode & PROXY_MODE_FLAG_READONLY:
            raise ProxyError('changes can not be commited in readonly mode')

        # For incremental updates of the source, the push request requires, that
        # changes have not yet been applied to the local table
        if self._proxy_mode & PROXY_MODE_FLAG_INCREMENTAL:
            self.push()
            super().commit()
            return
        # For full updates of the source, the push request requires, that all
        # changes have been applied to the local table
        super().commit()
        self.push()
