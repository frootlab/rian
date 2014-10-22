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

        config = nemoa.common.ini_loads(header, nosection = True,
            structure = structure)

        if 'name' in config:
            name = config['name']
        else:
            name = nemoa.common.get_file_basename(path)
            config['name'] = name
        if not 'type' in config:
            config['type'] = 'base.Dataset'

        config['table'] = {name: config.copy()}
        config['table'][name]['fraction'] = 1.0

        # add column androw filters
        config['colfilter'] = {'*': ['*:*']}
        config['rowfilter'] = {'*': ['*:*'], name: [name + ':*']}

        data = nemoa.common.csv_get_data(path)

        config['columns'] = tuple()
        for col in data.dtype.names:
            if col == 'label': continue
            config['columns'] += (('', col),)

        # get source data from csv data
        source = {
            name: {
                'array': data,
                'fraction': 1.0}}

        return {'config': config, 'source': source}

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    settings = {
        'delimiter': '\t',
        'csvtype': None }
