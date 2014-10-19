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

def _encode_config(dataset, **kwargs):

    # include meta information of dataset
    csv_comment = 'name: %s\n' % (dataset.get('name'))
    dataset_branch = dataset.get('branch')
    if dataset_branch:
        csv_comment += 'branch: %s\n' % (dataset_branch)
    dataset_version = dataset.get('version')
    if dataset_version:
        csv_comment += 'version: %s\n' % (dataset_version)
    dataset_about = dataset.get('about')
    if dataset_about:
        csv_comment += 'about: %s\n' % (dataset_about)
    dataset_author = dataset.get('author')
    if dataset_author:
        csv_comment += 'author: %s\n' % (dataset_author)
    dataset_author_email = dataset.get('email')
    if dataset_author_email:
        csv_comment += 'email: %s\n' % (dataset_author_email)
    dataset_license = dataset.get('license')
    if dataset_license:
        csv_comment += 'license: %s\n' % (dataset_license)
    csv_comment += 'type: %s\n' % (dataset.get('type'))

    # include file information
    csv_comment += 'application: nemoa %s\n' % (nemoa.version())
    csv_comment += 'filetype: text/csv\n'
    csv_type = None
    if 'csvtype' in kwargs and isinstance(kwargs['csvtype'], str):
        csv_type = kwargs['csvtype']
    else:
        src_config = dataset.get('config', 'source')
        if 'csvtype' in src_config:
            csv_type = src_config['csvtype']
    if not isinstance(csv_type, str):
        csv_type = 'default'
    csv_comment += 'csvtype: %s\n' % (csv_type)

    # include preprocessing in csv comment section
    prepro_list = []
    for key, val in dataset.get('config', 'preprocessing').items():
        prepro_list.append('%s = "%s"' % (key, val))
    prepro_str = 'preprocessing: ' + ', '.join(prepro_list)
    csv_comment += prepro_str + '\n'

    return csv_comment.strip('\n')

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
        header = _encode_config(dataset, **self.settings)
        delimiter = self.settings['delimiter']
        cols, data = dataset.get('data', output = ('cols', 'recarray'))
        return nemoa.common.csv_save_data(path, data, header = header,
            delimiter = delimiter, labels = [''] + cols)

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    settings = {
        'delimiter': '\t',
        'csvtype': None }
