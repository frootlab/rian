# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def get_layout(graph, layout = 'spring',
    size = None, padding = None, rotate = None, **kwargs):
    """Calculate positions of nodes, depending on graph layout.

    Args:
        graph: networkx graph instance

    Kwargs:
        layout (string):
        size (tuple):

    """

    try: import networkx as nx
    except ImportError: raise ImportError(
        "nemoa.common.graph.layout() requires networkx: "
        "https://networkx.github.io")

    # Todo: allow layouts from pygraphviz_layout

    if layout == 'spring':
        pos = nx.spring_layout(graph, **kwargs)
    elif layout == 'layer':
        pos = get_layer_layout(graph, **kwargs)
    elif layout == 'random':
        pos = nx.random_layout(graph, **kwargs)
    elif layout == 'circular':
        pos = nx.circular_layout(graph, **kwargs)
    elif layout == 'shell':
        pos = nx.shell_layout(graph, **kwargs)
    elif layout == 'spectral':
        pos = nx.spectral_layout(graph, **kwargs)
    elif layout == 'fruchterman_reingold':
        pos = nx.fruchterman_reingold_layout(graph, **kwargs)
    else: raise ValueError(
        "nemoa.common.graph.layout(): "
        "'%s' is not a valid graph layout." % layout)

    # rescale node positions to given figure size, padding
    # and rotation angle
    pos = rescale_layout(pos, size = size, padding = padding,
        rotate = rotate)

    return pos

def get_layers(graph):

    # create node stack as list of lists
    # sorted by the node attributes layer_id and layer_sub_id
    sort = {}
    for node, data in graph.nodes(data = True):
        l = (data.get('layer'), data.get('layer_id'))
        n = (node, data.get('layer_sub_id'))
        if not l in sort: sort[l] = [n]
        else: sort[l].append(n)
    layers = []
    for (layer, lid) in sorted(sort.keys(), key = lambda x: x[1]):
        layers.append([node for (node, nid) in \
            sorted(sort.get((layer, lid), []), key = lambda x: x[1])])
    return layers

def get_layer_layout(graph, direction = 'right',
    minimize = 'weight'):
    """Calculate node positions for layer layout.

    Args:
        graph: networkx graph instance

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nemoa.common.graph.get_layer_layout() requires numpy: "
        "https://scipy.org")

    assert is_layered(graph), (
        "nemoa.common.graph.get_layer_layout(): "
        "graph is not layered.")

    if len(graph) == 0: return {}
    if len(graph) == 1: return { graph.nodes()[0]: (0.5, 0.5) }

    # get list of node lists, sorted by layer (list of lists)
    stack = get_layers(graph)

    # sort node stack to minimize the euclidean distances
    # of connected nodes
    if isinstance(minimize, str):
        edges = {(u, v): data \
            for (u, v, data) in graph.edges(data = True)}

        for lid, tgt in enumerate(stack[1:], 1):
            src  = stack[lid - 1]
            slen = len(src)
            tlen = len(tgt)

            # calculate cost matrix for positions by weights
            cost = np.zeros((tlen, tlen))
            for sid, u in enumerate(src):
                for tid, v in enumerate(tgt):
                    data = edges.get((u, v))
                    if data == None: data = edges.get((v, u))
                    if not isinstance(data, dict): continue
                    value = data.get(minimize)
                    if not isinstance(value, float): continue
                    weight = np.absolute(value)
                    for pid in range(tlen):
                        dist = np.absolute(
                            (pid + .5) / (tlen + 1.) \
                            - (sid + .5) / (slen + 1.))
                        cost[pid, tid] += dist * weight

            # choose (node, position) pair with maximum savings
            # thereby penalize large distances by power two
            # repeat until all nodes have positions
            nsel = range(tlen) # node select list
            psel = range(tlen) # position select list
            sort = [None] * tlen
            for i in range(tlen):
                cmax = np.amax(cost[psel][:, nsel], axis = 0)
                cmin = np.amin(cost[psel][:, nsel], axis = 0)
                diff = cmax ** 2 - cmin ** 2
                nid  = nsel[np.argmax(diff)]
                pid  = psel[np.argmin(cost[psel][:, nid])]
                sort[pid] = tgt[nid]
                nsel.remove(nid)
                psel.remove(pid)
            stack[lid] = sort

    # calculate node positions in box [0, 1] x [0, 1]
    orientate = lambda (x, y), d: {'right': (x, y), 'up': (y, x),
        'left': (1. - x,  y), 'down': (y, 1. - x)}.get(d, (x, y))
    pos = {}
    for l, layer in enumerate(stack):
        for n, node in enumerate(layer):
            x = float(l) / (len(stack) - 1)
            y = (float(n) + 0.5) / len(layer)
            pos[node] = orientate((x, y), direction)

    return pos

def get_layout_normsize(pos):
    """Calculate normal sizes for given node positions.

    Args:
        graph: networkx graph instance

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nemoa.common.graph.layout_normsizes() requires numpy: "
        "https://scipy.org")

    # calculate norm scaling
    scale = get_layout_normscale(pos)

    return {
        'node_size':   0.0558 * scale ** 2,
        'node_radius': 23. * (0.01 * scale - 0.2),
        'line_width':  0.0030 * scale,
        'edge_width':  0.0066 * scale,
        'font_size':   0.1200 * scale }

def get_subgraphs(graph):

    # Todo

    try: import networkx as nx
    except ImportError: raise ImportError(
        "nemoa.common.graph.subgraphs() requires networkx: "
        "https://networkx.github.io")

    import nemoa

    # find (disconected) complexes in graph
    graphs = list(nx.connected_component_subgraphs(
        graph.to_undirected()))
    if len(graphs) > 1:
        nemoa.log('note', '%i complexes found' % (len(graphs)))
    for i in xrange(len(graphs)):
        for n in graphs[i].nodes(): graph.node[n]['complex'] = i

    return True

def get_groups(graph, attribute = None, param = None):

    if attribute == None and param == None:
        attribute = 'group'

    groups = {None: []}

    for node, data in graph.nodes(data = True):
        if not isinstance(data, dict):
            groups[None].append(node)
            continue
        elif not attribute == None and not attribute in data:
            groups[None].append(node)
            continue
        elif not param == None \
            and not ('params' in data and param in data['params']):
            groups[None].append(node)
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

def get_node_layout(ntype):

    layouts = {
        'dark blue': {
            'color': 'marine blue',
            'font_color': 'white',
            'border_color': 'dark navy'},
        'light grey': {
            'color': 'light grey',
            'font_color': 'dark grey',
            'border_color': 'grey'},
        'dark grey': {
            'color': 'dark grey',
            'font_color': 'white',
            'border_color': 'black' }}

    types = {
        'observable': {
            'description': 'Observable',
            'groupid': 0,
            'layout': 'dark blue' },
        'source': {
            'description': 'Source',
            'groupid': 1,
            'layout': 'dark blue' },
        'latent': {
            'description': 'Latent',
            'groupid': 2,
            'layout': 'light grey' },
        'target': {
            'description': 'Target',
            'groupid': 3,
            'layout': 'dark grey' },
        'isolated': {
            'description': 'Isolated',
            'groupid': 4,
            'layout': 'dark grey' } }
    
    t = types.get(ntype, {})
    layout = layouts.get(t.get('layout', None), {})
    layout['description'] = t.get('description', 'Unknown')
    layout['groupid'] = t.get('groupid', 'none')

    return layout

def is_directed(graph):
    """Test if layered graph is directed.

    Args:
        graph: networkx graph instance

    """

    if is_layered(graph):
        layers = get_layers(graph)
        if len(layers) == 1: return False
        i = graph.node.get(layers[0][0], {}).get('visible', True)
        o = graph.node.get(layers[-1][0], {}).get('visible', True)
        if i and o: return True
        return False

    return None

def is_layered(graph):
    """Test if graph nodes contain layer attributes.

    Args:
        graph: networkx graph instance

    """

    require = ['layer', 'layer_id', 'layer_sub_id']
    for node, data in graph.nodes(data = True):
        for key in require:
            if not key in data: return False

    return True

def get_layout_normscale(pos):
    """Calculate scaling.

    Args:
        pos: dictionary with node positions

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nemoa.common.graph.get_layout_normscale() requires numpy: "
        "https://scipy.org")

    # calculate euclidean distances between node positions
    euklid = lambda x: np.sqrt(np.sum(x ** 2))
    dlist = []
    for i, u in enumerate(pos.keys()):
        for j, v in enumerate(pos.keys()[i + 1:], i + 1):
            pu, pv = np.array(pos[u]), np.array(pos[v])
            dlist.append(euklid(pu - pv))
    darr = np.array(dlist)

    # calculate maximal scaling factor for non overlapping nodes
    # by minimal euklidean distance between node positions
    maxscale = 2.32 * np.amin(darr)

    # calculate minimal scaling factor
    # by average euklidean distance between node positions
    minscale = 0.20 * np.mean(darr)

    # if some nodes are exceptional close
    # the overlapping of those nodes is not avoided
    if minscale > maxscale: return minscale

    return minscale * (2. - minscale / maxscale)

def rescale_layout(pos, size = None, padding = None, rotate = 0.):
    """Rescale node positions.

    Args:
        pos: dictionary with node positions

    Kwargs:
        size (tuple): size in pixel (x, y)
            default is None, which means no rescale
        padding (tuple): padding in percentage (up, down, left, right)
            default is None, which means no padding
        rotate (float): rotation angle in degrees
            default is 0. which mean no rotation

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nemoa.common.graph.rescale_layout() requires numpy: "
        "https://scipy.org")

    data = np.array([(x, y) for x, y in pos.values()])

    # rotate positions around its center a by given rotation angle
    if bool(rotate):
        theta = np.radians(rotate)
        cos, sin = np.cos(theta), np.sin(theta)
        R = np.array([[cos, -sin], [sin, cos]])
        mean = data.mean(axis = 0)
        data = np.dot(data - mean, R.T) + mean

    # rescale positions with padding [u, r, d, l]
    if not isinstance(size, type(None)):
        dmin, dmax = np.amin(data, axis = 0), np.amax(data, axis = 0)
        if isinstance(padding, type(None)): u, r, d, l = 0., 0., 0., 0.
        else: u, r, d, l = padding
        pmin, pmax = np.array([l, d]), 1. - np.array([r, u])
        data = (pmax - pmin) * (data - dmin) / (dmax - dmin) + pmin
        data = np.array(size) * data

    return {node: tuple(data[i]) for i, node in enumerate(pos.keys())}
