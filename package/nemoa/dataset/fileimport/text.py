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

def _decode_config(comment, **kwargs):

    config = {}

    return config

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

        # get csv comment

        return

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    settings = {
        'delimiter': '\t',
        'csvtype': None }
