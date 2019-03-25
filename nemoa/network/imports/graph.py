# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import networkx
from flib.base import mapping


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
    from flib.base import env

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
    from flib.base import binary

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
