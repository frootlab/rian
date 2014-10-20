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
    filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import dataset:
            filetype '%s' is not supported.""" % (filetype))

    if filetype == 'csv':
        return Csv(**kwargs).load(path)
    if filetype in ['tsv', 'tab']:
        return Tsv(**kwargs).load(path)

    return False

def _decode_config(header, **kwargs):

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

    return nemoa.common.ini_loads(header, nosection = True,
        structure = structure)

class Csv:
    """Import dataset from Comma Separated Values."""

    settings = {
        'delimiter': ',',
        'csvtype': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        """Get dataset configuration and source data.

        Args:
            path (string): csv file containing dataset configuration and
                source data.

        """

        # get config from csv header
        header = nemoa.common.csv_get_header(path)
        config = _decode_config(header)
        copy = config.copy()
        name = config['name']
        config['table'] = {name: copy}
        config['table'][name]['fraction'] = 1.0
        config['col_filter'] = {'*': ['*:*'], name: [name + ':*']}
        config['row_filter'] = {'*': ['*:*'], name: [name + ':*']}
        config['columns'] = tuple()
        for col in nemoa.common.csv_get_labels(path):
            config['columns'] += ((name, col),)

        # get source data from csv data
        source = {
            name: {
                'array': nemoa.common.csv_get_data(path),
                'fraction': 1.0}}

        return {'config': config, 'source': source}

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    settings = {
        'delimiter': '\t',
        'csvtype': None }
