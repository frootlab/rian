# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def filetypes():
    """Get supported graph description filetypes for network import."""

    d = {
        'gml': 'Graph Modelling Language',
        'graphml': 'Graph Markup Language',
        'xml': 'Graph Markup Language',
        'dot': 'GraphViz DOT'
    }

    return d

def load(path, **kwargs):
    """Import network from graph description file."""

    # extract filetype from path
    filetype = nemoa.common.ospath.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    if filetype == 'gml': return Gml(**kwargs).load(path)
    if filetype in ['graphml', 'xml']: return Graphml(**kwargs).load(path)
    if filetype == 'dot': return Dot(**kwargs).load(path)

    return False

def _graph_decode(G):
    """ """

    from nemoa.common import iozip

    # no decoding
    if not G.graph.get('coding', None) or G.graph['coding'].lower() == 'none':
        return G

    # base64 decoding
    elif G.graph['coding'] == 'base64':
        G.graph['params'] = iozip.loads(G.graph['params'], encode = 'base64')

        for node in G.nodes():
            G.node[node]['params'] = iozip.loads(
                G.node[node]['params'], encode = 'base64')

        for edge in G.edges():
            G.edges[edge]['params'] = iozip.loads(
                G.edges[edge]['params'], encode = 'base64')

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

    def __init__(self, **kwargs):
        """ """

        from nemoa.common.dict import merge

        self.settings = merge(kwargs, self.default)

    def load(self, path):
        """ """

        from nemoa.common.dict import strkeys

        G = networkx.read_graphml(path)
        d = strkeys(_graph_to_dict(_graph_decode(G)))

        return {'config': d['graph']['params'], 'graph': d }

class Gml:
    """Import network from GML file."""

    settings = None
    default = {}

    def __init__(self, **kwargs):
        """ """

        from nemoa.common.dict import merge

        self.settings = merge(kwargs, self.default)

    def load(self, path):
        """ """

        from nemoa.common.dict import strkeys

        G = networkx.read_gml(path, relabel = True)
        d = strkeys(_graph_to_dict(_graph_decode(G)))

        return {'config': d['graph']['params'], 'graph': d }
