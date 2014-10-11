# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

class Gml:
    """Export network to gml file."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def save(self, network, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        graph = network.get('graph', type = 'graph', encode = 'base64')
        networkx.write_gml(graph, path)
        return True
