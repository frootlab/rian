# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def nx_multilayer_layout(graph, minimize = 'weight', threshold = 0.0,
    transform = None):
    """Calculate positions for layer layout of multilayer graphs.

    Args:
        graph: networkx graph instance

    """

    try: import numpy
    except ImportError: raise ImportError(
        "nx_multilayer_layout() requires numpy: https://scipy.org/")
    try: import networkx
    except ImportError: raise ImportError(
        "nx_multilayer_layout() requires networkx: https://networkx.github.io/")

    assert nx_is_multilayer(graph), \
        "nx_multilayer_layout() requires networkx multilayer graph"

    if len(graph) == 0: return {}
    if len(graph) == 1: return { graph.nodes()[0]: (0.5, 0.5)}

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

    # sort node stack by attribute
    if isinstance(minimize, str):
        edges = {(u, v): data \
            for (u, v, data) in graph.edges(data = True)}

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
                    if weight < threshold: continue
                    if type(transform) == 'function':
                        weight = transform(weight)
                    for pid in range(tlen):
                        dist = numpy.absolute(
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
    pos = {}
    for l, layer in enumerate(stack):
        for n, node in enumerate(layer):
            x = float(l) / (len(stack) - 1)
            y = (float(n) + 0.5) / len(layer)
            pos[node] = (x, y)

    return pos

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

def nx_get_scaling(pos):
    """Calculate scaling.

    Args:
        pos:

    """

    try: import numpy
    except ImportError: raise ImportError(
        "nx_get_scaling() requires numpy: https://scipy.org/")

    # calculate euclidean distances of node positions
    dist = lambda (ux, uy), (vx, vy): \
        numpy.sqrt((ux - vx) ** 2 + (uy - vy) ** 2)
    #darr = numpy.zeros((len(pos), len(pos)))
    dseq = []
    for i, u in enumerate(pos.keys()):
        for j, v in enumerate(pos.keys()[i + 1:], i + 1):
            dseq.append(dist(pos[u], pos[v]))
            #d = dist(pos[u], pos[v])
            #darr[i, j] = darr[j, i] = d
            #dseq.append(d)
    darr = numpy.array(dseq)

    # calculate maximal scaling factor from minimal node distance
    maxscale = 2.32 * numpy.amin(darr)

    # calculate minimal scaling factor from average node distance
    minscale = 0.2 * numpy.mean(darr)

    return (minscale + maxscale) / 2

def nx_rescale_layout(pos, xscale = (0., 1.), yscale = (0., 1.),
        padding = (0., 0., 0., 0.), rotate = 0.):
    """Rescale node positions.

    Args:
        pos:
    
    Kwargs:
        xscale:
        yscale:
        padding:
        rotate:

    """

    try: import numpy
    except ImportError: raise ImportError(
        "nx_rescale_layout() requires numpy: https://scipy.org/")

    nodes = pos.keys()
    data = numpy.array([[x, y] for x, y in pos.values()])
    size = numpy.array([xscale, yscale])

    # rotate positions around its center a by given rotation angle
    if bool(rotate):
        theta = numpy.radians(rotate)
        cos, sin = numpy.cos(theta), numpy.sin(theta)
        R = numpy.array([[cos, -sin], [sin, cos]])
        mean = data.mean(axis = 0)
        data = numpy.dot(data - mean, R.T) + mean

    # rescale position to box [0, 1] x [0, 1] with padding [u, r, d, l]
    dmin, dmax = numpy.amin(data, axis = 0), numpy.amax(data, axis = 0)
    u, r, d, l = padding
    pmin, pmax = numpy.array([l, d]), 1. - numpy.array([r, u])
    data = (pmax - pmin) * (data - dmin) / (dmax - dmin) + pmin

    # rescale box to given xscale and yscale
    sarr = numpy.array([xscale, yscale]).T
    smin, smax = sarr[0], sarr[1]
    data = (smax - smin) * data + smin

    return {node: tuple(data[i]) for i, node in enumerate(nodes)}
