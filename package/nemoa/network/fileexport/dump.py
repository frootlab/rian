# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os

def filetypes():
    """Get supported dump filetypes for network export."""
    return {
        'npz': 'Numpy Zipped Archive' }

def save(network, path, **kwargs):
    """Export network to dump file."""
    copy = network.get('copy')
    return Npz(**kwargs).save(copy, path)

class Npz:
    """Export network to numpy zip compressed file."""

    settings = {
        'compress': True }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, copy, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        if self.settings['compress']:
            numpy.savez_compressed(path, **copy)
        else:
            numpy.savez(path, **copy)

        return path
