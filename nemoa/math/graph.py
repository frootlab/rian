# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Functions for NetworkX Graphs."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
from flab.base.types import Any, OptBool, OptStr, OptTuple, FloatPair

DiGraph = nx.classes.digraph.DiGraph

def get_layers(G: DiGraph) -> list:
    """Return list of layers in DiGraph."""
    # create list of lists
    # sorted by the node attributes "layer_id" and "layer_sub_id"
    sort = {}
    for node, data in G.nodes(data=True):
        l = (data.get('layer'), data.get('layer_id'))
        n = (node, data.get('layer_sub_id'))
        if l not in sort:
            sort[l] = [n]
        else:
            sort[l].append(n)

    layers = []
    for (layer, lid) in sorted(list(sort.keys()), key=lambda x: x[1]):
        layers.append([node for (node, nid) in \
            sorted(sort.get((layer, lid), []), key=lambda x: x[1])])

    return layers

def get_groups(
        G: DiGraph, attribute: OptStr = None,
        param: OptStr = None) -> dict:
    """Return dictinary with grouped lists of nodes."""
    if attribute is None and param is None:
        attribute = 'group'

    groups: dict = {'': []}

    for node, data in G.nodes(data=True):
        if not isinstance(data, dict):
            groups[''].append(node)
            continue
        elif attribute is not None and not attribute in data:
            groups[''].append(node)
            continue
        elif param is not None \
            and not ('params' in data and param in data['params']):
            groups[''].append(node)
            continue
        if attribute is not None and param is None:
            group = data[attribute]
        elif attribute is None and param is not None:
            group = data['params'][param]
        else:
            group = (data[attribute], data['params'][param])
        if group not in groups:
            groups[group] = [node]
            continue
        groups[group].append(node)

    return groups

def is_directed(G: DiGraph) -> OptBool:
    """Determine if layered graph is directed.

    Args:
        G: networkx graph instance

    Returns:

    """
    if is_layered(G):
        decl = G.graph.get('directed')
        if isinstance(decl, bool):
            return decl
        layers = get_layers(G)
        if len(layers) == 1:
            return False
        i = G.node.get(layers[0][0], {}).get('visible', False)
        o = G.node.get(layers[-1][0], {}).get('visible', False)
        if i and o:
            return True
        return False

    return None

def is_layered(G: DiGraph) -> bool:
    """Test if graph nodes contain layer attributes.

    Args:
        G: networkx graph instance

    Returns:
        Bool which is True if the graph nodes contain layer attributes.

    Todo:
        Test by edge structure and not by node attributes

    """
    require = ['layer', 'layer_id', 'layer_sub_id']
    for node, data in G.nodes(data=True):
        for key in require:
            if key not in data:
                return False

    return True
