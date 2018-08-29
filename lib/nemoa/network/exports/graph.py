# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def filetypes():
    """Get supported graph filetypes for network export."""
    return {
        'gml': 'Graph Modelling Language',
        'graphml': 'Graph Markup Language',
        'xml': 'Graph Markup Language',
        'dot': 'GraphViz DOT' }

def save(network, path, filetype, **kwargs):
    """Export network to graph description file."""

    # test if filetype is supported
    if filetype not in filetypes():
        return nemoa.log('error', f"filetype '{filetype}' is not supported")

    # create path if not available
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # get networkx graph from network
    graph = network.get('graph', type = 'graph')

    if filetype == 'gml':
        return Gml(**kwargs).save(graph, path)
    if filetype in ['graphml', 'xml']:
        return Graphml(**kwargs).save(graph, path)
    if filetype == 'dot':
        return Dot(**kwargs).save(graph, path)

    return False

def _graph_encode(graph, coding = None):
    """Encode graph parameters."""

    from nemoa.common import iozip

    # no encoding
    if not isinstance(coding, str) or coding.lower() == 'none':
        return self._graph.copy()

    # base64 encoding
    elif coding.lower() == 'base64':

        # encode graph 'params' dictionary to base64
        graph.graph['params'] = iozip.dumps(
            graph.graph['params'], encode = 'base64')

        # encode nodes 'params' dictionaries to base64
        for node in graph.nodes():
            graph.node[node]['params'] = iozip.dumps(
                graph.node[node]['params'], encode = 'base64')

        # encode edges 'params' dictionaries to base64
        for edge in graph.edges():
            graph.edges[edge]['params'] = iozip.dumps(
                graph.edges[edge]['params'], encode = 'base64')

        # set flag for graph parameter coding
        graph.graph['coding'] = 'base64'
        return graph

    return nemoa.log('error', """could not encode graph parameters:
        unsupported coding '%s'.""" % coding)

class Gml:
    """Export network to GML file."""

    settings = None
    default = { 'coding': 'base64' }

    def __init__(self, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = _graph_encode(graph, coding = self.settings['coding'])

        # write networkx graph to gml file
        networkx.write_gml(graph, path)

        return path

class Graphml:
    """Export network to GraphML file."""

    settings = None
    default = { 'coding': 'base64' }

    def __init__(self, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = _graph_encode(graph, coding = self.settings['coding'])

        # write networkx graph to gml file
        networkx.write_graphml(graph, path)

        return path

class Dot:
    """Export network to GraphViz Dot file."""

    settings = None
    default = { 'coding': 'base64' }

    def __init__(self, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = _graph_encode(graph, coding = self.settings['coding'])

        # check library support for dot files
        try:
            module = networkx.drawing.write_dot.__module__
        except:
            return nemoa.log('error', """could not export graph:
                filetype 'dot' needs libraries 'pygraphviz' and
                'pydot'.""")

        # write networkx graph to graphviz dot file
        networkx.write_dot(graph, path)

        return path
