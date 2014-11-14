# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

def filetypes():
    """Get supported archive filetypes for dataset import."""

    return {
        'npz': 'Numpy Zipped Archive' }

def load(path, **kwargs):
    """Import dataset from archive file."""

    return Npz(**kwargs).load(path)

class Npz:
    """Import dataset from numpy zipped archive."""

    settings = {}

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        copy = numpy.load(path)
        return {
            'config': copy['config'].item(),
            'tables': copy['tables'].item() }
