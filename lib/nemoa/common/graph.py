# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def nx_get_layout(graph, layout = 'spring', scale = None,
    padding = None, **kwargs):
    """Calculate positions of nodes, depending on graph layout.

    Args:
        graph: networkx graph instance
    
    Kwargs:
        layout (string):
        scale (tuple or None):

    """

    try: import networkx as nx
    except ImportError: raise ImportError(
        "nx_layout() requires networkx: https://networkx.github.io/")

    # Todo: allow layouts from pygraphviz_layout
    
    if layout == 'spring':
        pos = nx.spring_layout(graph, **kwargs)
    elif layout == 'multilayer':
        pos = nx_get_multilayer_layout(graph, **kwargs)
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
    else:
        raise ValueError("nx_layout() invalid layout.")
        return None

    if isinstance(scale, type(None)): return pos

    # rescale node positions to figure size and padding
    pos = nx_rescale_layout(pos, scale = scale, padding = padding)
 
    return pos

def nx_get_multilayer_layout(graph, direction = 'right',
    minimize = 'weight'):
    """Calculate positions for layer layout of multilayer graphs.

    Args:
        graph: networkx graph instance

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nx_get_multilayer_layout() requires numpy: https://scipy.org/")

    assert nx_is_multilayer(graph), \
        "nx_get_multilayer_layout() requires networkx multilayer graph"

    if len(graph) == 0: return {}
    if len(graph) == 1: return { graph.nodes()[0]: (0.5, 0.5) }

    # create node stack as list of lists
    layers = graph.graph['params']['layer']
    nodes  = {n: data for (n, data) in graph.nodes(data = True)}
    count  = {layer: 0 for layer in layers}
    for data in nodes.values(): count[data['params']['layer']] += 1
    stack = [range(count[layer]) for layer in layers]
    for node, data in nodes.items():
        l = data['params']['layer_id']
        n = data['params']['layer_sub_id']
        stack[l][n] = node

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

def nx_get_normsizes(pos):
    """Calculate normal sizes for given node positions.

    Args:
        graph: networkx graph instance

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nx_get_normsizes() requires numpy: https://scipy.org/")

    # calculate norm scaling
    scale = nx_get_normscale(pos)
    
    return {
        'node_size':   0.0558 * scale ** 2,
        'node_radius': 23. * (0.01 * scale - 0.2),
        'line_width':  0.0030 * scale,
        'font_size':  0.1200 * scale }

def nx_get_groups(graph, param = None):

    # get groups
    groups = {None: []}
    for node, data in graph.nodes(data = True):
        if not isinstance(data, dict) \
            or not 'params' in data \
            or not param in data['params']:
            groups[None].append(node)
            continue
        group = data['params'].get(param)
        if not group in groups:
            groups[group] = [node]
            continue
        groups[group].append(node)
    
    return groups

def nx_is_multilayer(graph):
    """Test if graph is multilayer graph.

    Args:
        graph: networkx graph instance
    
    """

    retval = True

    # todo    

    # test type(graph)
    # print graph.graph['params']['layer']

    return retval

def nx_get_normscale(pos):
    """Calculate scaling.

    Args:
        pos: dictionary with node positions

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nx_get_normscale() requires numpy: https://scipy.org/")

    # calculate euclidean distances between node positions
    euklid = lambda (a, b), (c, d): np.sqrt((a - c) ** 2 + (b - d) ** 2)
    dlist = []
    for i, u in enumerate(pos.keys()):
        for j, v in enumerate(pos.keys()[i + 1:], i + 1):
            dlist.append(euklid(pos[u], pos[v]))
    darr = np.array(dlist)

    # calculate maximal scaling factor from minimal node distance and
    # minimal scaling factor from average node distance
    maxscale = 2.32 * np.amin(darr)
    minscale = 0.2 * np.mean(darr)

    return (minscale + maxscale) / 2

def nx_rescale_layout(pos, scale = None, padding = None, rotate = 0.):
    """Rescale node positions.

    Args:
        pos: dictionary with node positions
    
    Kwargs:
        xscale:
        yscale:
        padding:
        rotate:

    """

    try: import numpy as np
    except ImportError: raise ImportError(
        "nx_rescale_layout() requires numpy: https://scipy.org/")

    data = np.array([(x, y) for x, y in pos.values()])

    # rotate positions around its center a by given rotation angle
    if bool(rotate):
        theta = np.radians(rotate)
        cos, sin = np.cos(theta), np.sin(theta)
        R = np.array([[cos, -sin], [sin, cos]])
        mean = data.mean(axis = 0)
        data = np.dot(data - mean, R.T) + mean

    # rescale positions with padding [u, r, d, l]
    if not isinstance(scale, type(None)):
        dmin, dmax = np.amin(data, axis = 0), np.amax(data, axis = 0)
        if isinstance(padding, type(None)): u, r, d, l = 0., 0., 0., 0.
        else: u, r, d, l = padding
        pmin, pmax = np.array([l, d]), 1. - np.array([r, u])
        data = (pmax - pmin) * (data - dmin) / (dmax - dmin) + pmin
        data = np.array(scale) * data

    return {node: tuple(data[i]) for i, node in enumerate(pos.keys())}
