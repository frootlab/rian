# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

class Plot:
    """Base class for matplotlib plots.

    Export classes like Histogram, Heatmap or Graph share a common
    interface to matplotlib, as well as certain plotting attributes.
    This base class is intended to provide a unified interface to access
    matplotlib and those attributes.

    Attributes:

    """

    _default = {
        'fileformat': 'pdf',
        'figure_size': (10., 6.),
        'dpi': None,
        'bg_color': 'none',
        'usetex': False,
        'font_family': 'sans-serif',
        'style': 'seaborn-white',
        'title': None,
        'show_title': True,
        'title_fontsize': 14.0}

    _config = {}
    _plt = None
    _figure = None

    figure = None # 2do

    def __init__(self, *args, **kwargs):

        try: import matplotlib
        except ImportError: raise ImportError(
            "nemoa.common.plot.Plot() requires matplotlib: "
            "https://matplotlib.org")

        # merge config from defaults, current config and kwargs
        self._config = nemoa.common.dict.merge(
            kwargs, self._config, self._default)

        # update global matplotlib settings
        matplotlib.rc('text', usetex = \
            self._config.get('usetex'))
        matplotlib.rc('font', family = \
            self._config.get('font_family'))

        # link matplotlib.pyplot
        import matplotlib.pyplot as plt
        self._plt = plt

        # close previous figures
        plt.close('all')

        # update plot settings
        plt.style.use(self._config.get('style'))

        # create figure
        self._figure = plt.figure(
            figsize   = self._config.get('figure_size'),
            dpi       = self._config.get('dpi'),
            facecolor = self._config.get('bg_color'))

    def __del__(self):
        self._figure.clear()

    def set_default(self, default: dict = {}):
        """Set default values. """

        # merge self._config over defaults
        self._config = nemoa.common.dict.merge(self._config, default)

        return True

    def plot_title(self):
        if not self._config.get('show_title'):
            return False

        title = self._config.get('title') or 'Unknown'
        fontsize = self._config.get('title_fontsize')

        self._plt.title(title, fontsize = fontsize)
        return True

    def show(self):
        return self._plt.show()

    def save(self, path, *args, **kwargs):
        return self._figure.savefig(path,
            dpi = self._config.get('dpi'), **kwargs)

    def release(self):
        return self._figure.clear()

class Heatmap(Plot):

    _config = {
        'interpolation': 'nearest' }

    def plot(self, array):

        import matplotlib.cm
        import numpy

        # create subplot
        ax = self._figure.add_subplot(111)
        ax.grid(True)

        # create heatmap
        cax = ax.imshow(array, cmap = matplotlib.cm.hot_r,
            interpolation = self._config.get('interpolation'),
            extent = (0, array.shape[1], 0, array.shape[0]))

        # create labels for axis
        max_font_size = 12.
        x_labels = []
        for label in self._config['x_labels']:
            if ':' in label: label = label.split(':', 1)[1]
            x_labels.append(get_label(label))
        y_labels = []
        for label in self._config['y_labels']:
            if ':' in label: label = label.split(':', 1)[1]
            y_labels.append(get_label(label))
        fontsize = min(max_font_size, \
            400. / float(max(len(x_labels), len(y_labels))))
        self._plt.xticks(
            numpy.arange(len(x_labels)) + 0.5,
            tuple(x_labels), fontsize = fontsize, rotation = 65)
        self._plt.yticks(
            len(y_labels) - numpy.arange(len(y_labels)) - 0.5,
            tuple(y_labels), fontsize = fontsize)

        # create colorbar
        cbar = self._figure.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # (optional) plot title
        self.plot_title()

        return True

class Histogram(Plot):

    _config = {
        'bins': 100,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def plot(self, array):

        # create subplot
        ax = self._figure.add_subplot(111)
        ax.grid(True)

        # create histogram
        cax = ax.hist(array,
            bins      = self._config.get('bins'),
            facecolor = self._config.get('facecolor'),
            histtype  = self._config.get('histtype'),
            linewidth = self._config.get('linewidth'),
            edgecolor = self._config.get('edgecolor'))

        # (optional) plot title
        self.plot_title()

        return True

class Graph(Plot):

    _config = {
        'padding':            (0.1, 0.1, 0.1, 0.1),
        'show_legend':        False,
        'legend_fontsize':    9.0,
        'graph_layout':       'layer',
        'graph_direction':    'right',
        'node_style':         'o',
        'edge_width_enabled': True,
        'edge_curvature':     1.0}

    def plot(self, graph):
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
            "nemoa.common.plot.Graph.plot() requires matplotlib: "
            "https://matplotlib.org")

        try: import numpy as np
        except ImportError: raise ImportError(
            "nemoa.common.plot.Graph.plot() requires numpy: "
            "https://scipy.org")

        try: import networkx as nx
        except ImportError: raise ImportError(
            "nemoa.common.plot.Graph.plot() requires networkx: "
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
        layout_params = nmdict.section(self._config, 'graph_')
        del layout_params['layout']

        pos = nmgraph.get_layout(graph,
            layout  = self._config['graph_layout'],
            size    = figsize,
            padding = self._config['padding'],
            **layout_params)

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
                node_shape = self._config['node_style'],
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
                if self._config['graph_layout'] == 'layer':
                    gdir = self._config['graph_direction']
                    if gdir in ['left', 'right']: rad *= -1
            seen[(u, v)] = rad

            # determine style of edge from edge weight
            if weight == None:
                linestyle = '-'
                linewidth = 0.5 * edge_width
                alpha = 0.5
            elif not self._config['edge_width_enabled']:
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
        if self._config['show_legend']:
            num_groups = np.sum([1 for g in list(groups.values()) \
                if isinstance(g, list) and len(g) > 0])
            markerscale = 0.6 * self._config['legend_fontsize'] / font_size
            ax.legend(
                numpoints      = 1,
                loc            = 'lower center',
                ncol           = num_groups,
                borderaxespad  = 0.,
                framealpha     = 0.,
                bbox_to_anchor = (0.5, -0.1),
                fontsize       = self._config['legend_fontsize'],
                markerscale    = markerscale)

        # (optional) plot title
        self.plot_title()

        return True

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

# def graph(graph,
#     padding            = (0.1, 0.1, 0.1, 0.1),
#     show_title         = False,
#     title              = None,
#     title_fontsize     = 14.,
#     show_legend        = False,
#     legend_fontsize    = 9.0,
#     graph_layout       = 'layer',
#     node_style         = 'o',
#     edge_width_enabled = True,
#     edge_curvature     = 1.0,
#     **kwargs):
#     """Plot graph.
#
#     Args:
#         graph: networkx graph instance
#
#     Kwargs:
#         figure_size (tuple): figure size in inches
#             (11.69,8.27) for A4, (16.53,11.69) for A3
#         edge_attribute (string): name of edge attribute, that
#             determines the edge colors by its sign and the edge width
#             by its absolute value.
#             default: 'weight'
#         edge_color (bool): flag for colored edges
#             True: edge colors are determined by the sign of the
#                 attribute 'weight'
#             False: edges are black
#         edge_poscolor (string): name of color for edges with
#             positive signed attribute. For a full list of specified
#             color names see nemoa.common.plot.get_color()
#         edge_negcolor (string): name of color for edges with
#             negative signed attribute. For a full list of specified
#             color names see nemoa.common.plot.get_color()
#         edge_curvature (float): value within the intervall [-1, 1],
#             that determines the curvature of the edges.
#             Thereby 1 equals max convexity and -1 max concavity.
#         direction (string): string within the list ['up', 'down',
#             'left', 'right'], that dermines the plot direction of the
#             graph. 'up' means, the first layer is at the bottom.
#         edge_style (string):  '-', '<-', '<->', '->',
#             '<|-', '<|-|>', '-|>', '|-', '|-|', '-|',
#             ']-', ']-[', '-[', 'fancy', 'simple', 'wedge'
#
#     Returns:
#         Boolen value which is True if no error occured.
#
#     """
#
#     try:
#         import matplotlib
#         import matplotlib.pyplot as plt
#     except ImportError: raise ImportError(
#         "nemoa.common.plot.graph() requires matplotlib: "
#         "https://matplotlib.org")
#
#     try: import numpy as np
#     except ImportError: raise ImportError(
#         "nemoa.common.plot.graph() requires numpy: "
#         "https://scipy.org")
#
#     try: import networkx as nx
#     except ImportError: raise ImportError(
#         "nemoa.common.plot.graph() requires networkx: "
#         "https://networkx.github.io")
#
#     import nemoa.common.graph as nmgraph
#     import nemoa.common.dict as nmdict
#
#     # close previous figures and create figure object
#     fig = plt.gcf()
#     ax = fig.add_subplot(111)
#     ax.set_autoscale_on(False)
#     figsize = fig.get_size_inches() * fig.dpi
#     ax.set_xlim(0., figsize[0])
#     ax.set_ylim(0., figsize[1])
#     ax.set_aspect('equal', 'box')
#     ax.axis('off')
#
#     # get node positions and sizes
#     layout_params = nmdict.section(kwargs, 'graph_')
#     pos = nmgraph.get_layout(graph, layout = graph_layout,
#         size = figsize, padding = padding, **layout_params)
#     sizes       = nmgraph.get_layout_normsize(pos)
#     node_size   = sizes.get('node_size', None)
#     node_radius = sizes.get('node_radius', None)
#     line_width  = sizes.get('line_width', None)
#     edge_width  = sizes.get('edge_width', None)
#     font_size   = sizes.get('font_size', None)
#
#     # get nodes and groups sorted by node attribute group_id
#     groups = nmgraph.get_groups(graph, attribute = 'group')
#     sorted_groups = sorted(list(groups.keys()), key = \
#         lambda g: 0 if not isinstance(g, list) or len(g) == 0 \
#         else graph.node.get(g[0], {}).get('group_id', 0))
#
#     # draw nodes, labeled by groups
#     for group in sorted_groups:
#         gnodes = groups.get(group, [])
#         if len(gnodes) == 0: continue
#         refnode = graph.node.get(gnodes[0])
#         label = refnode.get('description') \
#             or refnode.get('group') or str(group)
#
#         # draw nodes in group
#         node_obj = nx.draw_networkx_nodes(graph, pos,
#             nodelist   = gnodes,
#             linewidths = line_width,
#             node_size  = node_size,
#             node_shape = node_style,
#             node_color = get_color(refnode.get('color'), 'white'),
#             label      = label)
#         node_obj.set_edgecolor(
#             get_color(refnode.get('border_color'), 'black'))
#
#     # draw node labels
#     for node, data in graph.nodes(data = True):
#
#         # determine label, fontsize and color
#         node_label = data.get('label', str(node).title())
#         node_label_format = get_label(node_label)
#         node_label_size = np.sqrt(get_label_width(node_label))
#         font_color = get_color(data.get('font_color'), 'black')
#
#         # draw node label
#         nx.draw_networkx_labels(graph, pos,
#             labels      = {node: node_label_format},
#             font_size   = font_size / node_label_size,
#             font_color  = font_color,
#             font_family = 'sans-serif',
#             font_weight = 'normal')
#
#         # patch node for edges
#         circle = matplotlib.patches.Circle(pos.get(node), alpha = 0.,
#             radius = node_radius)
#         ax.add_patch(circle)
#         graph.node[node]['patch'] = circle
#
#     # draw edges
#     seen = {}
#     if nmgraph.is_directed(graph): default_edge_style = '-|>'
#     else: default_edge_style = '-'
#
#     for (u, v, data) in graph.edges(data = True):
#         weight = data.get('weight')
#         if weight == 0.: continue
#
#         # calculate edge curvature from node positions
#         # parameter rad describes the height in the normalized triangle
#         if (u, v) in seen:
#             rad = seen.get((u, v))
#             rad = -(rad + float(np.sign(rad)) * .2)
#         else:
#             scale = 1. / np.amax(np.array(figsize))
#             vec = scale * (np.array(pos[v]) - np.array(pos[u]))
#             rad = vec[0] * vec[1] / np.sqrt(2 * np.sum(vec ** 2))
#             if graph_layout == 'layer':
#                 gdir = layout_params.get('direction', 'down')
#                 if gdir in ['left', 'right']: rad *= -1
#         seen[(u, v)] = rad
#
#         # determine style of edge from edge weight
#         if weight == None:
#             linestyle = '-'
#             linewidth = 0.5 * edge_width
#             alpha = 0.5
#         elif not edge_width_enabled:
#             linestyle = '-'
#             linewidth = edge_width
#             alpha = np.amin([np.absolute(weight), 1.0])
#         else:
#             linestyle = '-'
#             linewidth = np.absolute(weight) * edge_width
#             alpha = np.amin([np.absolute(weight), 1.0])
#
#         # draw edge
#         nodeA = graph.node[u]['patch']
#         nodeB = graph.node[v]['patch']
#         arrow = matplotlib.patches.FancyArrowPatch(
#             posA            = nodeA.center,
#             posB            = nodeB.center,
#             patchA          = nodeA,
#             patchB          = nodeB,
#             arrowstyle      = default_edge_style,
#             connectionstyle = 'arc3,rad=%s' % rad,
#             mutation_scale  = linewidth * 12.,
#             linewidth       = linewidth,
#             linestyle       = linestyle,
#             color           = get_color(data.get('color'), 'black'),
#             alpha           = alpha )
#         ax.add_patch(arrow)
#
#     # (optional) draw legend
#     if show_legend:
#         num_groups = np.sum([1 for g in list(groups.values()) \
#             if isinstance(g, list) and len(g) > 0])
#         ax.legend(
#             numpoints      = 1,
#             loc            = 'lower center',
#             ncol           = num_groups,
#             borderaxespad  = 0.,
#             framealpha     = 0.,
#             bbox_to_anchor = (0.5, -0.1),
#             fontsize       = legend_fontsize,
#             markerscale    = 0.6 * legend_fontsize / font_size)
#
#     # (optional) draw title
#     if show_title:
#         if title == None: title = 'Unknown'
#         plt.title(title, fontsize = title_fontsize)
#
#     return True
