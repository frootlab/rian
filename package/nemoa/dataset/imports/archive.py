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

    settings = None
    default = {}

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def load(self, path):
        copy = numpy.load(path)
        return {
            'config': copy['config'].item(),
            'tables': copy['tables'].item() }
