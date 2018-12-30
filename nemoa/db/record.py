# -*- coding: utf-8 -*-
"""Record Class."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import abc
import contextlib
import itertools
import dataclasses
from nemoa.base import check
from nemoa.errors import InvalidTypeError
from nemoa.types import Tuple, StrDict, StrList, StrTuple, void
from nemoa.types import OptOp, Any, Type, Union, Optional, TypeHint

#
# Structural Types
#

Field = dataclasses.Field
FieldTuple = Tuple[Field, ...]
ColDefA = str # Column definition: name
ColDefB = Tuple[str, type] # Column definition: name and type
ColDefC = Tuple[str, type, StrDict] # Column definition: name, type, constraints
ColDefD = Tuple[str, type, Field] # Column definition: name, type, constraints
ColDef = Union[ColDefA, ColDefB, ColDefC, ColDefD] # Column definition
ColsDef = Tuple[ColDef, ...]
OptColsDef = Optional[ColsDef]

#
# Constants
#

STATE_CREATE = 0b0001
STATE_UPDATE = 0b0010
STATE_DELETE = 0b0100

#
# Record Base Class
#

class Record(abc.ABC):
    """Abstract base class for :mod:`dataclasses` based records.

    Args:
        *args: Arguments, that are valid with respect to the column definitions
            of derived :mod:'dataclasses'.
        **kwds: Keyword arguments, that are valid with respect to the column
            definitions of derived :mod:'dataclasses'.

    """

    __slots__: StrTuple = ('_id', '_name', '_state')

    _id: int
    _name: str
    _state: int

    def __post_init__(self, *args: Any, **kwds: Any) -> None:
        self._validate()
        self._id = self._get_newid()
        self._state = STATE_CREATE

    def _validate(self) -> None:
        """Check validity of the field types."""
        fields = getattr(self, '__dataclass_fields__', {})
        for name, field in fields.items():
            if isinstance(field.type, str):
                continue # Do not type check structural types like 'typing.Any'
            value = getattr(self, name)
            check.has_type(f"field '{name}'", value, field.type)

    def _delete(self) -> None:
        """Mark record as deleted and remove it's ID from index."""
        if not self._state & STATE_DELETE:
            self._state |= STATE_DELETE
            self._delete_hook(self._id)

    def _update(self, **kwds: Any) -> None:
        """Mark record as updated and write the update to diff table."""
        if not self._state & STATE_UPDATE:
            self._state |= STATE_UPDATE
            self._update_hook(self._id, **kwds)

    def _restore(self) -> None:
        """Mark record as not deleted and append it's ID to index."""
        if self._state & STATE_DELETE:
            self._state &= ~STATE_DELETE
            self._restore_hook(self._id)

    def _revoke(self) -> None:
        """Mark record as not updated and remove the update from diff table."""
        if self._state & STATE_UPDATE:
            self._state &= ~STATE_UPDATE
            self._revoke_hook(self._id)

    @abc.abstractmethod
    def _get_newid(self) -> int:
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
# Builder, Constructor and helper functions
#

def build(columns: ColsDef, newid: OptOp = None, **kwds: Any) -> Type[Record]:
    """Create a new subclass of the Record class.

    Args:
        columns: Tuple of *column definitions*. All column definitions
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
        newid: Optional reference to a method, which returns the current ID of
            a new instance of the Record class. By default the Record class
            uses an internal Iterator.
        **kwds: Optional references to methods, which are bound to specific
            events of the new Record class. These events are: 'delete',
            'restore', 'update' and 'revoke'. By default no events are hooked.

    Returns:
        New subclass of the Record class.

    """
    # Check column defnitions and convert them to field descriptors, as required
    # by dataclasses.make_dataclass()
    check.has_type("'columns'", columns, tuple)
    fields: list = []
    names: StrList = []
    for column in columns:
        if isinstance(column, str):
            fields.append(column)
            names.append(column)
            continue
        check.has_type(f'column {column}', column, tuple)
        check.has_size(f'column {column}', column, min_size=2, max_size=3)
        check.has_type('first argument', column[0], str)
        check.has_type('second argument', column[1], TypeHint)
        if len(column) == 2:
            fields.append(column)
            names.append(column[0])
            continue
        check.has_type('third argument', column[2], (Field, dict))
        if isinstance(column[2], Field):
            fields.append(column)
            names.append(column[0])
            continue
        field = dataclasses.field(**column[2])
        names.append(column[0])
        fields.append(column[:2] + (field,))

    # Dynamically create a dataclass, which is inherited from Record class.
    # Thereby create an ampty '__slots__' attribute to avoid collision with
    # default values (which in dataclasses are stored as class variables),
    # while avoiding the creation of a '__dict__' attribute
    namespace: StrDict = {}
    if newid and callable(newid):
        namespace['_get_newid'] = newid
    else:
        counter = itertools.count() # Infinite iterator
        namespace['_get_newid'] = lambda obj: next(counter)
    hooks = {
        'delete': '_delete_hook', 'restore': '_restore_hook',
        'update': '_update_hook', 'revoke': '_revoke_hook'}
    for key in hooks:
        namespace[hooks[key]] = kwds.get(key, void)
    namespace['__slots__'] = tuple()
    dataclass = dataclasses.make_dataclass(
        Record.__name__, fields, bases=(Record, ), namespace=namespace)

    # Dynamically create a new class, which is inherited from dataclass,
    # with corrected __slots__ attribute.
    return type(dataclass.__name__, (dataclass,), {'__slots__': names})

def create_from(record: Record, **changes: Any) -> Record:
    if not is_record(record):
        raise InvalidTypeError('record', record, Record)
    newrec = dataclasses.replace(record, **changes)
    with contextlib.suppress(AttributeError):
        newrec._id = record._id # pylint: disable=W0212
    with contextlib.suppress(AttributeError):
        newrec._state = record._state # pylint: disable=W0212
    with contextlib.suppress(AttributeError):
        newrec._name = record._name # pylint: disable=W0212
    return newrec

def is_record(record: object) -> bool:
    if not isinstance(record, Record):
        return False
    if not dataclasses.is_dataclass(record):
        return False
    return True

def get_fields(record: Record) -> FieldTuple:
    return dataclasses.fields(record)
