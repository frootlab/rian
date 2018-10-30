# -*- coding: utf-8 -*-
"""DB-API 2.0 database interfaces."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
from nemoa.core.container import BaseContainer, VirtualAttr

class Cursor(BaseContainer, ABC):
    """Database Cursor.

    These objects represent a database cursor, which is used to manage the
    context of a fetch operation. Cursors created from the same connection are
    not isolated, i.e., any changes done to the database by a cursor are
    immediately visible by the other cursors. Cursors created from different
    connections can or can not be isolated, depending on how the transaction
    support is implemented (see also the connection's .rollback() and .commit()
    methods).

    """

    #
    # Cursor attributes
    #

    description: property = VirtualAttr(
        list, getter='_get_description', readonly=True)
    description.__doc__ = """
    Sequence of 7-item sequences containing information about one result column:
    name, type_code, display_size, internal_size, precision, scale, null_ok
    The first two items (name and type_code) are mandatory, the other five are
    optional and are set to None if no meaningful values can be provided.
    This attribute will be None for operations that do not return rows or if the
    cursor has not had an operation invoked via the .execute*() method yet.
    """

    def _get_description(self) -> list:
        pass

    rowcount: property = VirtualAttr(int, getter='_get_rowcount', readonly=True)
    description.__doc__ = """
    This read-only attribute specifies the number of rows that the last
    execute*() produced (for DQL statements like SELECT) or affected (for DML
    statements like UPDATE or INSERT). The attribute is -1 in case no
    .execute*() has been performed on the cursor or the rowcount of the last
    operation is cannot be determined by the interface.
    """

    def _get_rowcount(self) -> int:
        pass

    #
    # Cursor Methods
    #

class Connection(ABC):
    """Database Connection."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection now.

        The connection will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the connection. The same applies to all cursor objects trying to use the
        connection. Note that closing a connection without committing the
        changes first will cause an implicit rollback to be performed.
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit any pending transaction to the database.

        Note that if the database supports an auto-commit feature, this must be
        initially off. An interface method may be provided to turn it back on.
        Database modules that do not support transactions should implement this
        method with void functionality.
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction (if supported).

        In case a database does provide transactions this method causes the
        database to roll back to the start of any pending transaction. Closing a
        connection without committing the changes first will cause an implicit
        rollback to be performed.
        """
        pass

    @abstractmethod
    def cursor(self) -> Cursor:
        """Return a new Cursor Object using the connection.

        If the database does not provide a direct cursor concept, the module
        will have to emulate cursors using other means to the extent needed by
        this specification.
        """
        pass
