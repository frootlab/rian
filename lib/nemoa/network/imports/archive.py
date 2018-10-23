# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

def filetypes():
    """Get supported archive filetypes for network import."""
    return {
        'npz': 'Numpy Zipped Archive' }

def load(path, **kwds):
    """Import network from archive file."""
    return Npz(**kwds),load(path)

class Npz:
    """Import network from numpy zipped archive."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        copy = numpy.load(path)
        return {
            'config': copy['config'].item(),
            'graph': copy['graph'].item() }
