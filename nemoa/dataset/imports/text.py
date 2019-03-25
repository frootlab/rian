# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

from flib.base import env
from flib.io import csv, ini
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
