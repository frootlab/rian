# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def get_color(*args):
    """Convert color name of XKCD color name survey to RGBA tuple.

    Args:
        List of color names. If the list is empty, a full list of
        available color names is returned. Otherwise the first valid
        color in the list is returned as RGBA tuple. If no color is
        valid None is returned.

    """

    try: import matplotlib.colors as colors
    except ImportError: raise ImportError(
        "nemoa.common.plot.get_color() requires matplotlib: "
        "https://matplotlib.org")

    if len(args) == 0:
        clist = list(colors.get_named_colors_mapping().keys())
        return sorted([cname[5:].title() \
            for cname in clist if cname[:5] == 'xkcd:'])

    rgb = None
    for cname in args:
        try:
            rgb = colors.to_rgb('xkcd:%s' % cname)
            break
        except ValueError:
            continue
    return rgb

def get_label(string):
    """Return formated node label as used for plots."""

    lstr = string.rstrip('1234567890')
    if len(lstr) == len(string): return '${%s}$' % (string)
    rnum = int(string[len(lstr):])
    lstr = lstr.strip('_')
    return '${%s}_{%i}$' % (lstr, rnum)

def get_label_width(string):
    """Return estimated width for formated node labels."""

    lstr = string.rstrip('1234567890')
    if len(lstr) == len(string): return len(string)
    lstr = lstr.strip('_')
    rstr = str(int(string[len(lstr):]))
    return len(lstr) + 0.7 * len(rstr)

def filetypes():

    try: import matplotlib.pyplot as plt
    except ImportError: raise ImportError(
        "nemoa.common.plot.filetypes() requires matplotlib: "
        "https://matplotlib.org")

    return plt.gcf().canvas.get_supported_filetypes()

def heatmap(array,
    title          = None,
    show_title     = True,
    title_fontsize = None,
    interpolation  = None,
    **kwargs):

    try: import matplotlib.pyplot as plt
    except ImportError: raise ImportError(
        "nemoa.common.plot.filetypes() requires matplotlib: "
        "https://matplotlib.org")

    import matplotlib.cm
    import nemoa.common.text
    import numpy as np

    # create figure object
    fig = plt.gcf()
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create heatmap
    cax = ax.imshow(array, cmap = matplotlib.cm.hot_r,
        interpolation = interpolation,
        extent = (0, array.shape[1], 0, array.shape[0]))

    # create labels for axis
    max_font_size = 12.
    y_labels = []
    for label in kwargs['units'][0]:
        if ':' in label: label = label.split(':', 1)[1]
        y_labels.append(get_label(label))
    x_labels = []
    for label in kwargs['units'][1]:
        if ':' in label: label = label.split(':', 1)[1]
        x_labels.append(get_label(label))
    fontsize = min(max_font_size, \
        400. / float(max(len(x_labels), len(y_labels))))
    plt.xticks(
        np.arange(len(x_labels)) + 0.5,
        tuple(x_labels), fontsize = fontsize, rotation = 65)
    plt.yticks(
        len(y_labels) - np.arange(len(y_labels)) - 0.5,
        tuple(y_labels), fontsize = fontsize)

    # create colorbar
    cbar = fig.colorbar(cax)
    for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

    # (optional) draw title
    if show_title:
        if title == None: title = 'Unknown'
        plt.title(title, fontsize = title_fontsize)

    return True

def histogram(array,
    title          = None,
    show_title     = True,
    title_fontsize = None,
    bins           = 100,
    facecolor      = 'none',
    histtype       = None,
    linewidth      = None,
    edgecolor      = None,
    **kwargs):

    try: import matplotlib.pyplot as plt
    except ImportError: raise ImportError(
        "nemoa.common.plot.filetypes() requires matplotlib: "
        "https://matplotlib.org")

    # create figure object
    fig = plt.gcf()
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create histogram
    cax = ax.hist(array, bins = bins,
        facecolor = facecolor, histtype = histtype,
        linewidth = linewidth, edgecolor = edgecolor)

    # (optional) plot title
    if show_title and isinstance(title, str):
        plt.title(title, fontsize = title_fontsize)

    return True

def graph(graph,
    padding            = (0.1, 0.1, 0.1, 0.1),
    show_title         = False,
    title              = None,
    title_fontsize     = 14.,
    show_legend        = False,
    legend_fontsize    = 9.0,
    graph_layout       = 'layer',
    node_style         = 'o',
    edge_width_enabled = True,
    edge_curvature     = 1.0,
    **kwargs):
    """Plot graph.

    Args:
        graph: networkx graph instance

    Kwargs:
        figure_size (tuple): figure size in inches
            (11.69,8.27) for A4, (16.53,11.69) for A3
        edge_attribute (string): name of edge attribute, that
            determines the edge colors by its sign and the edge width
            by its absolute value.
            default: 'weight'
        edge_color (bool): flag for colored edges
            True: edge colors are determined by the sign of the
                attribute 'weight'
            False: edges are black
        edge_poscolor (string): name of color for edges with
            positive signed attribute. For a full list of specified
            color names see nemoa.common.plot.get_color()
        edge_negcolor (string): name of color for edges with
            negative signed attribute. For a full list of specified
            color names see nemoa.common.plot.get_color()
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

    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except ImportError: raise ImportError(
        "nemoa.common.plot.graph() requires matplotlib: "
        "https://matplotlib.org")

    try: import numpy as np
    except ImportError: raise ImportError(
        "nemoa.common.plot.graph() requires numpy: "
        "https://scipy.org")

    try: import networkx as nx
    except ImportError: raise ImportError(
        "nemoa.common.plot.graph() requires networkx: "
        "https://networkx.github.io")

    import nemoa.common.graph as nmgraph
    import nemoa.common.dict as nmdict

    # close previous figures and create figure object
    fig = plt.gcf()
    ax = fig.add_subplot(111)
    ax.set_autoscale_on(False)
    figsize = fig.get_size_inches() * fig.dpi
    ax.set_xlim(0., figsize[0])
    ax.set_ylim(0., figsize[1])
    ax.set_aspect('equal', 'box')
    ax.axis('off')

    # get node positions and sizes
    layout_params = nmdict.section(kwargs, 'graph_')
    pos = nmgraph.get_layout(graph, layout = graph_layout,
        size = figsize, padding = padding, **layout_params)
    sizes       = nmgraph.get_layout_normsize(pos)
    node_size   = sizes.get('node_size', None)
    node_radius = sizes.get('node_radius', None)
    line_width  = sizes.get('line_width', None)
    edge_width  = sizes.get('edge_width', None)
    font_size   = sizes.get('font_size', None)

    # get nodes and groups sorted by node attribute group_id
    groups = nmgraph.get_groups(graph, attribute = 'group')
    sorted_groups = sorted(list(groups.keys()), key = \
        lambda g: 0 if not isinstance(g, list) or len(g) == 0 \
        else graph.node.get(g[0], {}).get('group_id', 0))

    # draw nodes, labeled by groups
    for group in sorted_groups:
        gnodes = groups.get(group, [])
        if len(gnodes) == 0: continue
        refnode = graph.node.get(gnodes[0])
        label = refnode.get('description') \
            or refnode.get('group') or str(group)

        # draw nodes in group
        node_obj = nx.draw_networkx_nodes(graph, pos,
            nodelist   = gnodes,
            linewidths = line_width,
            node_size  = node_size,
            node_shape = node_style,
            node_color = get_color(refnode.get('color'), 'white'),
            label      = label)
        node_obj.set_edgecolor(
            get_color(refnode.get('border_color'), 'black'))

    # draw node labels
    for node, data in graph.nodes(data = True):

        # determine label, fontsize and color
        node_label = data.get('label', str(node).title())
        node_label_format = get_label(node_label)
        node_label_size = np.sqrt(get_label_width(node_label))
        font_color = get_color(data.get('font_color'), 'black')

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
    if nmgraph.is_directed(graph): default_edge_style = '-|>'
    else: default_edge_style = '-'

    for (u, v, data) in graph.edges(data = True):
        weight = data.get('weight')
        if weight == 0.: continue

        # calculate edge curvature from node positions
        # parameter rad describes the height in the normalized triangle
        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(np.sign(rad)) * .2)
        else:
            scale = 1. / np.amax(np.array(figsize))
            vec = scale * (np.array(pos[v]) - np.array(pos[u]))
            rad = vec[0] * vec[1] / np.sqrt(2 * np.sum(vec ** 2))
            if graph_layout == 'layer':
                gdir = layout_params.get('direction', 'down')
                if gdir in ['left', 'right']: rad *= -1
        seen[(u, v)] = rad

        # determine style of edge from edge weight
        if weight == None:
            linestyle = '-'
            linewidth = 0.5 * edge_width
            alpha = 0.5
        elif not edge_width_enabled:
            linestyle = '-'
            linewidth = edge_width
            alpha = np.amin([np.absolute(weight), 1.0])
        else:
            linestyle = '-'
            linewidth = np.absolute(weight) * edge_width
            alpha = np.amin([np.absolute(weight), 1.0])

        # draw edge
        nodeA = graph.node[u]['patch']
        nodeB = graph.node[v]['patch']
        arrow = matplotlib.patches.FancyArrowPatch(
            posA            = nodeA.center,
            posB            = nodeB.center,
            patchA          = nodeA,
            patchB          = nodeB,
            arrowstyle      = default_edge_style,
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = linewidth * 12.,
            linewidth       = linewidth,
            linestyle       = linestyle,
            color           = get_color(data.get('color'), 'black'),
            alpha           = alpha )
        ax.add_patch(arrow)

    # (optional) draw legend
    if show_legend:
        num_groups = np.sum([1 for g in list(groups.values()) \
            if isinstance(g, list) and len(g) > 0])
        ax.legend(
            numpoints      = 1,
            loc            = 'lower center',
            ncol           = num_groups,
            borderaxespad  = 0.,
            framealpha     = 0.,
            bbox_to_anchor = (0.5, -0.1),
            fontsize       = legend_fontsize,
            markerscale    = 0.6 * legend_fontsize / font_size)

    # (optional) draw title
    if show_title:
        if title == None: title = 'Unknown'
        plt.title(title, fontsize = title_fontsize)

    return True
