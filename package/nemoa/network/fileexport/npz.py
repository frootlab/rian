# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os

class Npz:
    """Export network to numpy zip compressed file."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def save(self, network, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        numpy.savez(path, **network.get('copy'))

        return True
