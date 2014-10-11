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

        # get networkx graph from network
        graph = network.get('graph', type = 'graph')

        # encode graph parameter dictionaries to base64
        graph = self._graph_encode(graph, coding = 'base64')

        # write networkx graph to gml file
        networkx.write_graphml(graph, path)

        return True

    @staticmethod
    def _graph_encode(graph, coding = None):
        """Encode graph parameters."""

        # no encoding
        if not isinstance(coding, str) or coding.lower() == 'none':
            return self._graph.copy()

        # base64 encoding
        elif coding.lower() == 'base64':

            # encode graph 'params' dictionary to base64
            graph.graph['params'] \
                = nemoa.common.dict_encode_base64(
                graph.graph['params'])

            # encode nodes 'params' dictionaries to base64
            for node in graph.nodes():
                graph.node[node]['params'] \
                    = nemoa.common.dict_encode_base64(
                    graph.node[node]['params'])

            # encode edges 'params' dictionaries to base64
            for edge in graph.edges():
                in_node, out_node = edge
                graph.edge[in_node][out_node]['params'] \
                    = nemoa.common.dict_encode_base64(
                    graph.edge[in_node][out_node]['params'])

            # set flag for graph parameter coding
            graph.graph['coding'] = 'base64'
            return graph

        return nemoa.log('error', """could not encode graph parameters:
            unsupported coding '%s'.""" % (coding))
