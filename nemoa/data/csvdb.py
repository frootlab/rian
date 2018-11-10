# -*- coding: utf-8 -*-
"""DB-API 2.0 interface for CSV-files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path
from nemoa.types import FileOrPathLike, OptStr, OptIntTuple, OptStrList, OptInt
from nemoa.base.file import csvfile, inifile
from nemoa.data import dbapi2
from nemoa.errors import NemoaError

#
# DB-API 2.0 Module globals
#

apilevel = '2.0'
threadsafety = 0
paramstyle = 'pyformat'

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
# DB-API 2.0 Connection Class
#

class Connection(dbapi2.Connection):
    pass

def load_csv(
        file: FileOrPathLike, delim: OptStr = None,
        labels: OptStrList = None, usecols: OptIntTuple = None,
        namecol: OptInt = None) -> dict:
    """ """
    # Get configuration from CSV header
    comment = csvfile.CSVFile(file).comment

    structure = {
        'name': str,
        'branch': str,
        'version': int,
        'about': str,
        'author': str,
        'email': str,
        'license': str,
        'filetype': str,
        'application': str,
        'preprocessing': dict,
        'type': str,
        'labelformat': str}

    config = inifile.decode(comment, flat=True, structure=structure)

    if 'name' in config:
        name = config['name']
    elif isinstance(file, str):
        name = Path(file).name
    elif isinstance(file, Path):
        name = file.name
    else:
        name = 'dataset'
    config['name'] = name

    if 'type' not in config:
        config['type'] = 'base.Dataset'

    # Add column and row filters
    config['colfilter'] = {'*': ['*:*']}
    config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}

    data = csvfile.CSVFile(
        file=file, delim=delim, labels=labels, usecols=usecols,
        namecol=namecol).select()

    config['table'] = {name: config.copy()}
    config['table'][name]['fraction'] = 1.0
    config['columns'] = tuple()
    config['colmapping'] = {}
    config['table'][name]['columns'] = []
    for column in data.dtype.names:
        if column == 'label': continue
        config['columns'] += (('', column),)
        config['colmapping'][column] = column
        config['table'][name]['columns'].append(column)

    # get data table from csv data
    tables = {name: data}

    return {'config': config, 'tables': tables}


#
# DB-API 2.0 Cursor Class
#

class Cursor(dbapi2.Cursor):
    pass
