# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import matplotlib
import nemoa
import networkx
import numpy

COLOR = {
    'black':      (0.,     0.,     0.,     1.),
    'white':      (1.,     1.,     1.,     1.),
    'alphawhite': (1.,     1.,     1.,     0.),
    'red':        (1.,     0.,     0.,     1.),
    'green':      (0.,     0.5,    0.,     1.),
    'blue':       (0.,     0.0,    0.7,    1.),
    'lightgrey':  (0.8,    0.8,    0.8,    1.),
    'lightgrey1': (0.96,   0.96,   0.96,   1.),
    'lightgrey2': (0.867,  0.867,  0.867,  1.),
    'lightgrey3': (0.2,    0.2,    0.2,    1.),
    'lightgreen': (0.6,    0.8,    0.196,  1.),
    'lightblue':  (0.439,  0.502,  0.565,  1.),
    'cornflower': (0.27,   0.51,   0.7,    1.),
    'lg1-bg':     (0.9529, 0.9529, 0.9529, 1.),
    'lg1-border': (0.7765, 0.7765, 0.7765, 1.),
    'lg1-font':   (0.2667, 0.2667, 0.2667, 1.),
    'lb1-bg':     (0.5450, 0.6470, 0.8078, 1.),
    'lb1-font':   (0.1367, 0.1367, 0.1367, 1.),
    'lb1-border': (0.1058, 0.3215, 0.4352, 1.),
    'lg2-bg':     (0.8235, 0.8235, 0.8235, 1.),
    'lg2-border': (0.5356, 0.5356, 0.5356, 1.),
    'lg2-font':   (0.2667, 0.2667, 0.2667, 1.),
}

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
        backcolor = COLOR[attr['color']]
        facecolor = COLOR['black']

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
        linecolor = list(COLOR[attr['color']])

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
            True: edge colors are determined by their weight and the
                keyword arguents 'edge_color_pos_weight',
                'edge_color_neg_weight' and 'edge_color_zero_weight'
            False: edges are black
        edge_color_pos_weight (string): name of color for positive
            weighted edges. For a full list of specified color names
            see nemoa.common.plot.COLOR
        edge_color_neg_weight (string): name of color for negative
            weighted edges. For a full list of specified color names
            see nemoa.common.plot.COLOR
        edge_color_zero_weight (string): name of color for zero
            weighted edges. For a full list of specified color names
            see nemoa.common.plot.COLOR
        edge_curvature (float): value within the intervall [-1, 1],
            that determines the curvature of the edges.
            Thereby 1 equals max convexity and -1 max concavity.
        graph_direction (string): string within the list ['up', 'down',
            'left', 'right'], that dermines the plot direction of the
            graph. 'up' means, the first layer is at the bottom.
        arrow_style (string):


    Returns:
        Boolen value which is True if no error occured.

    """

    node_size_max   = 1000.  # maximum node size
    node_size_scale = 3.7    # node size scale factor
    font_size_max   = 18.    # maximum font size
    font_size_scale = .95    # ration fon size to node
    edge_size_scale = 1.5    # edge size scale factor
    edge_arr_scale  = 6.     # edge arrow size scale factor

    if not 'edge_curvature' in kwargs:
        kwargs['edge_curvature'] = 1.0
    if not 'arrow_style' in kwargs:
        kwargs['arrow_style'] = '-|>'
    if not 'visible_node_bg_color' in kwargs:
        kwargs['visible_node_bg_color'] = 'lb1-bg'
    if not 'visible_node_font_color' in kwargs:
        kwargs['visible_node_font_color'] = 'lb1-font'
    if not 'visible_node_border_color' in kwargs:
        kwargs['visible_node_border_color'] = 'lb1-border'
    if not 'hidden_node_bg_color' in kwargs:
        kwargs['hidden_node_bg_color'] = 'lg2-bg'
    if not 'hidden_node_font_color' in kwargs:
        kwargs['hidden_node_font_color'] = 'lg2-font'
    if not 'hidden_node_border_color' in kwargs:
        kwargs['hidden_node_border_color'] = 'lg2-border'
    if not 'edge_weight' in kwargs:
        kwargs['edge_weight'] = 'adjacency'
    if not 'edge_color_enabled' in kwargs:
        kwargs['edge_color_enabled'] = True
    if not 'edge_color_pos_weight' in kwargs:
        kwargs['edge_color_pos_weight'] = 'green'
    if not 'edge_color_neg_weight' in kwargs:
        kwargs['edge_color_neg_weight'] = 'red'
    if not 'edge_color_zero_weight' in kwargs:
        kwargs['edge_color_zero_weight'] = 'alphawhite'

    # create node stack (list of node lists)
    layers = graph.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node in graph.nodes():
        count[graph.node[node]['params']['layer']] += 1
    nodes = [range(count[layer]) for layer in layers]
    for node in graph.nodes():
        lid = graph.node[node]['params']['layer_id']
        nid = graph.node[node]['params']['layer_sub_id']
        nodes[lid][nid] = node

    # (optional) sort nodes
    if kwargs['node_sort']:

        # start with first non-input layer
        for layer, tgt_nodes in enumerate(nodes):
            if layer == 0: continue
            src_nodes = nodes[layer - 1]
            src_size = len(src_nodes)
            tgt_size = len(tgt_nodes)

            # calculate cost matrix for positions of target nodes
            cost = numpy.zeros((tgt_size, tgt_size))

            for tgt_id, tgt_node in enumerate(tgt_nodes):
                for tgt_pos in range(tgt_size):
                    for src_id, src_node in enumerate(src_nodes):
                        if (src_node, tgt_node) in graph.edges():
                            weight = graph.edge[
                                src_node][tgt_node]['weight']
                        elif (tgt_node, src_node) in graph.edges():
                            weight = graph.edge[
                                tgt_node][src_node]['weight']
                        else: continue

                        # add cost from src node to tgt node
                        # by calculating distances in one dimension
                        distance = numpy.absolute(
                            (tgt_pos + .5) / (tgt_size + 1.)
                            - (src_id + .5) / (src_size + 1.))

                        cost[tgt_pos, tgt_id] += weight * distance

            # create selection order of target nodes sorted by savings
            selectorder = []
            maxcost = numpy.amax(cost, axis = 0)
            mincost = numpy.amin(cost, axis = 0)
            savings = maxcost - mincost

            for tgt_id, tgt_node in enumerate(tgt_nodes):
                selectorder.append((savings[tgt_id], tgt_id))

            sortedselect = [src_node[1] for src_node in \
                sorted(selectorder, key = lambda x: x[0])]

            # calculate optimal positions in selection order
            max_cost = numpy.amax(cost)
            new_tgt_nodes = [''] * tgt_size
            for tgt_id in sortedselect:
                optpos = numpy.argmin(cost[:, tgt_id])
                new_tgt_nodes[optpos] = tgt_nodes[tgt_id]
                cost[:, tgt_id] = max_cost + 1.
                cost[optpos, :] = max_cost + 1.

            nodes[layer] = new_tgt_nodes

    # calculate sizes
    n_len = max([len(layer) for layer in nodes])
    l_len = len(nodes)
    scale = min(240. / float(n_len), 150. / float(l_len), 35.)
    graph_caption_pos = -0.0025 * scale

    # calculate node positions for layer graph layout
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
    n_count   = float(len(graph))
    n_density = float(max(n_len, l_len))
    n_scale   = min(1., node_size_scale / n_density)
    n_size    = node_size_max * n_scale
    n_radius  = numpy.sqrt(n_size) / 600.
    n_fontmax = font_size_max * \
        numpy.sqrt(n_scale) * font_size_scale
    line_width = 2. / n_density
    edge_line_width = edge_size_scale / numpy.sqrt(n_count)

    # draw nodes
    for layer in nodes:
        for node in layer:
            attr = graph.node[node]
            is_visible = attr['params']['visible']

            # get node colors for backgroud, label and border
            color = {}
            if 'bg_color' in attr['params']:
                color['bg'] = attr['params']['bg_color']
            elif is_visible:
                color['bg'] = kwargs['visible_node_bg_color']
            else:
                color['bg'] = kwargs['hidden_node_bg_color']
            if 'font_color' in attr['params']:
                color['font'] = attr['params']['font_color']
            elif is_visible:
                color['font'] = kwargs['visible_node_font_color']
            else:
                color['font'] = kwargs['hidden_node_font_color']
            if 'border_color' in attr['params']:
                color['border'] = attr['params']['border_color']
            elif is_visible:
                color['border'] = kwargs['visible_node_border_color']
            else:
                color['border'] = kwargs['hidden_node_border_color']

            # determine label and fontsize
            label_str = attr['params']['label']
                #if is_visible \
                #else 'n%d' % (layer.index(node) + 1)
            node_label = nemoa.common.text.labelfomat(label_str)
            node_font_size = n_fontmax / numpy.sqrt(len(label_str))

            # draw node and node label
            node_obj = networkx.draw_networkx_nodes(graph, pos,
                node_size   = n_size,
                linewidths  = line_width,
                nodelist    = [node],
                node_shape  = 'o',
                node_color  = COLOR[color['bg']])
            networkx.draw_networkx_labels(graph, pos,
                font_size   = node_font_size,
                labels      = {node: node_label},
                font_color  = COLOR[color['font']],
                font_weight = 'normal')
            node_obj.set_edgecolor(
                COLOR[color['border']])

            # patch node for edges
            c = matplotlib.patches.Circle(pos[node],
                radius = n_radius, alpha = 0.)
            ax.add_patch(c)
            graph.node[node]['patch'] = c

    # draw edges
    seen = {}
    for (u, v, attr) in graph.edges(data = True):

        # get edge curvature
        n1  = graph.node[u]['patch']
        n2  = graph.node[v]['patch']
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

        # get edge weight
        weight = graph.edge[u][v]['weight']
        if kwargs['edge_weight'] == 'adjacency':
            edge_weight = edge_line_width
        else:
            edge_weight = edge_line_width * weight

        # get edge color
        if kwargs['edge_color_enabled']:
            pcol = numpy.array(COLOR[kwargs['edge_color_pos_weight']])
            ncol = numpy.array(COLOR[kwargs['edge_color_neg_weight']])
            zcol = numpy.array(COLOR[kwargs['edge_color_zero_weight']])
            if weight > 0: 
                edge_color = zcol + (pcol - zcol) * numpy.abs(weight)
            else:
                edge_color = zcol + (ncol - zcol) * numpy.abs(weight)
        else:
            edge_color = COLOR['black']

        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * .2)

        arrow = matplotlib.patches.FancyArrowPatch(
            posA = n1.center,
            posB = n2.center,
            patchA = n1,
            patchB = n2,
            arrowstyle = kwargs['arrow_style'],
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale = edge_arr_scale,
            linewidth = edge_weight,
            color = edge_color)

        seen[(u, v)] = rad
        ax.add_patch(arrow)

    return True
