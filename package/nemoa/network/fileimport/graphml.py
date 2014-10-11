# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx

class Graphml:
    """Import network from GraphML file."""

    def __init__(self, workspace = None):
        pass

    def load(self, path):
        print 'hi'
        graph = networkx.read_graphml(path)
        print graph
        return self._graph_to_dict(graph)

    def _graph_to_dict(self, graph):
        return {
            'config': graph.graph,
            'graph': {
                'graph': graph.graph,
                'nodes': graph.nodes(data = True),
                'edges': networkx.to_dict_of_dicts(graph) }}
