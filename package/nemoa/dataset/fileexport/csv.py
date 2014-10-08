# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

class Csv:
    """Export dataset to csv file."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def save(self, dataset, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        cols, data = dataset.data(output = ('cols', 'recarray'))
        ret_val = nemoa.common.csv_save_data(path, data,
            cols = [''] + cols)

        return ret_val
