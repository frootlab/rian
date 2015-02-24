# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for dataset import."""
    return {
        'csv': 'Comma Separated Values',
        'tsv': 'Tab Separated Values',
        'tab': 'Tab Separated Values'}

def load(path, **kwargs):
    """Import dataset from text file."""

    # get extract filetype from file extension
    filetype = nemoa.common.ospath.fileext(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import dataset:
            filetype '%s' is not supported.""" % filetype)

    if filetype == 'csv':
        return Csv(**kwargs).load(path)
    if filetype in ['tsv', 'tab']:
        return Tsv(**kwargs).load(path)

    return False

class Csv:
    """Import dataset from Comma Separated Values."""

    settings = None
    default = { 'delimiter': ',' }

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def load(self, path):
        """Get dataset configuration and dataset tables.

        Args:
            path (string): csv file containing dataset configuration and
                dataset table.

        """

        # get config from csv header
        header = nemoa.common.csvfile.getheader(path)

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
            'labelformat': 'str' }

        config = nemoa.common.inifile.loads(header, nosection = True,
            structure = structure)

        if 'name' in config:
            name = config['name']
        else:
            name = nemoa.common.ospath.basename(path)
            config['name'] = name
        if not 'type' in config:
            config['type'] = 'base.Dataset'

        # add column and row filters
        config['colfilter'] = {'*': ['*:*']}
        config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}

        data = nemoa.common.csvfile.load(path)

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

    default = { 'delimiter': '\t' }
