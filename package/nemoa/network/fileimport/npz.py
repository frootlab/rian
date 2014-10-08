# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

class Npz:
    """Import network from numpy zip compressed file."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def load(self, path):
        copy = numpy.load(path)
        return {
            'config': copy['config'].item(),
            'graph': copy['graph'].item() }
