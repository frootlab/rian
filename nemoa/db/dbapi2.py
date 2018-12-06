# -*- coding: utf-8 -*-
"""DB-API 2.0 database interfaces.

This module is a reference for the required exceptions, base classes, module
attributes and module functions specified in the Python Database API (DB-API)
Specification 2.0 :PEP:`249`.

Module attributes:
    apilevel:
        String constant stating the supported DB-API level.
    threadsafety:
        Integer constant stating the level of thread safety the interface
        supports.
    paramstyle:
        String constant stating the type of parameter marker formatting expected
        by the interface.

Constructor function:
    connect(...) -> Connection
        Constructor for creating a connection to the database. Returns a
        Connection Object. It takes a number of parameters which are database
        dependent.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
from nemoa.base import attrib
from nemoa.types import Any, OptList, OptInt, OptBool
from nemoa.errors import NemoaError

#
# DB-API 2.0 Exceptions
#

class Error(NemoaError):
    """DB-API Error.

    Exception that is the base class of all other error exceptions. You can use
    this to catch all errors with one single except statement. Warnings are not
    considered errors and thus should not use this class as base. It must be a
    subclass of the Python StandardError (defined in the module exceptions).
    """

class Warning(NemoaError): # pylint: disable=W0622
    """DB-API Warning.

    Exception raised for important warnings like data truncations while
    inserting, etc. It must be a subclass of the Standard DBIError.
    """

class InterfaceError(Error):
    """DB-API InterfaceError.

    Exception raised for errors that are related to the database interface
    rather than the database itself. It must be a subclass of Error.
    """

class DatabaseError(Error):
    """DB-API DatabaseError.

    Exception raised for errors that are related to the database. It must be a
    subclass of Error.
    """

class InternalError(DatabaseError):
    """DB-API InternalError.

    Exception raised when the database encounters an internal error, e.g. the
    cursor is not valid anymore, the transaction is out of sync, etc. It must
    be a subclass of DatabaseError.
    """

class OperationalError(DatabaseError):
    """DB-API OperationalError.

    Exception raised for errors that are related to the database's operation and
    not necessarily under the control of the programmer, e.g. an unexpected
    disconnect occurs, the data source name is not found, a transaction could
    not be processed, a memory allocation error occurred during processing, etc.
    It must be a subclass of DatabaseError.
    """

class ProgrammingError(DatabaseError):
    """DB-API ProgrammingError.

    Exception raised for programming errors, e.g. table not found or already
    exists, syntax error in the SQL statement, wrong number of parameters
    specified, etc. It must be a subclass of DatabaseError.
    """

class IntegrityError(DatabaseError):
    """DB-API IntegrityError.

    Exception raised when the relational integrity of the database is affected,
    e.g. a foreign key check fails. It must be a subclass of DatabaseError.
    """

class DataError(DatabaseError):
    """DB-API DataError.

    Exception raised for errors that are due to problems with the processed data
    like division by zero, numeric value out of range, etc. It must be a
    subclass of DatabaseError.
    """

class NotSupportedError(DatabaseError):
    """DB-API NotSupportedError.

    Exception raised in case a method or database API was used which is not
    supported by the database, e.g. requesting a `rollback` on a connection
    that does not support transaction or has transactions turned off. It must be
    a subclass of DatabaseError.
    """

#
# DB-API 2.0 Cursor Class
#

class Cursor(attrib.Container, ABC):
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

    arraysize: property = attrib.MetaData(classinfo=int, default=1)
    arraysize.__doc__ = """
    This read/write attribute specifies the number of rows to fetch at a time
    with `fetchmany`. It defaults to 1 meaning to fetch a single row at a time.
    Implementations must observe this value with respect to the `fetchmany`
    method, but are free to interact with the database a single row at a time.
    It may also be used in the implementation of `executemany`.
    """

    description: property = attrib.Virtual(fget='_get_description')
    description.__doc__ = """
    Sequence of 7-item sequences containing information about one result column:
    name, type_code, display_size, internal_size, precision, scale, null_ok
    The first two items (name and type_code) are mandatory, the other five are
    optional and are set to None if no meaningful values can be provided.
    This attribute will be None for operations that do not return rows or if the
    cursor has not had an operation invoked via the .execute*() method yet.
    """

    @abstractmethod
    def _get_description(self) -> list:
        pass

    rowcount: property = attrib.Virtual(fget='_get_rowcount')
    description.__doc__ = """
    This read-only attribute specifies the number of rows that the last
    execute*() produced (for DQL statements like SELECT) or affected (for DML
    statements like UPDATE or INSERT). The attribute is -1 in case no
    .execute*() has been performed on the cursor or the rowcount of the last
    operation is cannot be determined by the interface.
    """

    @abstractmethod
    def _get_rowcount(self) -> int:
        pass

    #
    # Cursor Methods
    #

    @abstractmethod
    def callproc(self, procname: str, *args: Any, **kwds: Any) -> Any:
        """Call stored database procedure.

        Call a stored database procedure with the given name. The sequence of
        parameters must contain one entry for each argument, that the procedure
        expects. The result of the call is returned as modified copy of the
        input sequence. Input parameters are left untouched, output and
        input/output parameters replaced with possibly new values.

        The procedure may also provide a result set as output. This must then be
        made available through the standard .fetch*() methods.

        If the database does not support the functionality required by the
        method, the interface should throw an exception in case the method is
        used.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the cursor.
        """
        pass

    @abstractmethod
    def execute(self, operation: str, *args: Any) -> Any:
        """Prepare and execute a database operation (query or command).

        Parameters may be provided as sequence or mapping and will be bound to
        variables in the operation. Variables are specified in a
        database-specific notation, which is identified by the module global
        `paramstyle`.

        A reference to the operation will be retained by the cursor. If the same
        operation object is passed in again, then the cursor can optimize its
        behavior. This is most effective for algorithms where the same operation
        is used, but different parameters are bound to it.

        For maximum efficiency when reusing an operation, it is best to use the
        `setinputsizes` method to specify the parameter types and sizes ahead
        of time. It is legal for a parameter to not match the predefined
        information; the implementation should compensate, possibly with a loss
        of efficiency.

        The parameters may also be specified as list of tuples to e.g. insert
        multiple rows in a single operation, but this kind of usage is
        deprecated: .executemany() should be used instead.
        """
        pass

    @abstractmethod
    def executemany(self, operation: str, seq_of_parameters: list) -> Any:
        """Prepare and execute database operation for multiple parameters.

        Prepare a database operation (query or command) and then execute it
        against all parameter sequences or mappings found in the sequence
        *seq_of_parameters*.

        Modules are free to implement this method using multiple calls to the
        `execute` method or by using array operations to have the database
        process the sequence as a whole in one call.

        Use of this method for an operation which produces one or more result
        sets constitutes undefined behavior, and the implementation is permitted
        (but not required) to raise an exception when it detects that a result
        set has been created by an invocation of the operation.
        """
        pass

    @abstractmethod
    def fetchone(self) -> OptList:
        """Fetch the next row of a query result.

        Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.

        An Error (or subclass) exception is raised if the previous call to
        `execute` did not produce any result set or no call was issued yet.
        """
        pass

    @abstractmethod
    def fetchmany(self, size: OptInt) -> list:
        """Fetch the next set of rows of a query result.

        Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when no
        more rows are available.

        The number of rows to fetch per call is specified by the parameter. If
        it is not given, the cursor's arraysize determines the number of rows to
        be fetched. The method should try to fetch as many rows as indicated by
        the size parameter. If this is not possible due to the specified number
        of rows not being available, fewer rows may be returned.

        An Error (or subclass) exception is raised if the previous call to
        `execute` did not produce any result set or no call was issued yet.

        Note there are performance considerations involved with the size
        parameter. For optimal performance, it is usually best to use the
        `arraysize` attribute. If the size parameter is used, then it is best
        for it to retain the same value from one `fetchmany` call to the next.
        """
        pass

    @abstractmethod
    def fetchall(self) -> list:
        """Fetch all remaining rows of a query result.

        Fetch all remaining rows of a query result, returning them as a sequence
        of sequences (e.g. a list of tuples). Note that the cursor's arraysize
        attribute can affect the performance of this operation.

        An Error (or subclass) exception is raised if the previous call to
        `execute` did not produce any result set or no call was issued yet.
        """
        pass

    @abstractmethod
    def nextset(self) -> OptBool:
        """Skip cursor to the next available set (if supported).

        This method will make the cursor skip to the next available set,
        discarding any remaining rows from the current set. If there are no more
        sets, the method returns None. Otherwise, it returns a true value and
        subsequent calls to the `fetch*` methods will return rows from the next
        result set.

        An Error (or subclass) exception is raised if the previous call to an
        `execute*` method did not produce any result set or no call was issued
        yet.

        If the database does not support the functionality required by the
        method, the interface should throw an exception in case the method is
        used.
        """
        pass

    @abstractmethod
    def setinputsizes(self, sizes: list) -> None:
        """Set input sizes for database operations (query or command).

        This can be used before a call to `execute*` to predefine memory areas
        for the operation's parameters. *sizes* is specified as a sequence with
        one item for each input parameter. The item should be a type object that
        corresponds to the input that will be used, or it should be an integer
        specifying the maximum length of a string parameter. If the item is
        None, then no predefined memory area will be reserved for that column
        (this is useful to avoid predefined areas for large inputs).

        This method would be used before the `execute*` method is invoked.
        Implementations are free to have this method do nothing and users are
        free to not use it.
        """
        pass

    @abstractmethod
    def setoutputsize(self, size: int, column: OptInt) -> None:
        """Set a column buffer size for fetches of large columns.

        The column is specified as an index into the result sequence. Not
        specifying the column will set the default size for all large columns in
        the cursor.

        This method would be used before an `execute*` method is invoked.
        Implementations are free to have this method do nothing and users are
        free to not use it.
        """
        pass

#
# DB-API 2.0 Connection Class
#

class Connection(attrib.Container, ABC):
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
