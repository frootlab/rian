# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for dataset import."""
    return {
        'csv': 'Comma Separated Values',
        'tsv': 'Tab Separated Values',
        'tab': 'Tab Separated Values'}

def load(path, **kwds):
    """Import dataset from text file."""

    from nemoa.base import npath

    # get extract filetype from file extension
    filetype = npath.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    if filetype == 'csv': return Csv(**kwds).load(path)
    if filetype in ['tsv', 'tab']: return Tsv(**kwds).load(path)

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

        from nemoa.fileio import csvfile, inifile
        from nemoa.base import npath

        # Get configuration from CSV header
        header = csvfile.get_header(path)

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

        config = inifile.loads(header, flat=True, structure=structure)

        if 'name' in config: name = config['name']
        else:
            name = npath.basename(path)
            config['name'] = name
        if 'type' not in config: config['type'] = 'base.Dataset'

        # add column and row filters
        config['colfilter'] = {'*': ['*:*']}
        config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}

        data = csvfile.load(path)

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
        tables = { name: data }

        return { 'config': config, 'tables': tables }

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    default = { 'delim': '\t' }
