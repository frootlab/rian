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
    """Export dataset to CSV file."""

    settings = {
        'delimiter': ',',
        'comment': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, dataset, path):

        # include type in comment
        self.settings['comment'] = 'type: %s\n' % (
            dataset.get('config', 'type'))

        # include preprocessing in comment
        prepro_list = []
        for key, val in dataset.get('config', 'preprocessing').items():
            prepro_list.append('%s = %s' % (key, val))
        prepro_str = 'preprocessing: ' + ', '.join(prepro_list)
        self.settings['comment'] += prepro_str

        cols, data = dataset.get('data', output = ('cols', 'recarray'))
        nemoa.common.csv_save_data(path, data, cols = [''] + cols,
            **self.settings)
        return path

class Tsv(Csv):
    """Export dataset to TSV file."""

    settings = {
        'delimiter': '\t',
        'comment': None }
