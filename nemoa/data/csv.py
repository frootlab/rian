# -*- coding: utf-8 -*-
"""Table Proxy for textfiles containing delimiter-separated values."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import attrib
from nemoa.data import Proxy
from nemoa.file import csv
from nemoa.types import FileRef, Any

#
# Classes
#

class Table(Proxy):
    """CSV-Table Proxy."""

    _file: property = attrib.Temporary(classinfo=csv.File)

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Initialize CSV-Table Proxy.

        Args:
            file:
            *args: Additional arguments, that are passed to
                :class:`csv.File <nemoa.file.csv.File>`.
            **kwds: Additional keyword arguments, that are passed to csv.File.

        """
        # Initialize table proxy
        super().__init__()

        # Open CSV-formatted file
        self._file = csv.File(file, *args, **kwds)

        # Create header
        self._create_header(self._file.fields)

        # Run post init hook
        self._post_init()

    def pull(self) -> None:
        """Pull all rows from CSV-File."""
        rows = self._file.read()
        self.append_rows(rows)

    def push(self) -> None:
        """Push all rows to CSV-File."""
        rows = self.select()
        self._file.write(rows)

    #
    # def __init__(
    #         self, file: FileOrPathLike, delim: OptStr = None,
    #         labels: OptStrList = None, usecols: OptIntTuple = None,
    #         namecol: OptInt = None) -> None:
    #     """ """
    #     # Get configuration from CSV header
    #     comment = csv.File(file).comment
    #
    #     structure = {
    #         'name': str,
    #         'branch': str,
    #         'version': int,
    #         'about': str,
    #         'author': str,
    #         'email': str,
    #         'license': str,
    #         'filetype': str,
    #         'application': str,
    #         'preprocessing': dict,
    #         'type': str,
    #         'labelformat': str}
    #
    #     config = ini.decode(comment, flat=True, structure=structure)
    #
    #     if 'name' in config:
    #         name = config['name']
    #     elif isinstance(file, str):
    #         name = Path(file).name
    #     elif isinstance(file, Path):
    #         name = file.name
    #     else:
    #         name = 'dataset'
    #     config['name'] = name
    #
    #     if 'type' not in config:
    #         config['type'] = 'base.Dataset'
    #
    #     # Add column and row filters
    #     config['colfilter'] = {'*': ['*:*']}
    #     config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}
    #
    #     data = csv.load(
    #         file=file, delim=delim, labels=labels, usecols=usecols,
    #         namecol=namecol).load_old()
    #
    #     config['table'] = {name: config.copy()}
    #     config['table'][name]['fraction'] = 1.0
    #     config['columns'] = tuple()
    #     config['colmapping'] = {}
    #     config['table'][name]['columns'] = []
    #     for column in data.dtype.names:
    #         if column == 'label': continue
    #         config['columns'] += (('', column),)
    #         config['colmapping'][column] = column
    #         config['table'][name]['columns'].append(column)
    #
    #     # get data table from csv data
    #     tables = {name: data}
    #
    #     self.config = config
    #     self.tables = tables
