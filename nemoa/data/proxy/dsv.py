# -*- coding: utf-8 -*-
"""Table Proxy for DSV-formatted flat file databases."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import attrib
from nemoa.file import dsv #, inifile
from nemoa.data import proxy
from nemoa.types import FileRef, Any

#
# Classes
#

class DSVTable(proxy.Table):
    """DSV-Table Proxy."""

    _file: property = attrib.Temporary(classinfo=dsv.DSVFile)

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Initialize DSV-Table Proxy.

        Args:
            file:
            *args: Additional arguments, that are passed to
                :class:`~nemoa.file.dsv.DSVFile`.
            **kwds: Additional keyword arguments, that are passed to DSVFile.

        """
        self._file = dsv.DSVFile(file, *args, **kwds)

        # Create header
        self._create_header(self._file.fields)

        # Initialize table proxy
        super().__init__()

    def pull(self) -> None:
        """Pull all rows from DSV-File."""
        rows = self._file.read()
        self.append_rows(rows)

    def push(self) -> None:
        """Push all rows to DSV-File."""
        rows = self.select()
        self._file.write(rows)

    #
    # def __init__(
    #         self, file: FileOrPathLike, delim: OptStr = None,
    #         labels: OptStrList = None, usecols: OptIntTuple = None,
    #         namecol: OptInt = None) -> None:
    #     """ """
    #     # Get configuration from CSV header
    #     comment = dsv.DSVFile(file).comment
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
    #     config = inifile.decode(comment, flat=True, structure=structure)
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
    #     data = dsv.DSVFile(
    #         file=file, delim=delim, labels=labels, usecols=usecols,
    #         namecol=namecol).select()
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
