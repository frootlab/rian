# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import networkx
from flab.base import mapping


def filetypes():
    """Get supported graph description filetypes for network import."""

    d = {
        'gml': 'Graph Modelling Language',
        'graphml': 'Graph Markup Language',
        'xml': 'Graph Markup Language',
        'dot': 'GraphViz DOT'
    }

    return d

def load(path, **kwds):
    """Import network from graph description file."""
    from flab.base import env

    # extract filetype from path
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    if filetype == 'gml': return Gml(**kwds).load(path)
    if filetype in ['graphml', 'xml']: return Graphml(**kwds).load(path)
    if filetype == 'dot': return Dot(**kwds).load(path)

    return False

def _graph_decode(G):
    """ """
    from flab.base import binary

    # no encoding
    if not G.graph.get('coding', None) or G.graph['coding'].lower() == 'none':
        return G

    # base64 encoding
    if G.graph['coding'] == 'base64':
        G.graph['params'] = binary.unpack(G.graph['params'], encoding='base64')

        for node in G.nodes():
            G.node[node]['params'] = binary.unpack(
                G.node[node]['params'], encoding='base64')

        for edge in G.edges():
            G.edges[edge]['params'] = binary.unpack(
                G.edges[edge]['params'], encoding='base64')

        G.graph['coding'] == 'none'

        return graph

    raise ValueError(f"unsupported coding '{coding}'")

def _graph_to_dict(G):
    """ """

    d = {
        'graph': G.graph,
        'nodes': G.nodes(data = True),
        'edges': networkx.to_dict_of_dicts(G)
    }

    return d

class Graphml:
    """Import network from GraphML file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        """ """
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """ """

        G = networkx.read_graphml(path)
        d = mapping.strkeys(_graph_to_dict(_graph_decode(G)))

        return {'config': d['graph']['params'], 'graph': d }

class Gml:
    """Import network from GML file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        """ """
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """ """

        G = networkx.read_gml(path, relabel = True)
        d = mapping.strkeys(_graph_to_dict(_graph_decode(G)))

        return {'config': d['graph']['params'], 'graph': d }
