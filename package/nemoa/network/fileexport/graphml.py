# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

class Graphml:
    """Export network to GraphML file."""

    def __init__(self, workspace = None):
        pass

    def save(self, network, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        graph = network.get('graph', type = 'graph', encode = True)
        networkx.write_graphml(graph, path)
        return True
