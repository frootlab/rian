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

    import matplotlib.pyplot
    import matplotlib.cm
    import nemoa.common.text
    import numpy

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

    import matplotlib.pyplot

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

    import matplotlib.pyplot
    import matplotlib.patches
    import networkx
    import numpy

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
        graph_direction (string): string within the list ['up', 'down',
            'left', 'right'], that dermines the plot direction of the
            graph. 'up' means, the first layer is at the bottom.
        edge_style (string):  '-', '<-', '<->', '->',
            '<|-', '<|-|>', '-|>', '|-', '|-|', '-|',
            ']-', ']-[', '-[', 'fancy', 'simple', 'wedge'

    Returns:
        Boolen value which is True if no error occured.

    """

    import nemoa.common.dict
    import nemoa.common.text
    import nemoa.common.math
    import matplotlib.pyplot
    import matplotlib.patches
    import numpy
    import networkx

    # default settings
    kwargs = nemoa.common.dict.merge(kwargs, {
        'graph_direction':      'right',
        'figure_padding':       (0.1, 0.1, 0.1, 0.1),
        'figure_size':          (6.4, 4.8), # (11.69,8.27) for A4
                                            # (16.53,11.69) for A3
        'node_style':           'o',
        'node_groupby':         'visible',
        'node_groups': {
            True: {
                'label': 'Observable',
                'bg_color': 'marine blue',
                'font_color': 'white',
                'border_color': 'dark navy'},
            False: {
                'label': 'Latent',
                'bg_color': 'light grey',
                'font_color': 'dark grey',
                'border_color': 'grey'} },
        'node_sort':            True,
        'node_scale':           1.0,
        'node_fontsize':        16.0,
        'node_color':           True,
        'edge_style':           '-|>',
        'edge_attribute':       'weight',
        'edge_threshold':       0.75,
        'edge_scale':           1.0,
        'edge_arrow_scale':     12.0,
        'edge_width_enabled':   True,
        'edge_color':           False,
        'edge_poscolor':        'green',
        'edge_negcolor':        'red',
        'edge_curvature':       1.0 })

    # get dictionaries for nodes and edges
    nodes = {n: data for (n, data) in graph.nodes(data = True)}
    edges = {(u, v): data for (u, v, data) in graph.edges(data = True)}

    # group nodes
    groups = {None: []}
    attr = kwargs['node_groupby']
    for node, data in nodes.iteritems():
        if not isinstance(data, dict) \
            or not 'params' in data or not attr in data['params']:
            groups[None].append(node)
            continue
        if not data['params'][attr] in groups:
            groups[data['params'][attr]] = []
        groups[data['params'][attr]].append(node)

    # create node stack as list of lists
    layers = graph.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node, data in nodes.items():
        count[data['params']['layer']] += 1
    stack = [range(count[layer]) for layer in layers]
    for node, data in nodes.items():
        lid = data['params']['layer_id']
        nid = data['params']['layer_sub_id']
        stack[lid][nid] = node

    # sort node stack by attribute
    if bool(kwargs['node_sort']):
        attr = kwargs['edge_attribute']

        for lid, tgt in enumerate(stack[1:], 1):
            src  = stack[lid - 1]
            slen = len(src)
            tlen = len(tgt)

            # calculate cost matrix for positions
            # by sum of weighted distances

            cost = numpy.zeros((tlen, tlen))
            for sid, u in enumerate(src):
                for tid, v in enumerate(tgt):
                    data = edges.get((u, v))
                    if data == None: data = edges.get((v, u))
                    if not isinstance(data, dict): continue
                    val = data.get(attr)
                    if not isinstance(val, float): continue
                    absval = numpy.absolute(val)
                    if absval < kwargs['edge_threshold']: continue
                    weight = nemoa.common.math.softstep(absval)
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
            for n in range(tlen):
                cmax = numpy.amax(cost[psel][:, nsel], axis = 0)
                cmin = numpy.amin(cost[psel][:, nsel], axis = 0)
                diff = cmax ** 2 - cmin ** 2
                nid  = nsel[numpy.argmax(diff)]
                pid  = psel[numpy.argmin(cost[psel][:, nid])]
                sort[pid] = tgt[nid]
                nsel.remove(nid)
                psel.remove(pid)
            stack[lid] = sort

    # create figure object
    fig = matplotlib.pyplot.figure(figsize = kwargs['figure_size'])
    fig.patch.set_facecolor(kwargs['bg_color'])
    figsize = fig.get_size_inches() * fig.dpi
    ax = fig.add_subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xlim(0., figsize[0])
    ax.set_ylim(0., figsize[1])
    ax.set_aspect('equal', 'box')
    ax.axis('off')

    # calculate node positions for layered graph layout
    pos = {}
    assign  = {'right': 0, 'up': 1, 'left': 2, 'down': 3}
    align   = assign.get(kwargs['graph_direction'], 0)
    padding = kwargs['figure_padding']
    xscale  = 1. / (len(stack) - 1)
    yscale  = [1. / len(l) for l in stack]
    rotate  = lambda (x, y), i: \
        [(x, y), (y, x), (1. - x, y), (y, 1. - x)][i % 4]
    constr  = lambda (x, y), (u, r, d, l): \
        (l + x - x * l - x * r, d + y - y * u - y * d)
    resize  = lambda (x, y), (a, b): (x * a, y * b)
    for lid, layer in enumerate(stack):
        for nid, node in enumerate(layer):
            x = lid * xscale
            y = (nid + 0.5) * yscale[lid]
            pos[node] = resize(constr(rotate(
                (x, y), align), padding), figsize)

    # calculate minimal distance between nodes
    euclidd = lambda (a, b), (c, d): \
        numpy.sqrt((a - c) ** 2 + (b - d) ** 2)
    mindist = numpy.amin([euclidd(pos[u], pos[v]) \
        for u in pos for v in pos if not u == v])

    # calculate node size and radius from minimal distance
    scale = 1.6 * kwargs.get('node_scale', 1.0) * mindist
    node_size = 0.0558 * scale ** 2
    line_width = 0.0030 * scale
    fontsize = 0.0075 * scale * kwargs.get('node_fontsize', 16.0)
    nradius = 23 * (0.01 * scale - 0.2)

    # draw nodes
    for group in sorted(groups):
        if group == None: continue

        # get group layout
        layout = kwargs['node_groups'].get(group, {})
        if 'label' in layout: group_label = layout['label']
        elif isinstance(group, bool):
            group_label = str(kwargs['node_groupby']).title()
            if not group: group_label = 'not ' + group_label
        elif group == None: group_label = 'Unknown'
        else: group_label = str(group).title()
        if not 'bg_color' in layout: bg_color = color('white')
        else: bg_color = color(layout['bg_color'], 'white')
        if not 'font_color' in layout: font_color = color('black')
        else: font_color = color(layout['font_color'], 'black')
        if not 'border_color' in layout: border_color = color('black')
        else: border_color = color(layout['border_color'], 'black')
        nodes_in_group = groups[group]

        # draw nodes in group
        node_obj = networkx.draw_networkx_nodes(graph, pos,
            nodelist   = nodes_in_group,
            linewidths = line_width,
            node_size  = node_size,
            node_shape = kwargs['node_style'],
            node_color = bg_color,
            label      = group_label)
        node_obj.set_edgecolor(border_color)

        # draw node labels
        for node in nodes_in_group:

            # determine label and fontsize
            label_str = nodes[node]['params']['label']
            node_label = nemoa.common.text.labelfomat(label_str)
            node_font_size = fontsize / len(label_str.rstrip('1234567890'))
            # 2do

            # draw node label
            networkx.draw_networkx_labels(graph, pos,
                labels      = {node: node_label},
                font_size   = node_font_size,
                font_color  = font_color,
                font_weight = 'normal')

            # patch node for edges
            c = matplotlib.patches.Circle(pos[node],
                radius = nradius, alpha = 0.)
            ax.add_patch(c)
            graph.node[node]['patch'] = c

    # draw edges
    seen = {}
    attr = kwargs['edge_attribute']
    val = 1.
    weight = 1.
    for (u, v) in edges.keys():

        # get value of edge attribute
        if bool(attr):
            data = edges.get((u, v))
            if not isinstance(data, dict): continue
            val = data.get(attr)
            if not isinstance(val, float): continue
            absval = numpy.absolute(val)
            if absval < kwargs['edge_threshold']: continue
            weight = nemoa.common.math.softstep(absval)

        # calculate edge curvature from node positions
        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * .2)
        elif kwargs['graph_direction'] in ['top', 'down']:
            rad = 2.0 * kwargs['edge_curvature'] \
                * (pos[u][1] - pos[v][1]) * (pos[u][0] - pos[v][0]) \
                / figsize[0] / figsize[1]
        elif kwargs['graph_direction'] in ['right', 'left']:
            rad = -2.0 * kwargs['edge_curvature'] \
                * (pos[u][1] - pos[v][1]) * (pos[u][0] - pos[v][0]) \
                / figsize[0] / figsize[1]
        else: rad = .0
        seen[(u, v)] = rad

        # calculate edge width from edge attribute
        if not bool(kwargs['edge_width_enabled']):
            edge_width = line_width * 2.2 * kwargs['edge_scale']
        else:
            edge_width = weight * 2.2 \
                * line_width * kwargs['edge_scale']

        # calculate edge arrow scale from edge width
        edge_arrow_scale = kwargs['edge_arrow_scale'] * edge_width

        # get edge color from attribute
        if not bool(kwargs['edge_color']): edge_color = 'black'
        elif val > 0: edge_color = kwargs['edge_poscolor']
        else: edge_color = kwargs['edge_negcolor']

        # draw edge
        nodeA = graph.node[u]['patch']
        nodeB = graph.node[v]['patch']
        arrow = matplotlib.patches.FancyArrowPatch(
            posA            = nodeA.center,
            posB            = nodeB.center,
            patchA          = nodeA,
            patchB          = nodeB,
            arrowstyle      = kwargs['edge_style'],
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = edge_arrow_scale,
            linewidth       = edge_width,
            color           = color(edge_color, 'black'),
            alpha           = min(weight, 1.0))
        ax.add_patch(arrow)

    return True
