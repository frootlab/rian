# -*- coding: utf-8 -*-
"""DB-API 2.0 interface for CSV-file Database."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path
from nemoa.types import FileOrPathLike, OptStr, OptIntTuple, OptStrList, OptInt
from nemoa.base import npath
from nemoa.base.container import BaseContainer
from nemoa.base.file import csvfile, inifile
from nemoa.core.db import dbapi2
from nemoa.core.db.dbapi2 import Error, Warning, InterfaceError, DatabaseError
from nemoa.core.db.dbapi2 import InternalError, OperationalError, DataError
from nemoa.core.db.dbapi2 import ProgrammingError, IntegrityError
from nemoa.core.db.dbapi2 import NotSupportedError

#
# Module globals
#

apilevel = '2.0'
threadsafety = 0
paramstyle = 'pyformat'

#
# DB-API 2.0 Connection Class
#

class Connection(dbapi2.Connection):
    pass

def load_csv(
        file: FileOrPathLike, delim: OptStr = None,
        labels: OptStrList = None, usecols: OptIntTuple = None,
        rowlabelcol: OptInt = None) -> dict:
    """ """
    # Get configuration from CSV header
    header = csvfile.get_header(file)

    structure = {
        'name': 'str',
        'branch': 'str',
        'version': 'int',
        'about': 'str',
        'author': 'str',
        'email': 'str',
        'license': 'str',
        'filetype': 'str',
        'application': 'str',
        'preprocessing': 'dict',
        'type': 'str',
        'labelformat': 'str'}

    config = inifile.decode(header, flat=True, structure=structure)

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

    data = csvfile.load(
        file=file, delim=delim, labels=labels, usecols=usecols,
        rowlabelcol=rowlabelcol)

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
