# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import env
from flab.io import csv, ini
from nemoa.base import array

def filetypes():
    """Get supported text filetypes for dataset import."""
    return {
        'csv': 'Comma Separated Values',
        'tsv': 'Tab Separated Values',
        'tab': 'Tab Separated Values'}

def load(path, **kwds):
    """Import dataset from text file."""

    # get extract filetype from file extension
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    if filetype == 'csv':
        return Csv(**kwds).load(path)
    if filetype in ['tsv', 'tab']:
        return Tsv(**kwds).load(path)

    return False

class Csv:
    """Import dataset from Comma Separated Values."""

    settings = None
    default = {'delim': ','}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """Get dataset configuration and dataset tables.

        Args:
            path (string): csv file containing dataset configuration and
                dataset table.

        """

        # Get instance of CSV-file
        file = csv.File(path)

        # Get configuration from CSV comment lines
        comment = file.comment

        scheme = {
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

        config = ini.decode(comment, flat=True, scheme=scheme)

        if 'name' in config:
            name = config['name']
        else:
            name = env.basename(path)
            config['name'] = name
        if 'type' not in config:
            config['type'] = 'base.Dataset'

        # Add column and row filters
        config['colfilter'] = {'*': ['*:*']}
        config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}

        # Load data
        names = list(file.header)
        names[0] = 'label'
        data = array.from_tuples(file.read(), names=tuple(names))

        config['table'] = {name: config.copy()}
        config['table'][name]['fraction'] = 1.0
        config['columns'] = tuple()
        config['colmapping'] = {}
        config['table'][name]['columns'] = []
        for column in data.dtype.names:
            if column == 'label':
                continue
            config['columns'] += (('', column),)
            config['colmapping'][column] = column
            config['table'][name]['columns'].append(column)

        # Get data table from CSV data
        tables = {name: data}

        return {'config': config, 'tables': tables}

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    default = {'delim': '\t'}
