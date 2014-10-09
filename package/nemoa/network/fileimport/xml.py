# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx

class Xml:
    """Import network from GraphML file."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def load(self, path):
        graph = networkx.read_graphml(path, relabel = True)
        return self._graph_to_dict(graph)

    def _graph_to_dict(self, graph):
        return {
            'config': graph.graph,
            'graph': {
                'graph': graph.graph,
                'nodes': graph.nodes(data = True),
                'edges': networkx.to_dict_of_dicts(graph) }}
