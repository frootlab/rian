# -*- coding: utf-8 -*-
"""Data mappers."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path
from nemoa.types import FileOrPathLike, OptStr, OptIntTuple, OptStrList, OptInt
from nemoa.base.file import csvfile, inifile
from nemoa.data.table import Table

class CSVTable(Table):
    def __init__(
            self, file: FileOrPathLike, delim: OptStr = None,
            labels: OptStrList = None, usecols: OptIntTuple = None,
            namecol: OptInt = None) -> None:
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

        self.config = config
        self.tables = tables
