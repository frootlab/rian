# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import matplotlib
import nemoa
import networkx
import numpy

def color(*args):
    """Convert color name of XKCD color name survey to RGBA tuple.

    Args:
        List of color names. If the list is empty, a full list of
        available color names is returned. Otherwise the first valid
        color in the list is returned as RGBA tuple. If no color is
        valid None is returned.

    """

    if len(args) == 0:
        clist = matplotlib.colors.get_named_colors_mapping().keys()
        return [cname[5:].title() \
            for cname in clist if cname[:5] == 'xkcd:']
    if args[0] == 'alpha':
        return (0., 0., 0., 0.)
    rgba = None
    for cname in args:
        try:
            rgba = matplotlib.colors.to_rgba('xkcd:%s' % cname)
            break
        except ValueError:
            continue
    return rgba

def heatmap(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create heatmap
    cax = ax.imshow(array,
        cmap = matplotlib.cm.hot_r,
        interpolation = kwargs['interpolation'],
        extent = (0, array.shape[1], 0, array.shape[0]))

    # create labels for axis
    max_font_size = 12.
    y_labels = []
    for label in kwargs['units'][0]:
        if ':' in label: label = label.split(':', 1)[1]
        y_labels.append(nemoa.common.text.labelfomat(label))
    x_labels = []
    for label in kwargs['units'][1]:
        if ':' in label: label = label.split(':', 1)[1]
        x_labels.append(nemoa.common.text.labelfomat(label))
    fontsize = min(max_font_size, \
        400. / float(max(len(x_labels), len(y_labels))))
    matplotlib.pyplot.xticks(
        numpy.arange(len(x_labels)) + 0.5,
        tuple(x_labels), fontsize = fontsize, rotation = 65)
    matplotlib.pyplot.yticks(
        len(y_labels) - numpy.arange(len(y_labels)) - 0.5,
        tuple(y_labels), fontsize = fontsize)

    # create colorbar
    cbar = fig.colorbar(cax)
    for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

    return True

def histogram(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create histogram
    cax = ax.hist(array,
        normed = False,
        bins = kwargs['bins'],
        facecolor = kwargs['facecolor'],
        histtype = kwargs['histtype'],
        linewidth = kwargs['linewidth'],
        edgecolor = kwargs['edgecolor'])

    return True

def graph(graph, **kwargs):

    node_size_max = 800.     # maximum node size
    node_size_scale = 1.85   # node size scale factor
    font_size_max = 18.      # maximum font size
    edge_size_scale = 4.     # edge size scale factor
    edge_normalize = True
    edge_arr_scale = 8.      # edge arrow size scale factor
    edge_radius = 0.15       # edge radius for fancy edges

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate positions
    # Todo: allow layouts from pygraphviz_layout
    layout = kwargs['layout'].lower()
    if layout == 'random': pos = networkx.random_layout(graph)
    elif layout == 'circular': pos = networkx.circular_layout(graph)
    elif layout == 'shell': pos = networkx.shell_layout(graph)
    elif layout == 'spring': pos = networkx.spring_layout(graph)
    elif layout == 'spectral': pos = networkx.spectral_layout(graph)
    else: pos = networkx.spring_layout(graph)

    # calculate sizes of nodes, fonts and lines depending on graph size
    n_count = float(len(graph))
    n_size = max(node_size_max,
        node_size_scale * node_size_max / n_count)
    n_radius = numpy.sqrt(n_size) / 480.
    f_size = font_size_max * numpy.sqrt(n_size / node_size_max)
    n_fontmax = f_size * 0.9
    line_width = 2. / n_count
    edge_line_width = edge_size_scale / numpy.sqrt(n_count)

    # draw nodes
    for node, attr in graph.nodes(data = True):
        label = attr['label']

        # calculate node fontsize depending on label
        cl_label = label.replace('{', '').replace('}', '')
        if '_' in cl_label: len_label = len('_'.split(cl_label)[0]) \
            + 0.5 * len('_'.split(cl_label)[0])
        else: len_label = len(cl_label)
        node_font_size = n_fontmax / numpy.sqrt(len_label)

        # set colors (backcolor and facecolor)
        backcolor = color(attr['color'])
        facecolor = color('black')

        # draw node
        networkx.draw_networkx_nodes(graph, pos,
            node_size = n_size,
            linewidths = line_width,
            nodelist = [node],
            node_shape = 'o',
            node_color = backcolor)

        # draw node label
        networkx.draw_networkx_labels(graph, pos,
            font_size = node_font_size,
            labels = {node: label},
            font_color = facecolor,
            font_weight = 'normal')

        # patch node for edges
        c = matplotlib.patches.Circle(pos[node],
            radius = n_radius, alpha = 0.)
        ax.add_patch(c)
        graph.node[node]['patch'] = c

    # draw edges
    if edge_normalize:
        max_weight = 0.0
        for (u, v, attr) in graph.edges(data = True):
            if max_weight > attr['weight']: continue
            max_weight = attr['weight']
        edge_line_width /= max_weight
    seen = {}
    for (u, v, attr) in graph.edges(data = True):
        n1 = graph.node[u]['patch']
        n2 = graph.node[v]['patch']
        rad = edge_radius
        linewidth = edge_line_width * attr['weight']
        linecolor = list(color(attr['color']))

        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * 0.2)

        arrow = matplotlib.patches.FancyArrowPatch(
            posA = n1.center,
            posB = n2.center,
            patchA = n1,
            patchB = n2,
            arrowstyle = '-|>',
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale = edge_arr_scale,
            linewidth = linewidth,
            color = linecolor)

        seen[(u, v)] = rad
        ax.add_patch(arrow)

    return True

def layergraph(graph, **kwargs):
    """Plot graph with layered layout.

    Args:
        graph: nemoa graph instance from nemoa network instance

    Kwargs:
        edge_color_enabled (bool): flag for colored edges
            True: edge colors are determined by the sign of a given
                edge attribute defined by the keyword argument
                'edge_color_attribute'
            False: edges are black
        edge_color_attribute (string): name of edge attribute, that
            determines the edge colors by its sign.
            default: 'weight'
        edge_color_positive (string): name of color for edges with
            positive signed attribute. For a full list of specified
            color names see nemoa.common.plot.color()
        edge_color_negative (string): name of color for edges with
            negative signed attribute. For a full list of specified
            color names see nemoa.common.plot.color()
        edge_curvature (float): value within the intervall [-1, 1],
            that determines the curvature of the edges.
            Thereby 1 equals max convexity and -1 max concavity.
        graph_direction (string): string within the list ['up', 'down',
            'left', 'right'], that dermines the plot direction of the
            graph. 'up' means, the first layer is at the bottom.
        edge_arrow_style (string):  '-', '<-', '<->', '->',
            '<|-', '<|-|>', '-|>', '|-', '|-|', '-|'


    Returns:
        Boolen value which is True if no error occured.

    """

    node_size_max    = 1000.  # maximum node size
    node_size_scale  = 3.7    # node size scale factor
    font_size_max    = 18.    # maximum font size
    font_size_scale  = .95    # ration fon size to node
    edge_arr_scale   = 6.     # edge arrow size scale factor

    # set default settings for kwargs
    kwargs = nemoa.common.dict.merge(kwargs, {
        'node_sort_enabled':    True,
        'node_sort_attribute':  'weight',
        'node_scale':           1.0,
        'node_color_enabled':   True,
        'node_color_attribute': 'visible',
        'node_bg_color': {      True: 'light periwinkle',
                                False: 'light grey' },
        'node_font_color': {    True: 'black',
                                False: 'black' },
        'node_border_color': {  True: 'twilight blue',
                                False: 'black' },
        'edge_width_enabled':   True,
        'edge_width_attribute': 'weight',
        'edge_scale':           1.0,
        'edge_color_enabled':   True,
        'edge_color_attribute': 'weight',
        'edge_color_positive':  'green',
        'edge_color_negative':  'red',
        'edge_curvature':       1.0,
        'edge_arrow_style':     '-|>',
        'graph_direction':      'right' })

    # create list of node lists
    layers = graph.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node in graph.nodes():
        count[graph.node[node]['params']['layer']] += 1
    nodes = [range(count[layer]) for layer in layers]
    for node in graph.nodes():
        lid = graph.node[node]['params']['layer_id']
        nid = graph.node[node]['params']['layer_sub_id']
        nodes[lid][nid] = node

    # sort nodes by attribute
    if bool(kwargs['node_sort_enabled']):
        for lid, tlay in enumerate(nodes[1:], 1):
            slay = nodes[lid - 1]
            slen = len(slay)
            tlen = len(tlay)

            # calculate cost matrix for positions of target nodes
            cost = numpy.zeros((tlen, tlen))
            for tid, tnode in enumerate(tlay):
                for sid, snode in enumerate(slay):
                    if (snode, tnode) in graph.edges():
                        weight = graph.edge[snode][tnode]['weight']
                    elif (tnode, snode) in graph.edges():
                        weight = graph.edge[tnode][snode]['weight']
                    else: continue

                    for tpos in range(tlen):

                        # add cost from src node to tgt node
                        # by calculating distances in one dimension
                        distance = numpy.absolute(
                            (tpos + .5) / (tlen + 1.)
                            - (sid + .5) / (slen + 1.))

                        cost[tpos, tid] += weight * distance

            # create selection order of target nodes sorted by savings
            selectorder = []
            maxcost = numpy.amax(cost, axis = 0)
            mincost = numpy.amin(cost, axis = 0)
            savings = maxcost - mincost

            for tid, tnode in enumerate(tlay):
                selectorder.append((savings[tid], tid))

            sortedselect = [snode[1] for snode in \
                sorted(selectorder, key = lambda x: x[0])]

            # calculate optimal positions in selection order
            max_cost = numpy.amax(cost)
            newlayer = [''] * tlen
            for tid in sortedselect:
                oid = numpy.argmin(cost[:, tid])
                newlayer[oid] = tlay[tid]
                cost[:, tid] = max_cost + 1.
                cost[oid, :] = max_cost + 1.

            nodes[lid] = newlayer

    # calculate sizes
    n_len = max([len(layer) for layer in nodes])
    l_len = len(nodes)
    scale = min(240. / float(n_len), 150. / float(l_len), 35.)
    graph_caption_pos = -0.0025 * scale

    # calculate node positions for layered graph layout
    pos = {}
    pos_cap = {}
    for l_id, layer in enumerate(nodes):
        for n_id, node in enumerate(layer):
            n_pos = (float(n_id) + 0.5) / len(layer)
            l_pos = 1. - float(l_id) / (len(nodes) - 1.)
            pos[node] = {
                'up': (n_pos, 1. - l_pos), 'down': (n_pos, l_pos),
                'left': (l_pos, n_pos), 'right': (1. - l_pos, n_pos)
                }[kwargs['graph_direction']]
            pos_cap[node] = (pos[node][0],
                pos[node][1] + graph_caption_pos)

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate sizes of nodes, fonts and lines depending on graph size
    n_density = float(max(n_len, l_len))
    n_scale   = min(1., node_size_scale / n_density)
    n_size    = node_size_max * n_scale
    n_radius  = numpy.sqrt(n_size) / 600.
    n_fontmax = font_size_max * \
        numpy.sqrt(n_scale) * font_size_scale
    line_width = 2. / n_density

    # draw nodes
    for layer in nodes:
        for node in layer:
            attr = graph.node[node]
            
            # get colors
            if bool(kwargs['node_color_enabled']) \
                and kwargs['node_color_attribute'] in attr['params']:
                key = attr['params'][kwargs['node_color_attribute']]
                if key in kwargs['node_bg_color']:
                    node_bg_color = kwargs['node_bg_color'][key]
                else: node_bg_color = 'white'
                if key in kwargs['node_font_color']:
                    node_font_color = kwargs['node_font_color'][key]
                else: node_font_color = 'black'
                if key in kwargs['node_border_color']:
                    node_border_color = kwargs['node_border_color'][key]
                else: node_boder_color = 'black'
            else:
                node_bg_color = 'white'
                node_font_color = 'black'
                node_border_color = 'black'

            # determine label and fontsize
            label_str = attr['params']['label']
            node_label = nemoa.common.text.labelfomat(label_str)
            node_font_size = n_fontmax / numpy.sqrt(len(label_str))

            # draw node
            node_obj = networkx.draw_networkx_nodes(graph, pos,
                nodelist    = [node],
                linewidths  = line_width,
                node_size   = n_size * kwargs['node_scale'],
                node_shape  = 'o',
                node_color  = color(node_bg_color, 'white'))
            node_obj.set_edgecolor(color(node_border_color, 'black'))

            # draw node label
            networkx.draw_networkx_labels(graph, pos,
                labels      = {node: node_label},
                font_size   = node_font_size,
                font_color  = color(node_font_color, 'black'),
                font_weight = 'normal')

            # patch node for edges
            c = matplotlib.patches.Circle(pos[node],
                radius = n_radius, alpha = 0.)
            ax.add_patch(c)
            graph.node[node]['patch'] = c

    # draw edges
    seen = {}
    for (u, v) in graph.edges():

        # calculate edge curvature
        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * .2)
        else:
            rad = 0.5 * kwargs['edge_curvature']
            if kwargs['graph_direction'] == 'right':
                rad *= (pos[u][1] - pos[v][1]) * (pos[v][0] - pos[u][0])
            elif kwargs['graph_direction'] == 'left':
                rad *= (pos[v][1] - pos[u][1]) * (pos[u][0] - pos[v][0])
            elif kwargs['graph_direction'] == 'up':
                rad *= (pos[v][1] - pos[u][1]) * (pos[v][0] - pos[u][0])
            elif kwargs['graph_direction'] == 'down':
                rad *= (pos[u][1] - pos[v][1]) * (pos[u][0] - pos[v][0])
            else: rad = .0
        seen[(u, v)] = rad

        # calculate edge width from attribute
        if not bool(kwargs['edge_width_enabled']) \
            or not bool(kwargs['edge_width_attribute']):
            edge_width = line_width * kwargs['edge_scale']
        elif not kwargs['edge_width_attribute'] in graph.edge[u][v]:
            edge_width = 0.0
        else:
            # normalization with softstep between [-1.3, 1.3]
            wattr = graph.edge[u][v][kwargs['edge_width_attribute']]
            if not isinstance(wattr, float): edge_width = 0.0
            else: edge_width = nemoa.common.math.softstep(wattr) \
                * line_width * kwargs['edge_scale']

        # get edge color from attribute
        if not bool(kwargs['edge_color_enabled']) \
            or not bool(kwargs['edge_color_attribute']):
            edge_color = 'black'
        elif not kwargs['edge_color_attribute'] in graph.edge[u][v]:
            edge_color = 'alpha'
        else:
            cattr = graph.edge[u][v][kwargs['edge_color_attribute']]
            if cattr > 0: edge_color = kwargs['edge_color_positive']
            else : edge_color = kwargs['edge_color_negative']

        # draw edge
        nodeA = graph.node[u]['patch']
        nodeB = graph.node[v]['patch']
        arrow = matplotlib.patches.FancyArrowPatch(
            posA            = nodeA.center,
            posB            = nodeB.center,
            patchA          = nodeA,
            patchB          = nodeB,
            arrowstyle      = kwargs['edge_arrow_style'],
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = edge_arr_scale,
            linewidth       = edge_width,
            color           = color(edge_color, 'black'))
        ax.add_patch(arrow)

    return True
