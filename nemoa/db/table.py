# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Database Tables."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import types
from typing import Any, NewType, Tuple, List, Optional, Iterator, Union
from nemoa.base import attrib, check, abc
from nemoa.db import record, cursor
from nemoa.errors import RowLookupError, ProxyError, InvalidTypeError
from nemoa.math import stype
from nemoa.types import StrList, StrTuple, OptOp, SeqOp, OptType
from nemoa.types import OptStrTuple, OptInt, OptStr
from nemoa.types import Mapping, OptMapping

#
# Structural Types
#

# Various
OrderByType = Optional[Union[str, StrList, StrTuple, SeqOp]]

# MappingProxy
MappingProxy = types.MappingProxyType
OptMappingProxy = Optional[MappingProxy]

# Fields
OptFieldTuple = Optional[Tuple[record.Field, ...]]

# Colums
SelColA = str # Select Column: name
SelColB = Tuple[str, SeqOp] # Select Column: name, aggregator
SelCol = Union[SelColA, SelColB] # Select Column
ColsDef = Tuple[record.ColDef, ...]
OptColsDef = Optional[ColsDef]

# Rows
Row = NewType('Row', record.Record)
OptRow = Optional[Row]
RowList = List[Row]
RowLike = Union[tuple, Mapping, Row]
RowLikeClasses = (tuple, Mapping, record.Record)
RowLikeList = Union[RowList, List[tuple], List[Mapping]]
ValuesType = Optional[Union[RowLike, RowLikeList]]

#
# Constants
#

PROXY_MODE_FLAG_CACHE = 0b0001
PROXY_MODE_FLAG_INCREMENTAL = 0b0010
PROXY_MODE_FLAG_READONLY = 0b0100

#
# Table Class
#

class Table(attrib.Group):
    """Table Class.

    Args:
        name: Optional table name. If provided, the choice of the table name is
            restricted to valid identifiers, described by [UAX31]_.
        columns: Optionl tuple of *column definitions*. All column definitions
            independent from each other can be given in one of the following
            formats: (1) In order to only specify the name of the column,
            without further information, the colum definition has to be given as
            a string `<name>`. Thereby the choice of `<name>` is restricted to
            valid identifiers, described by [UAX31]_. (2) If, additionally to
            the name, also the data type of the column shall be specified, then
            the column definition has to be given as a tuple `(<name>, <type>)`.
            Thereby `<type>` is required to by a valid :class:`type`, like
            like :class:`str`, :class:`int`, :class:`float` or :class:`Date
            <datetime.datetime>`. (3) Finally the column definition may also
            contain supplementary constraints and metadata. In this case the
            definition has to be given as a tuple `(<name>, <type>, <dict>)`,
            where `<dict>` is dictionary which comprises any items, documented
            by the function :func:`dataclasses.fields`.
        metadata: Optional dictionary, with supplementary metadata of the table.
            This does not comprise metadata of the fields, which has to be
            included within the field declarations.
        parent: Reference to parent :class:`attribute group
            <nemoa.base.attrib.Group>`, which is used for inheritance and
            shared attributes. By default no parent is referenced.

    """

    #
    # Public Attributes
    #

    name: property = attrib.Virtual(fget='_get_name', fset='_set_name')
    name.__doc__ = "Name of the table."

    metadata: property = attrib.Virtual(fget='_get_metadata_proxy')
    metadata.__doc__ = """
    Read-only attribute, that provides an access to the tables metadata by a
    :class:`MappingProxy <types.MappingProxyType>`. Individual entries can be
    accessed and changed by the methods :meth:`.get_metadata` and
    :meth:`.set_metadata`. This attribute is not used by the :class:`Table class
    <nemoa.db.table.Table>` itself, but intended for data integration by
    third-party extensions.
    """

    fields: property = attrib.Virtual(fget='_get_fields')
    fields.__doc__ = """
    Read-only attribute, that provides information about the fields of the
    table, as returned by the function :func:`dataclasses.fields`.
    """

    columns: property = attrib.Virtual(fget='_get_columns')
    columns.__doc__ = """
    Read-only attribute containing a tuple with all column names of the table.
    The order of the column names reflects the order of the corresponding fields
    in the table.
    """

    #
    # Protected Attributes
    #

    _data: property = attrib.Content(dtype=list)
    _name: property = attrib.MetaData(dtype=str)
    _metadata: property = attrib.MetaData(dtype=Mapping)
    _metadata_proxy: property = attrib.Temporary(dtype=MappingProxy)
    _record: property = attrib.Temporary()
    _diff: property = attrib.Temporary(dtype=list, default=[])
    _index: property = attrib.Temporary(dtype=list, default=[])
    _iter_index: property = attrib.Temporary()

    #
    # Special Methods
    #

    def __init__(
            self, name: OptStr = None, columns: OptColsDef = None,
            metadata: OptMapping = None,
            parent: Optional[attrib.Group] = None) -> None:
        super().__init__(parent=parent) # Initialize Attribute Group

        # Initialize Table Structure
        if columns:
            self.create(name, columns, metadata=metadata)

    def __iter__(self) -> Iterator:
        self._iter_index = iter(self._index)
        return self

    def __next__(self) -> Row:
        row = self.row(next(self._iter_index))
        while not row:
            row = self.row(next(self._iter_index))
        return row

    def __len__(self) -> int:
        return len(self._index)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name='{self.name}')"

    #
    # Public Methods
    #

    def create(
            self, name: OptStr, columns: ColsDef,
            metadata: OptMapping = None) -> None:
        """Create table structure.

        This method is motivated by the The SQL `CREATE TABLE`_ statement and
        used to define and initialize the structure of the table and it's
        fields. This includes naming the table, defining and initializing the
        field parameters by column names, types and further constraints, like
        default values, and supplementary table metadata.

        Args:
            name: The table name is required to be a valid identifier as defined
                in [UAX31]_.
            columns: Tuple of *column definitions*. All column definitions
                independent from each other can be given in one of the following
                formats: (1) In order to only specify the name of the column,
                without further information, the colum definition has to be
                given as a string `<name>`. Thereby the choice of `<name>` is
                restricted to valid identifiers, described by [UAX31]_. (2) If,
                additionally to the name, also the data type of the column shall
                be specified, then the column definition has to be given as a
                tuple `(<name>, <type>)`. Thereby `<type>` is required to by a
                valid :class:`type`, like like :class:`str`, :class:`int`,
                :class:`float` or :class:`Date <datetime.datetime>`. (3) Finally
                the column definition may also contain supplementary constraints
                and metadata. In this case the definition has to be given as a
                tuple `(<name>, <type>, <dict>)`, where `<dict>` is dictionary
                which comprises any items, documented by the function
                :func:`dataclasses.fields`.
            metadata: Optional dictionary (or arbitrary mapping), with
                supplementary metadata of the table. This does not comprise
                metadata of the columns, which has to be included within the
                column definitions.

        .. _CREATE TABLE: https://en.wikipedia.org/wiki/Create_(SQL)

        """
        self._set_name(name) # Set Name of the Table
        self._create_metadata(metadata) # Set supplementary Metadata of Table
        self._build_record_class(*columns) # Build Record Class

    def drop(self) -> None:
        """Delete table data and table structure.

        This method is motivated by the the SQL `DROP TABLE`_ statement and used
        to delete the table data and the table structure, given by the field
        declarations, the table metadata and the table identifier.

        Warning:
            This operation should be treated with caution as it can not be
            reverted by calling :meth:`.rollback`.

        .. _DROP TABLE: https://en.wikipedia.org/wiki/Drop_(SQL)

        """
        self.truncate() # Delete Table Data
        self._delete_header() # Delete Table Structure
        self._delete_metadata() # Delete Table Metadata
        self._delete_name() # Delete Table Identifier

    def truncate(self) -> None:
        """Delete table data.

        This method is motivated by the SQL `TRUNCATE TABLE`_ statement and used
        to delete the data inside a table, but not the table structure and
        metadata.

        Warning:
            This operation should be treated with caution as it can not be
            reverted by calling :meth:`.rollback`.

        .. _TRUNCATE TABLE: https://en.wikipedia.org/wiki/Truncate_(SQL)

        """
        self._data = [] # Initialize Storage Table
        self._diff = [] # Initialize Diff Table
        self._index = [] # Initialize Table Master Index

    def commit(self) -> None:
        """Apply data changes to table.

        This method is motivated by the SQL `COMMIT`_ statement and applies
        all data :meth:`updates <.update>`, :meth:`inserts <.insert>` and
        :meth:`deletions <.delete>` since the creation of the table or
        the last :meth:`.commit` and makes all changes visible to other users.

        .. _COMMIT: https://en.wikipedia.org/wiki/Commit_(SQL)

        """
        # Update data table and index
        for rowid in list(range(len(self._data))):
            row = self.row(rowid)
            if not row:
                continue
            state = row._state # pylint: disable=W0212
            if state & record.STATE_DELETE:
                self._data[rowid] = None
                try:
                    self._index.remove(rowid)
                except ValueError:
                    pass
            elif state & (record.STATE_CREATE | record.STATE_UPDATE):
                self._data[rowid] = self._diff[rowid]
                self._data[rowid]._state = 0 # pylint: disable=W0212

        self._diff = [None] * len(self._data) # Initialize Diff Table

    def rollback(self) -> None:
        """Revert data changes from table.

        This method is motivated by the SQL `ROLLBACK`_ statement and reverts
        all data :meth:`updates <.update>`, :meth:`inserts <.insert>` and
        :meth:`deletions <.delete>` since the creation of the table or
        the last :meth:`.commit`.

        .. _ROLLBACK: https://en.wikipedia.org/wiki/Rollback_(SQL)

        """
        # Remove newly created rows from index and reset states of already
        # existing rows
        for rowid in list(range(len(self._data))):
            row = self.row(rowid)
            if not row:
                continue
            state = row._state # pylint: disable=W0212
            if state & record.STATE_CREATE:
                try:
                    self._index.remove(rowid)
                except ValueError:
                    pass
            else:
                self._data[rowid]._state = 0 # pylint: disable=W0212

        self._diff = [None] * len(self._data) # Initialize Diff Table

    def insert(
            self, values: ValuesType = None,
            columns: OptStrTuple = None) -> None:
        """Append one or more records to the table.

        This method is motivated by the SQL `INSERT`_ statement and appends one
        ore more records to the table. The data changes can be organized in
        transactions by :meth:`.commit` and :meth:`.rollback`.

        Args:
            values: Single record, given as :term:`row like` data or multiple
                records given as list of row like data. If the records are given
                as tuples, the corresponding column names are determined from
                the argument *columns*.
            columns: Optional tuple of known column names. By default the
                columns are taken from the attribute :attr:`.columns`.

        .. _INSERT: https://en.wikipedia.org/wiki/Insert_(SQL)

        """
        values = values or tuple([]) # Get default value tuple
        if not isinstance(values, list):
            self._append_row(values, columns)
            return
        for row in values:
            self._append_row(row, columns)

    def update(self, where: OptOp = None, **kwds: Any) -> None:
        """Update values of one or more records from the table.

        This method is motivated by the SQL `UPDATE`_ statement and changes the
        values of all records in the table, that satisfy the `WHERE`_ clause
        given by the keyword argument 'where'. The data changes can be organized
        in transactions by :meth:`.commit` and :meth:`.rollback`.

        Args:
            where: Optional filter operator, which determines, if a row is
                included within the result set or not. By default all rows are
                included within the result set.
            **kwds: Items, which keys are valid column names of the table, and
                the values the new data, stored in the corresponding fields.

        .. _DELETE: https://en.wikipedia.org/wiki/Delete_(SQL)
        .. _WHERE: https://en.wikipedia.org/wiki/Where_(SQL)

        """
        cur = cursor.Cursor(getter=self.row, where=where, parent=self)
        for row in cur:
            row._update(**kwds) # pylint: disable=W0212

    def delete(self, where: OptOp = None) -> None:
        """Delete one or more records from the table.

        This method is motivated by the SQL `DELETE`_ statement and marks all
        records in the table as deleted, that satisfy the `WHERE`_ clause given
        by the keyword argument 'where'. The data changes can be organized in
        transactions by :meth:`.commit` and :meth:`.rollback`.

        Args:
            where: Optional filter operator, which determines, if a row is
                included within the result set or not. By default all rows are
                included within the result set.

        .. _DELETE: https://en.wikipedia.org/wiki/Delete_(SQL)
        .. _WHERE: https://en.wikipedia.org/wiki/Where_(SQL)

        """
        cur = cursor.Cursor(getter=self.row, where=where, parent=self)
        for row in cur:
            row._delete() # pylint: disable=W0212

    def select(
            self, *args: stype.VarLike, where: OptOp = None,
            groupby: cursor.GroupByType = None, dtype: OptType = None,
            orderby: OrderByType = None, reverse: bool = False,
            batchsize: OptInt = None, mode: OptStr = None) -> cursor.Cursor:
        """Get cursor on a specified result set of records from table.

        This method is motivated by the SQL `SELECT`_ statement and creates
        a :class:`Cursor class <nemoa.db.table.Cursor>` instance with specified
        properties.

        Args:
            *args: Optional columns of the result set. If provided the
                columns individually can be given can be given in one of the
                following formats: (1) In order to provide the content of the
                column the column has to be given by a string `<name>`, which is
                required to be known to the underlying object (table, view,
                etc.). (2) In order to aggregate the result set by using
                `groupby`, any non-grouping column has to be given as a tuple
                `(<name>, <operator>)`. Thereby `<operator>` is required to by a
                sequence operator, like :func:`max`, :func:`min` or :func:`sum`
                etc. If no colums is given, the arguments `groupby` and `dtype`
                are ignored, and the result set is returned as raw records.
            where: Optional filter operator, which determines, if a row is
                included within the result set or not. By default all rows are
                included within the result set.
            orderby: Optional parameter, that determine(s) the order of the rows
                within the result set. If provided, the parameter may be given
                as a column name, a tuple of column names or a callable sorting
                function. By default the order is determined by the creation
                order of the rows.
            reverse: Boolean value, which determines if the sorting order of the
                rows is reversed. For the default value ``False`` the sorting
                order is ascending with respect to given column names in the
                orderby parameter, for ``True`` it is descending.
            dtype: Format of the :term:`row like` data, which is used to
                represent the returned values of the result set. By default
                the result set is returned as a list of tuples.
            batchsize: Integer, that specifies the default number of rows which
                is to be fetched by the method :meth:`Cursor.fetch
                <nemoa.table.Cursor.fetch>`. It defaults to 1, meaning to fetch
                a single row at a time. Whether and which batchsize to use
                depends on the application and should be considered with care.
                The batchsize can also be adapted during the lifetime of the
                cursor, which allows dynamic performance optimization.
            mode: Named string identifier for the cursor :py:attr:`.mode`. The
                default cursor mode is 'forward-only indexed'. Note: After
                initializing the curser, it's mode can not be changed anymore.

        Returns:
            New instance of :class:`Cursor class <nemoa.db.table.Cursor>` on
            on a specified result set from the table.

        .. _SELECT: https://en.wikipedia.org/wiki/Select_(SQL)

        """
        # Check arguments and set default values
        if args:
            check.is_subset(
                'columns', set(args), 'table columns', set(self.columns))
        else:
            args = self.columns

        # Create and return cursor
        return cursor.Cursor(
            *args, getter=self.row, where=where, orderby=orderby,
            reverse=reverse, groupby=groupby, batchsize=batchsize, dtype=dtype,
            mode=mode, parent=self)

    def get_metadata(self, key: str) -> Any:
        """Get single entry from table metadata.

        Args:
            key: Name of metadata entry

        Returns:
            Value of metadata entry.

        """
        return self._metadata[key]

    def set_metadata(self, key: str, val: Any) -> None:
        """Change metadata entry of table."""
        self._metadata[key] = val

    def row(self, rowid: int) -> OptRow:
        """Get single row by row ID."""
        try:
            return self._diff[rowid] or self._data[rowid]
        except IndexError as err:
            raise RowLookupError(rowid) from err

    def pack(self) -> None:
        """Remove empty records from data and rebuild table index."""
        # Commit pending changes
        self.commit()

        # Remove empty records
        self._data = list(filter(None.__ne__, self._data))

        # Rebuild table index
        self._index = list(range(len(self._data)))
        for rowid in self._index:
            self._data[rowid]._id = rowid # pylint: disable=W0212

        # Rebuild diff table
        self._diff = [None] * len(self._data)

    #
    # Protected Methods
    #

    def _append_row(self, row: RowLike, columns: OptStrTuple = None) -> None:
        if columns:
            if not isinstance(row, tuple):
                raise TypeError() # TODO
            rec = self._create_record(**dict(zip(columns, row)))
        else:
            rec = self._create_record(row)
        self._data.append(None)
        self._diff.append(rec)
        self._append_rowid(rec._id) # pylint: disable=W0212

    def _append_rowid(self, rowid: int) -> None:
        self._index.append(rowid)

    def _create_metadata(self, mapping: OptMapping = None) -> None:
        check.has_opt_type("'metadata'", mapping, Mapping)
        self._metadata = mapping or {}
        self._metadata_proxy = MappingProxy(self._metadata)

    def _delete_metadata(self) -> None:
        del self._metadata_proxy
        del self._metadata

    def _build_record_class(self, *args: record.ColDef) -> None:
        # Dynamically create a new record class
        self._record = record.build(*args,
            newid=self._get_new_rowid,
            delete=self._remove_rowid,
            restore=self._append_rowid,
            update=self._update_row_diff,
            revoke=self._remove_row_diff)
        self.truncate() # Initialize table data

    def _create_record(self, data: RowLike) -> Row:
        if isinstance(data, tuple):
            return self._record(*data)
        if isinstance(data, Mapping):
            return self._record(**data)
        if isinstance(data, record.Record):
            keys = self.columns
            vals = tuple(getattr(data, key, None) for key in keys)
            return self._record(**dict(zip(keys, vals)))
        raise InvalidTypeError("'data'", data, RowLikeClasses)

    def _delete_header(self) -> None:
        self.truncate() # Delete table data
        del self._record # Delete record constructor

    def _get_new_rowid(self) -> int:
        return len(self._data)

    def _get_last_row(self, column: str) -> OptRow:
        try:
            return self._data[-1]
        except IndexError:
            return None

    def _get_columns(self) -> StrTuple:
        return tuple(field.name for field in self.fields)

    def _get_fields(self) -> OptFieldTuple:
        if not hasattr(self, '_record') or not self._record:
            return None
        return record.get_fields(self._record)

    def _get_name(self) -> str:
        return self._name or self._default_name()

    def _default_name(self) -> str:
        return 'unkown'

    def _delete_name(self) -> None:
        del self._name

    def _set_name(self, name: OptStr) -> None:
        if isinstance(name, str):
            check.is_identifier(f"'name'", name)
            self._name = name
        else:
            self._name = self._default_name()

    def _get_metadata_proxy(self) -> OptMappingProxy:
        return getattr(self, '_metadata_proxy', None)

    def _remove_row_diff(self, rowid: int) -> None:
        self._diff[rowid] = None

    def _remove_rowid(self, rowid: int) -> None:
        self._index.remove(rowid)

    def _update_row_diff(self, rowid: int, **kwds: Any) -> None:
        row = self.row(rowid)
        if not row: # Row has already been deleted
            return
        new = record.create_from(row, **kwds)
        self._diff[rowid] = new

#
# Proxy Class
#

class Proxy(Table, abc.Proxy):
    """Abstract Base Class for Table Proxies.

    Args:
        proxy_mode: Optional Integer, that determines the operation mode of the
            proxy.
        parent: Reference to parent :class:`attribute group
            <nemoa.base.attrib.Group>`, which is used for inheritance and
            shared attributes. By default no parent is referenced.

    """

    _proxy_mode: property = attrib.MetaData(dtype=int, default=1)

    #
    # Special Methods
    #

    def __init__(
            self, proxy_mode: OptInt = None,
            parent: Optional[attrib.Group] = None) -> None:

        # Initialize Proxy Base Class
        abc.Proxy.__init__(self)

        # Initialize Empty Table
        Table.__init__(self, parent=parent)

        # Initialize Table Proxy Parameters
        if proxy_mode is None:
            proxy_mode = PROXY_MODE_FLAG_CACHE # Set default proxy mode
        self._proxy_mode = proxy_mode

    def _post_init(self) -> None:
        # Retrieve all rows from source if table is cached
        if self._proxy_mode & PROXY_MODE_FLAG_CACHE:
            self.pull()

    #
    # Public Methods
    #

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
