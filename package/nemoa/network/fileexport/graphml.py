# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def save(network, path, **kwargs):

    return Graphml(**kwargs).save(network, path)

class Graphml:
    """Export network to GraphML file."""

    settings = {
        'coding': 'base64' }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, network, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # get networkx graph from network
        graph = network.get('graph', type = 'graph')

        # encode graph parameter dictionaries
        graph = nemoa.network.fileexport.encode(graph,
            coding = self.settings['coding'])

        # write networkx graph to gml file
        networkx.write_graphml(graph, path)

        return path
