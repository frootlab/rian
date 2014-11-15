# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for dataset export."""
    return {
        'csv': 'Comma Separated Values',
        'tsv': 'Tab Separated Values',
        'tab': 'Tab Separated Values'}

def save(dataset, path, filetype, **kwargs):
    """Export dataset to archive file."""

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not export dataset:
            filetype '%s' is not supported.""" % (filetype))

    # create path if not available
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    if filetype == 'csv':
        return Csv(**kwargs).save(dataset, path)
    if filetype in ['tsv', 'tab']:
        return Tsv(**kwargs).save(dataset, path)

    return False

class Csv:
    """Export dataset to Comma Separated Values."""

    settings = {
        'delimiter': ',',
        'csvtype': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, dataset, path):

        # create the configuration which is included in the CSV file
        # as header as a subset of the dataset configuration
        keys = ['name', 'branch', 'version', 'about', 'author', 'email',
            'license', 'filetype', 'application', 'preprocessing',
            'type', 'labelformat']
        config = {}
        for key, val in dataset.get('config').iteritems():
            if key in keys: config[key] = val

        # update configuration to include current appliucation settings
        #config['application'] = 'nemoa ' + nemoa.version()

        # prepare CSV parameters and write CSV file
        header = nemoa.common.ini_dumps(config).strip('\n')
        delimiter = self.settings['delimiter']
        cols, data = dataset.get('data', output = ('cols', 'recarray'))
        #print cols
        #print data.dtype.names
        #quit


        return nemoa.common.csv_save_data(path, data, header = header,
            delimiter = delimiter, labels = [''] + cols)

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    settings = {
        'delimiter': '\t',
        'csvtype': None }
