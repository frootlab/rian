# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

#import matplotlib
#import nemoa
#import networkx
#import numpy

def color(*args):
    """Convert color name of XKCD color name survey to RGBA tuple.

    Args:
        List of color names. If the list is empty, a full list of
        available color names is returned. Otherwise the first valid
        color in the list is returned as RGBA tuple. If no color is
        valid None is returned.

    """

    import matplotlib.colors

    if len(args) == 0:
        clist = matplotlib.colors.get_named_colors_mapping().keys()
        return sorted([cname[5:].title() \
            for cname in clist if cname[:5] == 'xkcd:'])

    if args[0] == 'alpha': return (0., 0., 0., 0.)

    rgba = None
    for cname in args:
        try:
            rgba = matplotlib.colors.to_rgba('xkcd:%s' % cname)
            break
        except ValueError:
            continue
    return rgba

def heatmap(array, **kwargs):

    import matplotlib.pyplot as plt
    import matplotlib.cm
    import nemoa.common.text
    import numpy

    # create figure object
    fig = plt.figure()
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
    plt.xticks(
        numpy.arange(len(x_labels)) + 0.5,
        tuple(x_labels), fontsize = fontsize, rotation = 65)
    plt.yticks(
        len(y_labels) - numpy.arange(len(y_labels)) - 0.5,
        tuple(y_labels), fontsize = fontsize)

    # create colorbar
    cbar = fig.colorbar(cax)
    for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

    return True

def histogram(array, **kwargs):

    import matplotlib.pyplot as plt

    # create figure object
    fig = plt.figure()
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

    import matplotlib.pyplot as plt
    import matplotlib.patches
    import networkx
    import numpy

    node_size_max = 800.     # maximum node size
    node_size_scale = 1.85   # node size scale factor
    font_size_max = 18.      # maximum font size
    edge_size_scale = 4.     # edge size scale factor
    edge_arr_scale = 8.      # edge arrow size scale factor
    edge_radius = 0.15       # edge radius for fancy edges

    # create figure object
    fig = plt.figure()
    fig.patch.set_facecolor(kwargs['bg_color'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    plt.axes().set_aspect('equal', 'box')

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

def layergraph(graph,
        graph_layout       = 'multilayer',
        show_legend        = False,
        legend_fontsize    = 9.0,
        title              = None,
        show_title         = False,
        title_fontsize     = 16.,
        direction          = 'right',
        figure_padding     = (0.1, 0.1, 0.1, 0.1),
        figure_size        = (6.4, 4.8),
        dpi                = None,
        bg_color           = 'none',
        node_style         = 'o',
        edge_style         = '-|>',
        edge_arrow_scale   = 12.0,
        edge_width_enabled = True,
        edge_curvature     = 1.0,
        **kwargs):
    """Plot graph with layered layout.

    Args:
        graph: nemoa graph instance from nemoa network instance

    Kwargs:
        figure_size (tuple): # (11.69,8.27) for A4
                                            # (16.53,11.69) for A3
        edge_attribute (string): name of edge attribute, that
            determines the edge colors by its sign and the edge width
            by its absolute value.
            default: 'weight'
        edge_color (bool): flag for colored edges
            True: edge colors are determined by the sign of a given
                edge attribute defined by the keyword argument
                'edge_attribute'
            False: edges are black
        edge_poscolor (string): name of color for edges with
            positive signed attribute. For a full list of specified
            color names see nemoa.common.plot.color()
        edge_negcolor (string): name of color for edges with
            negative signed attribute. For a full list of specified
            color names see nemoa.common.plot.color()
        edge_curvature (float): value within the intervall [-1, 1],
            that determines the curvature of the edges.
            Thereby 1 equals max convexity and -1 max concavity.
        direction (string): string within the list ['up', 'down',
            'left', 'right'], that dermines the plot direction of the
            graph. 'up' means, the first layer is at the bottom.
        edge_style (string):  '-', '<-', '<->', '->',
            '<|-', '<|-|>', '-|>', '|-', '|-|', '-|',
            ']-', ']-[', '-[', 'fancy', 'simple', 'wedge'

    Returns:
        Boolen value which is True if no error occured.

    """

    try: import numpy
    except ImportError: raise ImportError(
        "layergraph() requires numpy: https://scipy.org/")
    try: import networkx as nx
    except ImportError: raise ImportError(
        "layergraph() requires networkx: https://networkx.github.io/")
    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except ImportError: raise ImportError(
        "layergraph() requires matplotlib: https://matplotlib.org/")
    import nemoa.common.graph as nmgraph
    import nemoa.common.text as nmtext
    import nemoa.common.dict as nmdict

    # create figure object
    fig = plt.figure(figsize = figure_size, dpi = dpi)
    fig.patch.set_facecolor(bg_color)
    figsize = fig.get_size_inches() * fig.dpi
    ax = fig.add_subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xlim(0., figsize[0])
    ax.set_ylim(0., figsize[1])
    ax.set_aspect('equal', 'box')
    ax.axis('off')

    # get node positions
    layout_params = nmdict.section(kwargs, 'graph_layout_')
    pos = nmgraph.nx_get_layout(graph, layout = graph_layout,
        scale = figsize, padding = figure_padding, **layout_params)

    # get normal sizes with respect to node positions
    sizes       = nmgraph.nx_get_normsizes(pos)
    node_size   = sizes.get('node_size', None)
    node_radius = sizes.get('node_radius', None)
    line_width  = sizes.get('line_width', None)
    edge_width  = sizes.get('edge_width', None)
    font_size   = sizes.get('font_size', None)

    # get nodes and groups
    groups = nmgraph.nx_get_groups(graph, attribute = 'group')

    # draw nodes, labeled by groups
    for group in sorted(groups.keys()):
        gnodes = groups.get(group)
        if len(gnodes) == 0: continue
        refnode = graph.node.get(gnodes[0])

        # draw nodes in group
        node_obj = nx.draw_networkx_nodes(graph, pos,
            nodelist   = gnodes,
            linewidths = line_width,
            node_size  = node_size,
            node_shape = node_style,
            node_color = color(refnode.get('color'), 'white'),
            label      = refnode.get('group', str(group)))
        node_obj.set_edgecolor(
            color(refnode.get('border_color'), 'black'))

    # draw node labels
    for node, data in graph.nodes(data = True):

        # determine label, fontsize and color
        node_label = data.get('label', str(node).title())
        node_label_format = nmtext.labelfomat(node_label)
        node_label_size = len(node_label.rstrip('1234567890'))
        font_color = color(data.get('font_color'), 'black')

        # draw node label
        nx.draw_networkx_labels(graph, pos,
            labels      = {node: node_label_format},
            font_size   = font_size / node_label_size,
            font_color  = font_color,
            font_family = 'sans-serif',
            font_weight = 'normal')

        # patch node for edges
        circle = matplotlib.patches.Circle(pos.get(node), alpha = 0.,
            radius = node_radius)
        ax.add_patch(circle)
        graph.node[node]['patch'] = circle

    # draw edges
    seen = {}
    for u, v, data in graph.edges(data = True):
        weight = data.get('weight', 1.0)

        # calculate edge curvature from node positions
        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * .2)
        elif direction in ['top', 'down']:
            rad = 2.0 * edge_curvature \
                * (pos[u][1] - pos[v][1]) * (pos[u][0] - pos[v][0]) \
                / figsize[0] / figsize[1]
        elif direction in ['right', 'left']:
            rad = -2.0 * edge_curvature \
                * (pos[u][1] - pos[v][1]) * (pos[u][0] - pos[v][0]) \
                / figsize[0] / figsize[1]
        else: rad = .0
        seen[(u, v)] = rad

        # calculate line width and alpha value from edge weight
        if not edge_width_enabled: linewidth = edge_width
        else: linewidth = numpy.absolute(weight) * edge_width
        alpha = numpy.amin([numpy.absolute(weight), 1.0])

        # draw edge
        nodeA = graph.node[u]['patch']
        nodeB = graph.node[v]['patch']
        arrow = matplotlib.patches.FancyArrowPatch(
            posA            = nodeA.center,
            posB            = nodeB.center,
            patchA          = nodeA,
            patchB          = nodeB,
            arrowstyle      = edge_style,
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = linewidth * edge_arrow_scale,
            linewidth       = linewidth,
            color           = color(data.get('color'), 'black'),
            alpha           = alpha )
        ax.add_patch(arrow)

    # (optional) draw legend
    if show_legend:
        ax.legend(
            numpoints      = 1,
            loc            = 'lower left',
            ncol           = 4,
            borderaxespad  = 0.,
            bbox_to_anchor = (0., -0.1),
            fontsize       = legend_fontsize,
            markerscale    = 0.6 * legend_fontsize / font_size)

    # (optional) draw title
    if show_title:
        if title == None: title = 'Unknown'
        plt.title(title, fontsize = title_fontsize)

    return True
