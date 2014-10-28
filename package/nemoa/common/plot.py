# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import networkx
import matplotlib
import matplotlib.pyplot
from matplotlib.patches import FancyArrowPatch, Circle

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
    #'lb1-border': (0.0039, 0.2745, 0.4156, 1.),
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
    y_labels = [nemoa.common.str_format_unit_label(
        label.split(':')[1]) for label in kwargs['units'][0]]
    x_labels = [nemoa.common.str_format_unit_label(
        label.split(':')[1]) for label in kwargs['units'][1]]
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

    node_size_max = 800.      # maximum node size
    node_size_scale = 1.85    # node size scale factor
    font_size_max = 18.       # maximum font size
    edge_line_width_max = 10. # maximum edge line with
    edge_arr_scale = 8.       # edge arrow size scale factor
    edge_radius = 0.15        # edge radius for fancy edges

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate positions
    # TODO: allow layouts from pygraphviz_layout
    if kwargs['layout'] == 'random':
        pos = networkx.random_layout(graph)
    elif kwargs['layout'] == 'circular':
        pos = networkx.circular_layout(graph)
    elif kwargs['layout'] == 'shell':
        pos = networkx.shell_layout(graph)
    elif kwargs['layout'] == 'spring':
        pos = networkx.spring_layout(graph)
    elif kwargs['layout'] == 'fruchterman_reingold':
        pos = networkx.fruchterman_reingold_layout(graph)
    elif kwargs['layout'] == 'spectral':
        pos = networkx.spectral_layout(graph)
    else:
        pos = networkx.spring_layout(graph)

    # calculate sizes of nodes, fonts and lines depending on graph size
    n_count = float(len(graph))
    n_size = max(node_size_max,
        node_size_scale * node_size_max / n_count)
    n_radius = numpy.sqrt(n_size) / 480.
    f_size = font_size_max * numpy.sqrt(n_size / node_size_max)
    node_font_size_max = f_size * 0.9
    line_width = 2. / n_count
    edge_line_width = edge_line_width_max / n_count

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
        c = Circle(pos[node], radius = n_radius, alpha = 0.)
        ax.add_patch(c)
        graph.node[node]['patch'] = c

    # draw edges
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

def oldlayergraph(G, **kwargs):

    # create node stack (list with lists of nodes)
    layers = G.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node in G.nodes():
        count[G.node[node]['params']['layer']] += 1
    nodes = [range(count[layer]) for layer in layers]
    for node in G.nodes():
        layer_id = G.node[node]['params']['layer_id']
        layer_node_id = G.node[node]['params']['layer_sub_id']
        nodes[layer_id][layer_node_id] = node

    # (optional) sort nodes
    if kwargs['node_sort']:
        for layer, tgt_nodes in enumerate(nodes):
            if layer == 0: continue
            sort = []
            for tgt_id, tgt_node in enumerate(tgt_nodes):
                sort_order = 0.
                for src_id, src_node in enumerate(nodes[layer - 1]):
                    if (src_node, tgt_node) in G.edges():
                        weight = G.edge[src_node][tgt_node]['weight']
                    elif (tgt_node, src_node) in G.edges():
                        weight = G.edge[tgt_node][src_node]['weight']
                    else: weight = 0.
                    sort_order += float(src_id) * numpy.abs(weight)
                sort.append((sort_order, tgt_node))
            nodes[layer] = [src_node[1] for src_node in \
                sorted(sort, key = lambda x: x[0])]

    # calculate sizes
    n_len = max([len(layer) for layer in nodes])
    l_len = len(nodes)
    scale = min(240. / n_len, 150. / l_len, 35.)
    graph_node_size = 0.9 * scale ** 2
    graph_node_radius = numpy.sqrt(graph_node_size) / 480.
    graph_font_size = 0.4 * scale
    graph_caption_pos = -0.0025 * scale
    graph_line_width = 0.3

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

    # create figure and axis objects
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.autoscale()

    # draw labeled nodes
    for layer in nodes:
        for node in layer:
            attr = G.node[node]
            type = attr['params']['layer']
            typeid = attr['params']['layer_id']
            is_visible = attr['params']['visible']
            label_str = attr['params']['label'] if is_visible \
                else 'n%d' % (layer.index(node) + 1)
            label = nemoa.common.str_format_unit_label(label_str)

            color = {
                True: {
                    'bg': COLOR['cornflower'],
                    'font': COLOR['black'],
                    'border': COLOR['black'] },
                False: {
                    'bg': COLOR['lightgrey2'],
                    'font': COLOR['black'],
                    'border': COLOR['lightgrey3'] }
            }[is_visible]

            # draw node
            node_obj = networkx.draw_networkx_nodes(G, pos,
                node_size = graph_node_size,
                linewidths = graph_line_width,
                nodelist = [node],
                node_shape = 'o',
                node_color = color['bg'])

            node_obj.set_edgecolor(color['border'])

            # draw node label
            node_font_size = \
                2. * graph_font_size / numpy.sqrt(max(len(node) - 1, 1))

            networkx.draw_networkx_labels(G, pos,
                font_size = node_font_size,
                labels = {node: label},
                font_weight = 'normal' if not is_visible else 'bold',
                font_color = color['font'])

            # draw node caption
            if kwargs['node_caption'] and is_visible:
                if not 'caption' in G.node[node]: continue
                networkx.draw_networkx_labels(G, pos_cap,
                    font_size = 0.75 * graph_font_size,
                    labels = {node: G.node[node]['caption']},
                    font_weight = 'normal')

    # draw edges
    for (v, h) in G.edges():

        # get weight
        weight = G.edge[v][h]['weight']

        # get edge color and line width (from weight)
        if kwargs['edge_weight'] == 'adjacency':
            color = 'black'
            edge_line_width \
                = 1.5 * graph_line_width * kwargs['edge_scale']
        else:
            color = 'green' if weight > 0. else 'red'
            edge_line_width \
                = 1.5 * weight * graph_line_width * kwargs['edge_scale']

        # draw edges
        networkx.draw_networkx_edges(G, pos,
            width = edge_line_width,
            edgelist = [(v, h)],
            edge_color = color,
            arrows = False,
            alpha = 1.)

        # (optional) draw edge labels
        if kwargs['edge_caption']:
            if 'caption' in G.edge[v][h]:
                networkx.draw_networkx_edge_labels(G, pos,
                    edge_labels = {(v, h): G.edge[v][h]['caption']},
                    font_color = color,
                    clip_on = False,
                    font_size = graph_font_size / 1.5,
                    font_weight = 'normal')

    # draw graph caption
    if kwargs['graph_caption'] and 'caption' in G.graph:
        matplotlib.pyplot.figtext(.5, .11,
            G.graph['caption'], fontsize = 9., ha = 'center')

    return True

def layergraph(graph, edge_curvature = 1.0, **kwargs):

    node_size_max = 800.     # maximum node size
    node_size_scale = 1.85   # node size scale factor
    font_size_max = 18.      # maximum font size
    edge_line_width_max = 4. # maximum edge line with
    edge_arr_scale = 8.      # edge arrow size scale factor
    #curvature = 0.45         # edge curvature for fancy edges

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
        for layer, tgt_nodes in enumerate(nodes):
            if layer == 0: continue
            sort = []
            for tgt_id, tgt_node in enumerate(tgt_nodes):
                sort_order = 0.
                for src_id, src_node in enumerate(nodes[layer - 1]):
                    if (src_node, tgt_node) in graph.edges():
                        weight = graph.edge[src_node][tgt_node]['weight']
                    elif (tgt_node, src_node) in graph.edges():
                        weight = graph.edge[tgt_node][src_node]['weight']
                    else: weight = 0.
                    sort_order += float(src_id) * numpy.abs(weight)
                sort.append((sort_order, tgt_node))
            nodes[layer] = [src_node[1] for src_node in \
                sorted(sort, key = lambda x: x[0])]

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
            label = nemoa.common.str_format_unit_label(label_str)

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
            backcolor = color['bg'] # COLOR[attr['color']]
            facecolor = color['font'] #COLOR['black']

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
            c = Circle(pos[node], radius = n_radius, alpha = 0.)
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




