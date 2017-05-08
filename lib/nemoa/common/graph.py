# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def get_layer_layout(graph, minimize = 'weight', threshold = 0.0,
    transform = None):
    """Calculate positions for layer layout of multilayer graphs.

    Args:
        graph: networkx graph instance

    """

    if not nx_is_multilayer(graph): return None

    import networkx
    import numpy

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

    # calculate node positions in square [0, 1] x [0, 1]
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
