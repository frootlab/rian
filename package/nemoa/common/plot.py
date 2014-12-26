# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import matplotlib
import nemoa
import networkx
import numpy

COLOR = {
    'black': (0., 0., 0., 1.),
    'white': (1., 1., 1., 1.),
    'red': (1., 0., 0., 1.),
    'green': (0., 0.5, 0., 1.),
    'blue': (0., 0.0  , 0.7, 1.),
    'lightgrey': (0.8, 0.8, 0.8, 1.),
    'lightgrey1': (0.96, 0.96, 0.96, 1.),
    'lightgrey2': (0.867, 0.867, 0.867, 1.),
    'lightgrey3': (0.2, 0.2, 0.2, 1.),
    'lightgreen': (0.6, 0.8, 0.196, 1.),
    'lightblue': (0.439, 0.502, 0.565, 1.),
    'cornflower': (0.27, 0.51, 0.7, 1.),
    'lg1-bg': (0.9529, 0.9529, 0.9529, 1.),
    'lg1-border': (0.7765, 0.7765, 0.7765, 1.),
    'lg1-font': (0.2667, 0.2667, 0.2667, 1.),
    'lb1-bg': (0.5450, 0.6470, 0.8078, 1.),
    'lb1-font': (0.1367, 0.1367, 0.1367, 1.),
    'lb1-border': (0.1058, 0.3215, 0.4352, 1.),
    'lg2-bg': (0.8235, 0.8235, 0.8235, 1.),
    'lg2-border': (0.5356, 0.5356, 0.5356, 1.),
    'lg2-font': (0.2667, 0.2667, 0.2667, 1.),
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
        y_labels.append(nemoa.common.string.labelfomat(label))
    x_labels = []
    for label in kwargs['units'][1]:
        if ':' in label: label = label.split(':', 1)[1]
        x_labels.append(nemoa.common.string.labelfomat(label))
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
    node_font_size_max = f_size * 0.9
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
        node_font_size = node_font_size_max / numpy.sqrt(len_label)

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

def layergraph(graph, edge_curvature = 1.0, **kwargs):

    node_size_max = 800.     # maximum node size
    node_size_scale = 1.85   # node size scale factor
    font_size_max = 18.      # maximum font size
    edge_line_width_max = 4. # maximum edge linewidth
    edge_arr_scale = 8.      # edge arrow size scale factor

    # create node stack (list with lists of nodes)
    layers = graph.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node in graph.nodes():
        count[graph.node[node]['params']['layer']] += 1
    nodes = [range(count[layer]) for layer in layers]
    for node in graph.nodes():
        layer_id = graph.node[node]['params']['layer_id']
        layer_node_id = graph.node[node]['params']['layer_sub_id']
        nodes[layer_id][layer_node_id] = node

    # (optional) sort nodes
    if kwargs['node_sort']:
        # start with first layer which is not input
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
    scale = min(240. / n_len, 150. / l_len, 35.)
    graph_caption_pos = -0.0025 * scale

    # calculate node positions for layer graph layout
    pos = {}
    pos_cap = {}
    for l_id, layer in enumerate(nodes):
        for n_id, node in enumerate(layer):
            n_pos = (n_id + 0.5) / len(layer)
            l_pos = 1. - l_id / (len(nodes) - 1.)
            pos[node] = {
                'down': (n_pos, l_pos),
                'up': (n_pos, 1. - l_pos),
                'left': (l_pos, n_pos),
                'right': (1. - l_pos, n_pos)}[kwargs['graph_direction']]
            pos_cap[node] = (pos[node][0],
                pos[node][1] + graph_caption_pos)

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate sizes of nodes, fonts and lines depending on graph size
    n_count = float(len(graph))
    n_size = max(node_size_max,
        node_size_scale * node_size_max / n_count)
    n_radius = numpy.sqrt(n_size) / 600.
    f_size = font_size_max * numpy.sqrt(n_size / node_size_max)
    node_font_size_max = f_size * 0.9
    line_width = 5. / n_count
    edge_line_width = edge_line_width_max / n_count

    # draw nodes
    for layer in nodes:
        for node in layer:
            attr = graph.node[node]

            is_visible = attr['params']['visible']
            label_str = attr['params']['label'] if is_visible \
                else 'n%d' % (layer.index(node) + 1)
            label = nemoa.common.string.labelfomat(label_str)

            color = {
                True: {
                    'bg': COLOR['lb1-bg'],
                    'font': COLOR['lb1-font'],
                    'border': COLOR['lb1-border'] },
                False: {
                    'bg': COLOR['lg2-bg'],
                    'font': COLOR['lg2-font'],
                    'border': COLOR['lg2-border'] }
            }[is_visible]

            # calculate node fontsize depending on label
            cl_label = label.replace('{', '').replace('}', '')
            if '_' in cl_label:
                len_label = len('_'.split(cl_label)[0]) \
                    + 0.5 * len('_'.split(cl_label)[0])
            else: len_label = len(cl_label)
            node_font_size = node_font_size_max / numpy.sqrt(len_label)

            # set colors (backcolor and facecolor)
            backcolor = color['bg']
            facecolor = color['font']

            # draw node
            node_obj = networkx.draw_networkx_nodes(graph, pos,
                node_size = n_size,
                linewidths = line_width,
                nodelist = [node],
                node_shape = 'o',
                node_color = backcolor)

            node_obj.set_edgecolor(color['border'])

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
    seen = {}
    for (u, v, attr) in graph.edges(data = True):

        # calculate edge radius

        n1 = graph.node[u]['patch']
        n2 = graph.node[v]['patch']

        rad = edge_curvature
        if kwargs['graph_direction'] == 'right':
            rad *= (pos[u][1] - pos[v][1]) * (pos[v][0] - pos[u][0])
        elif kwargs['graph_direction'] == 'left':
            rad *= (pos[v][1] - pos[u][1]) * (pos[u][0] - pos[v][0])
        elif kwargs['graph_direction'] == 'up':
            rad *= (pos[v][1] - pos[u][1]) * (pos[v][0] - pos[u][0])
        elif kwargs['graph_direction'] == 'down':
            rad *= ()(pos[u][0] - pos[v][0])
        else:
            rad = 0.0

        # get weight
        weight = graph.edge[u][v]['weight']

        # get linecolor and linewidth (from weight)
        if kwargs['edge_weight'] == 'adjacency':
            linecolor = 'black'
            linewidth = edge_line_width
        else:
            linecolor = 'green' if weight > 0. else 'red'
            linewidth = edge_line_width * weight

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
