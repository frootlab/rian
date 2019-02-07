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
"""Cursor Class."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import random
from typing import List, NewType, Tuple, Union, Optional
from nemoa.base import attrib
from nemoa.db import record
from nemoa.math import operator, stype
from nemoa.errors import InvalidTypeError, NemoaError
from nemoa.types import StrList, StrTuple, OptIntList, OptOp, Callable, OptInt
from nemoa.types import OptStr, Iterator, Mapping, SeqOp, AnyOp, OptType, BoolOp

#
# Exceptions
#

class CursorError(NemoaError):
    """Base Class for Cursor Errors."""

class ModeError(CursorError):
    """Raise when a procedure is not supported by a cursor mode."""

    def __init__(self, mode: str, proc: OptStr = None) -> None:
        if proc:
            msg = f"{proc} is not supported by {mode} cursors"
        else:
            msg = f"unknown cursor mode '{mode}'"
        super().__init__(msg)

#
# Structural Types
#

# Various
PredLike = Optional[Union[str, BoolOp]]
OrderByType = Optional[Union[str, StrList, StrTuple, SeqOp]]
GroupByType = OrderByType
AggAttr = Union[str, Tuple[str, AnyOp]]
OptSeqOp = Optional[SeqOp]

# Variables
ColNames = Tuple[str, ...]
OptColNames = Optional[ColNames]

# Rows
Row = NewType('Row', record.Record)
OptRow = Optional[Row]
RowList = List[Row]
RowLike = Union[tuple, Mapping, Row]
RowLikeList = Union[RowList, List[tuple], List[Mapping]]

#
# Constants
#

MODE_BUFFERED = 0b0001
MODE_INDEXED = 0b0010
MODE_SCROLLABLE = 0b0100
MODE_RANDOM = 0b1000

#
# Cursor Class
#

class Cursor(attrib.Group):
    """Cursor Class.

    Args:
        *args: Optional :term:`variable defintions<variable defintion>`. If
            no variables are defined, the arguments `groupby` and `dtype` are
            ignored, and the result set is returned as raw records.
        where: Optional filter, which determines if a row is included within the
            result set or not. If provided, the filter ether can be given as
            a clause (string) which uses the field identifiers of the records as
            variables, or as a predicate (callable), which operates on the
            records. By default all rows are included within the result set.
        groupby:
        having:
        orderby: Optional parameter, that determine(s) the order of the rows
            within the result set. If provided, the parameter may be given
            as a column name, a tuple of column names or a callable sorting
            function. By default the order is determined by the creation
            order of the rows.
        index: List of row IDs, that are traversed by the cursor. By default the
            attribute '_index' of the parent object is used.
        mode: Named string identifier for the cursor :py:attr:`.mode`. The
            default cursor mode is 'forward-only indexed'. Note: After
            initializing the curser, it's mode can not be changed anymore.
        batchsize: Integer, that specifies the default number of rows which is
            to be fetched by the method :meth:`.fetch`. It defaults to 1,
            meaning to fetch a single row at a time. Whether and which batchsize
            to use depends on the application and should be considered with
            care. The batchsize can also be adapted during the lifetime of the
            cursor, which allows dynamic performance optimization.
        getter: Method, which is used to fetch single rows by their row ID.
        reverse: Boolean value, which determines if the sorting order of the
            rows is reversed. For the default value ``False`` the sorting
            order is ascending with respect to given column names in the
            orderby parameter, for ``True`` it is descending.
        parent: Reference to parent :class:'attribute group
            <nemoa.base.attrib.Group>', which is used for inheritance and
            shared attributes. By default no parent is referenced.
        dtype: Optional type of the returned records. Supported types are
            :class:`tuple` and :class:`dict`. The default type of the returned
            records depends on the variable definitions. If no variables are
            defined, the records by default are returned as instances of the
            :class:`Record class <nemoa.db.record.Record>`, if variables are
            defined, then the records by default are returned as tuples.

    """

    #
    # Public Attributes
    #

    mode: property = attrib.Virtual('_get_mode')
    mode.__doc__ = """
    The read-only attribute :term:`cursor mode` provides information about the
    *scrolling type* and the *operation mode* of the cursor.
    """

    batchsize: property = attrib.MetaData(dtype=int, default=1)
    """
    The read-writable integer attribute *batchsize* specifies the default number
    of rows which is to be fetched by the method :meth:`.fetch`. It defaults
    to 1, meaning to fetch a single row at a time. Whether and which batchsize
    to use depends on the application and should be considered with care. The
    batchsize can also be adapted during the lifetime of the cursor, which
    allows dynamic performance optimization.
    """

    rowcount: property = attrib.Virtual('_get_rowcount')
    """
    The read-only integer attribute *rowcount* identifies the current number of
    rows within the cursor.
    """

    #
    # Protected Attributes
    #

    _mode_id: property = attrib.MetaData(dtype=int, factory='_default_mode')
    _index: property = attrib.MetaData(dtype=list, inherit=True)
    _getter: property = attrib.Temporary(dtype=Callable)
    _groupby: property = attrib.Temporary(dtype=Callable, default=None)
    _sorter: property = attrib.Temporary(dtype=Callable, default=None)
    _mapper: property = attrib.Temporary(dtype=Callable, default=None)
    _where: property = attrib.Temporary(dtype=Callable, default=None)
    _buffer: property = attrib.Temporary(dtype=list, default=[])

    #
    # Special Methods
    #

    def __init__(
            self, *args: stype.VarLike, where: PredLike = None,
            groupby: GroupByType = None, having: PredLike = None,
            orderby: OrderByType = None, reverse: bool = False,
            batchsize: OptInt = None, dtype: OptType = None,
            index: OptIntList = None, getter: OptOp = None,
            mode: OptStr = None, parent: Optional[attrib.Group] = None) -> None:
        # Initialize Attribute Group with parent Attribute Group
        super().__init__(parent=parent)

        # Update Cursor Parameters (The order is important)
        self._set_mode(mode)
        self._getter = getter
        self._set_filter(where)
        self._set_aggregator(*args, groupby=groupby, having=having)
        self._set_sorter(orderby, reverse=reverse)
        self._set_mapper(*args, dtype=dtype)

        # Initialize index
        if index is not None:
            self._index = index

        # Set mode and batchsize
        if batchsize:
            self.batchsize = batchsize

        # Initialize cursor
        if self._mode_id & MODE_INDEXED:
            self._create_index() # Initialize index
        if self._mode_id & MODE_BUFFERED:
            self._create_buffer() # Initialize buffer
        self.reset() # Initialize iterator

    def __iter__(self) -> Iterator:
        self.reset()
        return self

    def __next__(self) -> Row:
        return self.next()

    def __len__(self) -> int:
        return self.rowcount

    #
    # Public Methods
    #

    def fetch(self, size: OptInt = None) -> RowList:
        """Fetch rows from the result set.

        Args:
            size: Integer value, which represents the number of rows, which is
                fetched from the result set. For the given size -1 all remaining
                rows from the result set are fetched. By default the number of
                rows is given by the cursors attribute :attr:`.batchsize`.

        Returns:
            Result set given by a list of :term:`row like` data.

        """
        # TODO: Scrollable cursors are defined on sequences not on iterables:
        # the cursor can use operations, such as FIRST, LAST, PRIOR, NEXT,
        # RELATIVE n, ABSOLUTE n to navigate the results
        if size is None:
            size = self.batchsize
        if self._mode_id & MODE_RANDOM and size < 1:
            raise ModeError(self.mode, 'fetching all rows')
        finished = False
        rows: RowList = []
        while not finished:
            try:
                rows.append(self.next())
            except StopIteration:
                finished = True
            else:
                finished = 0 < size <= len(rows)

        if self._mapper:
            return list(map(self._mapper, rows))
        return rows

    def next(self) -> Row:
        """Return next row that matches the given filter."""
        mode = self._mode_id
        if mode & MODE_BUFFERED:
            return self._get_next_from_buffer()
        if mode & MODE_INDEXED:
            return self._get_next_from_fixed_index()
        # TODO: For dynamic cursors implement _get_next_from_dynamic_index()
        return self._get_next_from_fixed_index()

    def reset(self) -> None:
        """Reset cursor position before the first record."""
        mode = self._mode_id
        if mode & MODE_BUFFERED: # Iterate over fixed result set
            self._iter_buffer = iter(self._buffer)
        elif mode & MODE_INDEXED: # Iterate over fixed index
            self._iter_index = iter(self._index)
        else: # TODO: handle case for dynamic cursors by self._iter_table
            self._iter_index = iter(self._index)

    #
    # Protected Methods
    #

    def _create_index(self) -> None:
        if isinstance(self._index, list):
            self._index = self._index.copy()
        else:
            self._index = []

    def _create_buffer(self) -> None:
        # List all operators, which are required to create the result set in
        # the order of their appearance
        ops = [lambda seq: map(self._getter, seq)] # Getter
        if self._where:
            ops.append(lambda seq: filter(self._where, seq)) # Row filter
        if self._groupby:
            ops.append(self._groupby)
        if self._having:
            ops.append(lambda seq: filter(self._having, seq))
        if self._sorter:
            ops.append(self._sorter)
        ops.append(list)

        # Compose and apply the operators to the index
        self._buffer = operator.compose(*ops[::-1])(self._index)

    def _set_filter(self, where: PredLike = None) -> None:
        if where is None:
            self._where = None
            return

        if callable(where):
            # TODO: check if where is a valid record predicate
            self._where = where
            return

        if isinstance(where, str):
            self._where = operator.Lambda(where, domain=object)
            return

        raise InvalidTypeError('where', where, (type(None), str)) # TODO: Type!

    def _set_aggregator(
            self, *args: stype.VarLike, groupby: GroupByType = None,
            having: PredLike = None) -> None:

        if not groupby:
            self._groupby = None
            self._having = None
            return

        # In order to provide a grouped result set, the cursor requires to
        # preprocess the fields to variables. This in turn needs the cursor to
        # be buffered and countable in the sense to support counting the rows
        # (which is not possible for random cursors).
        if not args:
            raise CursorError(
                'group aggregation requires the definition of variables')
        if not self._mode_id & MODE_BUFFERED:
            raise ModeError(
                "group aggregation requires a static cursor "
                f"not '{self.mode}'")
        if self._mode_id & MODE_RANDOM:
            raise ModeError(
                "group aggregation requires a forward-only cursor "
                f"not '{self.mode}'")

        # Create group aggragation operator
        self._groupby = operator.create_group_aggregator(
            *args, key=groupby, domain=object)

        if having is None:
            self._having = None
            return

        if callable(having):
            # TODO: check if having is a valid group predicate
            self._having = having # type: ignore
            return

        # Get variable names
        variables = map(stype.create_variable, args)
        names = tuple(var.name for var in variables)

        if isinstance(having, str):
            self._having = operator.Lambda(having, domain=(tuple, names))
            return

        raise InvalidTypeError('having', having, (type(None), str)) # TODO

    def _set_sorter(
            self, orderby: OrderByType, reverse: bool = False) -> None:

        # If sorting is not used, the sorting operator is the identity
        if not (orderby or reverse):
            self._sorter = None
            return

        # Validate sorting parameters
        if self._mode_id & MODE_RANDOM:
            raise ModeError(
                f"sorting requires a finite cursor not '{self.mode}'")
        if not self._mode_id & MODE_BUFFERED:
            raise ModeError(
                f"sorting requires a static cursor not '{self.mode}'")

        # If 'orderby' is given as an operator, set it as sorter
        if callable(orderby):
            # TODO: check if orderby is a valid sorter
            self._sorter = orderby
            return

        # If 'orderby' is given as a string or as a tuple of strings, use it as
        # the sorting key of a created sorting operator
        if isinstance(orderby, str):
            keys = [orderby]
        elif isinstance(orderby, (list, tuple)):
            keys = list(orderby)
        else:
            keys = []
        domain = tuple if self._groupby else object
        self._sorter = operator.create_sorter(
            *keys, domain=domain, reverse=reverse)

    def _set_mapper(self, *args: stype.VarLike, dtype: OptType = None) -> None:
        # Validate Arguments
        if dtype and not args:
            raise CursorError(
                'mapping to a given target type '
                'requires the definition of variables')

        # Get variable names
        variables = map(stype.create_variable, args)
        names = tuple(var.name for var in variables)

        # If the result set is aggregated by a grouping operator, the mapper
        # acts on tuples as an itemgetter, which requires the specification of
        # the tuple variables.
        if self._groupby:
            self._mapper = operator.Getter(
                *names, domain=(tuple, names), target=dtype)
            return

        # If the result set is not aggregated, and the target type is specified,
        # then the mapper acts on record objects as an attribute getter with
        # a subsequent converter
        if dtype:
            self._mapper = operator.Getter(*names, domain=object, target=dtype)
            return

        # If the result set is not aggregated, and the target type is not
        # specified (or None), then the rows are returned as records and the
        # mapper is the identity function
        self._mapper = None

    def _default_mode(self) -> int:
        if self._sorter:
            return MODE_BUFFERED
        return MODE_INDEXED

    def _get_next_from_fixed_index(self) -> Row:
        is_random = self._mode_id & MODE_RANDOM
        matches = False
        while not matches:
            if is_random:
                rowid = random.randrange(len(self._index))
            else:
                rowid = next(self._iter_index)
            row = self._getter(rowid)
            if self._where:
                matches = self._where(row)
            else:
                matches = True
        return row

    def _get_next_from_buffer(self) -> Row:
        if self._mode_id & MODE_RANDOM:
            rowid = random.randrange(len(self._buffer))
            return self._buffer[rowid]
        return next(self._iter_buffer)

    def _get_mode(self) -> str:
        mode = self._mode_id
        tokens = []

        # Add name of traversal mode
        if mode & MODE_RANDOM:
            tokens.append('random')
        elif mode & MODE_SCROLLABLE:
            tokens.append('scrollable')

        # Add name of operation mode
        if mode & MODE_BUFFERED:
            tokens.append('static')
        elif mode & MODE_INDEXED:
            tokens.append('indexed')
        else:
            tokens.append('dynamic')

        return ' '.join(tokens)

    def _set_mode(self, name: OptStr = None) -> None:
        if name is None:
            return

        mode = 0
        name = name.strip(' ').lower()

        # Set traversal mode flags
        if 'random' in name:
            mode |= MODE_RANDOM
        elif 'scrollable' in name:
            mode |= MODE_SCROLLABLE

        # Set operation mode flags
        if 'static' in name:
            mode |= MODE_BUFFERED | MODE_INDEXED
        elif 'indexed' in name:
            mode |= MODE_INDEXED

        self._mode_id = mode

    def _get_rowcount(self) -> int:
        mode = self._mode_id
        if mode & MODE_RANDOM:
            raise ModeError(self.mode, 'counting rows')
        if mode & MODE_BUFFERED:
            return len(self._buffer)
        if self._where:
            raise ModeError(self.mode, 'counting filtered rows')
        return len(self._index)
