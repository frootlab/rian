# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import networkx
except ImportError: raise ImportError(
    "nemoa.common.graph requires networkx: "
    "https://networkx.github.io")

try: import numpy
except ImportError: raise ImportError(
    "nemoa.common.graph requires numpy: "
    "https://scipy.org")

from networkx.classes.digraph import DiGraph
from typing import Optional

def get_layout(G: DiGraph, layout: str = 'spring',
    size: Optional[tuple] = None, padding: Optional[tuple] = None,
    rotate: float = 0.0, **kwargs) -> dict:
    """Calculate positions of nodes, depending on graph layout.

    Args:
        G: networkx graph instance

    Kwargs:
        layout (string, optional): graph layout name
            default is "spring"
        size (tuple, optional): size in pixel (x, y)
            default is None, which means no rescale
        padding (tuple, optional): padding in percentage (up, down, left, right)
            default is None, which means no padding
        rotate (float, optional): rotation angle in degrees
            default is 0.0, which means no rotation

    Return:
        dictionary containing node positions for graph layout

    """

    # 2do: allow layouts from pygraphviz_layout
    # 2do: determine layout by graph type if layout is None

    if layout == 'spring':
        pos = networkx.spring_layout(G, **kwargs)
    elif layout == 'layer':
        pos = get_layer_layout(G, **kwargs)
    elif layout == 'random':
        pos = networkx.random_layout(G, **kwargs)
    elif layout == 'circular':
        pos = networkx.circular_layout(G, **kwargs)
    elif layout == 'shell':
        pos = networkx.shell_layout(G, **kwargs)
    elif layout == 'spectral':
        pos = networkx.spectral_layout(G, **kwargs)
    elif layout == 'fruchterman_reingold':
        pos = networkx.fruchterman_reingold_layout(G, **kwargs)
    else: raise ValueError(
        "could not get graph layout: "
        "layout '%s' is not supported." % layout)

    # rescale node positions to given figure size, padding
    # and rotation angle
    pos = rescale_layout(pos, size = size, padding = padding, rotate = rotate)

    return pos

def get_layers(G: DiGraph) -> list:
    """Return list of layers in DiGraph."""

    # create node stack as list of lists
    # sorted by the node attributes layer_id and layer_sub_id
    sort = {}
    for node, data in G.nodes(data = True):
        l = (data.get('layer'), data.get('layer_id'))
        n = (node, data.get('layer_sub_id'))
        if not l in sort: sort[l] = [n]
        else: sort[l].append(n)

    layers = []
    for (layer, lid) in sorted(list(sort.keys()), key = lambda x: x[1]):
        layers.append([node for (node, nid) in \
            sorted(sort.get((layer, lid), []), key = lambda x: x[1])])

    return layers

def get_layer_layout(G: DiGraph, direction: str = 'right',
    minimize: str = 'weight') -> dict:
    """Calculate node positions for layer layout.

    Args:
        G: networkx graph instance

    Kwargs:
        direction (string, optional):
        minimize (string, optional):

    Return:

    """

    assert is_layered(G), (
        "nemoa.common.graph.get_layer_layout(): "
        "graph is not layered.")

    if len(G) == 0: return {}
    if len(G) == 1: return { G.nodes()[0]: (0.5, 0.5) }

    # get list of node lists, sorted by layer (list of lists)
    stack = get_layers(G)

    # sort node stack to minimize the euclidean distances
    # of connected nodes
    if isinstance(minimize, str):
        edges = {(u, v): data \
            for (u, v, data) in G.edges(data = True)}

        for lid, tgt in enumerate(stack[1:], 1):
            src  = stack[lid - 1]
            slen = len(src)
            tlen = len(tgt)

            # calculate cost matrix for positions by weights
            cost = numpy.zeros((tlen, tlen))
            for sid, u in enumerate(src):
                for tid, v in enumerate(tgt):
                    data = edges.get((u, v))
                    if data == None: data = edges.get((v, u))
                    if not isinstance(data, dict): continue
                    value = data.get(minimize)
                    if not isinstance(value, float): continue
                    weight = numpy.absolute(value)
                    for pid in range(tlen):
                        dist = numpy.absolute(
                            (pid + .5) / (tlen + 1.) \
                            - (sid + .5) / (slen + 1.))
                        cost[pid, tid] += dist * weight

            # choose (node, position) pair with maximum savings
            # thereby penalize large distances by power two
            # repeat until all nodes have positions
            nsel = list(range(tlen)) # node select list
            psel = list(range(tlen)) # position select list
            sort = [None] * tlen
            for i in range(tlen):
                cmax = numpy.amax(cost[psel][:, nsel], axis = 0)
                cmin = numpy.amin(cost[psel][:, nsel], axis = 0)
                diff = cmax ** 2 - cmin ** 2
                nid  = nsel[numpy.argmax(diff)]
                pid  = psel[numpy.argmin(cost[psel][:, nid])]
                sort[pid] = tgt[nid]
                nsel.remove(nid)
                psel.remove(pid)
            stack[lid] = sort

    # calculate node positions in box [0, 1] x [0, 1]
    orientate = lambda p, d: {
        'right': (p[0], p[1]),
        'up': (p[1], p[0]),
        'left': (1. - p[0],  p[1]),
        'down': (p[1], 1. - p[0])}.get(d)
    pos = {}
    for l, layer in enumerate(stack):
        for n, node in enumerate(layer):
            x = float(l) / (len(stack) - 1)
            y = (float(n) + .5) / len(layer)
            pos[node] = orientate((x, y), direction)

    return pos

def get_layout_normsize(pos: dict) -> dict:
    """Calculate normal sizes for given node positions.

    Args:
        pos:

    """

    # calculate norm scaling
    scale = get_layout_normscale(pos)

    return {
        'node_size':   0.0558 * scale ** 2,
        'node_radius': 23. * (0.01 * scale - 0.2),
        'line_width':  0.0030 * scale,
        'edge_width':  0.0066 * scale,
        'font_size':   0.1200 * scale }

def get_subgraphs(G: DiGraph) -> None:

    import nemoa

    # find (disconected) complexes in graph
    graphs = list(networkx.connected_component_subgraphs(G.to_undirected()))
    if len(graphs) > 1:
        nemoa.log('note', '%i complexes found' % (len(graphs)))
    for i in range(len(graphs)):
        for n in graphs[i].nodes(): G.node[n]['complex'] = i

    return True

def get_groups(G: DiGraph, attribute: Optional[str] = None,
    param: Optional[str] = None) -> dict:

    if attribute == None and param == None:
        attribute = 'group'

    groups = {'': []}

    for node, data in G.nodes(data = True):
        if not isinstance(data, dict):
            groups[''].append(node)
            continue
        elif not attribute == None and not attribute in data:
            groups[''].append(node)
            continue
        elif not param == None \
            and not ('params' in data and param in data['params']):
            groups[''].append(node)
            continue
        if not attribute == None and param == None:
            group = data.get(attribute)
        elif attribute == None and not param == None:
            group = data['params'].get(param)
        else:
            group = (data.get(attribute), data['params'].get(param))
        if not group in groups:
            groups[group] = [node]
            continue
        groups[group].append(node)

    return groups

def get_node_layout(ntype: str) -> dict:

    layouts = {
        'dark blue': { 'color': 'marine blue', 'font_color': 'white',
            'border_color': 'dark navy' },
        'light grey': { 'color': 'light grey', 'font_color': 'dark grey',
            'border_color': 'grey' },
        'dark grey': { 'color': 'dark grey', 'font_color': 'white',
            'border_color': 'black' }}

    types = {
        'observable': { 'description': 'Observable', 'groupid': 0,
            'layout': 'dark blue' },
        'source': { 'description': 'Source', 'groupid': 1,
            'layout': 'dark blue' },
        'latent': { 'description': 'Latent', 'groupid': 2,
            'layout': 'light grey' },
        'target': { 'description': 'Target', 'groupid': 3,
            'layout': 'dark grey' },
        'isolated': { 'description': 'Isolated', 'groupid': 4,
            'layout': 'dark grey' }}

    t = types.get(ntype, {})
    layout = layouts.get(t.get('layout', None), {})
    layout['description'] = t.get('description', 'Unknown')
    layout['groupid'] = t.get('groupid', 'none')

    return layout

def is_directed(G: DiGraph) -> Optional[bool]:
    """Determine if layered graph is directed.

    Args:
        G: networkx graph instance

    """

    if is_layered(G):
        decl = G.graph.get('directed')
        if isinstance(decl, bool): return decl
        layers = get_layers(G)
        if len(layers) == 1: return False
        i = G.node.get(layers[0][0], {}).get('visible', False)
        o = G.node.get(layers[-1][0], {}).get('visible', False)
        if i and o: return True
        return False

    return None

def is_layered(G: DiGraph) -> bool:
    """Test if graph nodes contain layer attributes.

    Args:
        G: networkx graph instance

    """

    require = ['layer', 'layer_id', 'layer_sub_id']
    for node, data in G.nodes(data = True):
        for key in require:
            if not key in data: return False

    return True

def get_layout_normscale(pos: dict) -> float:
    """Calculate scaling.

    Args:
        pos: dictionary with node positions

    """

    # calculate euclidean distances between node positions
    euklid = lambda x: numpy.sqrt(numpy.sum(x ** 2))
    dlist = []
    for i, u in enumerate(pos.keys()):
        for j, v in enumerate(list(pos.keys())[i + 1:], i + 1):
            pu, pv = numpy.array(pos[u]), numpy.array(pos[v])
            dlist.append(euklid(pu - pv))
    darr = numpy.array(dlist)

    # calculate maximal scaling factor for non overlapping nodes
    # by minimal euklidean distance between node positions
    maxscale = 2.32 * numpy.amin(darr)

    # calculate minimal scaling factor
    # by average euklidean distance between node positions
    minscale = 0.20 * numpy.mean(darr)

    # if some nodes are exceptional close
    # the overlapping of those nodes is not avoided
    if minscale > maxscale: return minscale

    return minscale * (2. - minscale / maxscale)

def rescale_layout(pos: dict, size: Optional[tuple] = None,
    padding: Optional[tuple] = None, rotate: float = 0.0) -> dict:
    """Rescale node positions.

    Args:
        pos (dict): dictionary with node positions

    Kwargs:
        size (tuple, optional): size in pixel (x, y)
            default is None, which means no rescale
        padding (tuple, optional): padding in percentage (up, down, left, right)
            default is None, which means no padding
        rotate (float, optional): rotation angle in degrees
            default is 0.0, which means no rotation

    """

    data = numpy.array([(x, y) for x, y in list(pos.values())])

    # rotate positions around its center a by given rotation angle
    if bool(rotate):
        theta = numpy.radians(rotate)
        cos, sin = numpy.cos(theta), numpy.sin(theta)
        R = numpy.array([[cos, -sin], [sin, cos]])
        mean = data.mean(axis = 0)
        data = numpy.dot(data - mean, R.T) + mean

    # rescale positions with padding [up, right, down, left]
    if not isinstance(size, type(None)):
        dmin, dmax = numpy.amin(data, axis = 0), numpy.amax(data, axis = 0)
        if isinstance(padding, type(None)): u, r, d, l = 0., 0., 0., 0.
        else: u, r, d, l = padding
        pmin, pmax = numpy.array([l, d]), 1. - numpy.array([r, u])
        data = (pmax - pmin) * (data - dmin) / (dmax - dmin) + pmin
        data = numpy.array(size) * data

    return {node: tuple(data[i]) for i, node in enumerate(pos.keys())}
