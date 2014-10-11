# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx

class Gml:
    """Import network from GML file."""

    def __init__(self, workspace = None):
        pass

    def load(self, path):
        graph = networkx.read_gml(path, relabel = True)
        graph = self._graph_decode(graph)
        graph_dict = self._graph_to_dict(graph)
        graph_dict = nemoa.common.dict_convert_unicode_keys(
            graph_dict)
        return {
            'config': graph_dict['graph']['params'],
            'graph': graph_dict }

    @staticmethod
    def _graph_decode(graph):

        # no decoding
        if not 'coding' in graph.graph \
            or not graph.graph['coding'] \
            or graph.graph['coding'].lower() == 'none':
            return graph

        # base64 decoding
        elif graph.graph['coding'] == 'base64':
            graph.graph['params'] = \
                nemoa.common.dict_decode_base64(
                graph.graph['params'])

            for node in graph.nodes():
                graph.node[node]['params'] = \
                    nemoa.common.dict_decode_base64(
                    graph.node[node]['params'])

            for src, tgt in graph.edges():
                graph.edge[src][tgt]['params'] = \
                    nemoa.common.dict_decode_base64(
                    graph.edge[src][tgt]['params'])

            graph.graph['coding'] == 'none'
            return graph

        else:
            nemoa.log('error', """could not decode graph parameters:
                unsupported coding '%s'.""" % (coding))

        return {}

    @staticmethod
    def _graph_to_dict(graph):
        return {
            'graph': graph.graph,
            'nodes': graph.nodes(data = True),
            'edges': networkx.to_dict_of_dicts(graph) }
