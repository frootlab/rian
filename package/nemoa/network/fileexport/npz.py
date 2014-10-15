# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os

def save(network, path, **kwargs):

    return Npz(**kwargs).save(network, path)

class Npz:
    """Export network to numpy zip compressed file."""

    settings = {
        'compress': True }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, network, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        if self.settings['compress']:
            numpy.savez_compressed(path, **network.get('copy'))
        else:
            numpy.savez(path, **network.get('copy'))

        return path
