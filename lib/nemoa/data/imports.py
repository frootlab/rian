# -*- coding: utf-8 -*-
"""Dataset imports."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path
from nemoa.base import npath
from nemoa.fileio import csvfile, inifile
from nemoa.types import FileOrPathLike, OptStr, OptIntTuple, OptStrList, OptInt

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
