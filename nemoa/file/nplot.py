# -*- coding: utf-8 -*-
"""Common function for creating plots with matplotlib."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import numpy as np
from nemoa.types import OptDict

class Plot:
    """Base class for matplotlib plots.

    Export classes like Histogram, Heatmap or Graph share a common
    interface to matplotlib, as well as certain plotting attributes.
    This base class is intended to provide a unified interface to access
    matplotlib and those attributes.

    Attributes:

    """

    _default: dict = {
        'fileformat': 'pdf',
        'figure_size': (10.0, 6.0),
        'dpi': None,
        'bg_color': 'none',
        'usetex': False,
        'font_family': 'sans-serif',
        'style': 'seaborn-white',
        'title': None,
        'show_title': True,
        'title_fontsize': 14.0
    }

    _config: dict = {}
    _kwds: dict = {}

    _plt = None
    _fig = None
    _axes = None

    def __init__(self, **kwds):
        """ """
        try:
            import matplotlib
        except ImportError as err:
            raise ImportError(
                "requires package matplotlib: "
                "https://matplotlib.org") from err

        # merge config from defaults, current config and keyword arguments
        self._kwds = kwds
        self._config = {**self._default, **self._config, **kwds}

        # update global matplotlib settings
        matplotlib.rc('text', usetex=self._config['usetex'])
        matplotlib.rc('font', family=self._config['font_family'])

        # link matplotlib.pyplot
        import matplotlib.pyplot as plt
        self._plt = plt

        # close previous figures
        plt.close('all')

        # update plot settings
        plt.style.use(self._config['style'])

        # create figure
        self._fig = plt.figure(
            figsize=self._config['figure_size'],
            dpi=self._config['dpi'],
            facecolor=self._config['bg_color'])

        # create subplot (matplotlib.axes.Axes)
        self._axes = self._fig.add_subplot(111)

    def set_default(self, config: OptDict = None) -> bool:
        """Set default values."""
        self._config = {**self._config, **(config or {}), **self._kwds}

        return True

    def plot_title(self) -> bool:
        """Plot title."""
        if not self._config['show_title']:
            return False

        title = self._config['title'] or 'Unknown'
        fontsize = self._config['title_fontsize']

        getattr(self._plt, 'title')(title, fontsize=fontsize)
        return True

    def show(self) -> None:
        """Show plot."""
        getattr(self._plt, 'show')()

    def save(self, path, **kwds):
        """Save plot to file."""
        return self._fig.savefig(path, dpi=self._config['dpi'], **kwds)

    def release(self):
        """Clear current plot."""
        return self._fig.clear()

class Heatmap(Plot):
    """ """

    _config = {
        'interpolation': 'nearest',
        'grid': True
    }

    def plot(self, array):
        """ """

        try:
            from matplotlib.cm import hot_r
        except ImportError as err:
            raise ImportError(
                "requires package matplotlib: "
                "https://matplotlib.org") from err

        # plot grid
        self._axes.grid(self._config['grid'])

        # plot heatmap
        cax = self._axes.imshow(
            array,
            cmap=hot_r,
            interpolation=self._config['interpolation'],
            extent=(0, array.shape[1], 0, array.shape[0]))

        # create labels for axis
        max_font_size = 12.
        x_labels = []
        for label in self._config['x_labels']:
            if ':' in label:
                label = label.split(':', 1)[1]
            x_labels.append(get_texlabel(label))
        y_labels = []
        for label in self._config['y_labels']:
            if ':' in label:
                label = label.split(':', 1)[1]
            y_labels.append(get_texlabel(label))
        fontsize = min(max_font_size, \
            400. / float(max(len(x_labels), len(y_labels))))
        self._plt.xticks(
            np.arange(len(x_labels)) + 0.5,
            tuple(x_labels), fontsize=fontsize, rotation=65)
        self._plt.yticks(
            len(y_labels) - np.arange(len(y_labels)) - 0.5,
            tuple(y_labels), fontsize=fontsize)

        # create colorbar
        cbar = self._fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # (optional) plot title
        self.plot_title()

        return True

class Histogram(Plot):
    """ """

    _config = {
        'bins': 100,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5,
        'grid': True
    }

    def plot(self, array):
        """ """

        # plot grid
        self._axes.grid(self._config['grid'])

        # plot histogram
        self._axes.hist(
            array,
            bins=self._config['bins'],
            facecolor=self._config['facecolor'],
            histtype=self._config['histtype'],
            linewidth=self._config['linewidth'],
            edgecolor=self._config['edgecolor'])

        # (optional) plot title
        self.plot_title()

        return True

class Scatter2D(Plot):
    """ """

    _config = {
        'grid': True,
        'pca': True
    }

    @staticmethod
    def _pca2d(array):
        """Calculate projection to largest two principal components."""
        # get dimension of array
        dim = array.shape[1]

        # calculate covariance matrix
        cov = np.cov(array.T)

        # calculate eigevectors and eigenvalues
        vals, vecs = np.linalg.eig(cov)

        # sort eigevectors by absolute eigenvalues
        pairs = [(np.abs(vals[i]), vecs[:, i]) for i in range(len(vals))]
        pairs.sort(key=lambda x: x[0], reverse=True)

        # calculate projection matrix
        proj = np.hstack(
            [pairs[0][1].reshape(dim, 1), pairs[1][1].reshape(dim, 1)])

        # calculate projection
        parray = np.dot(array, proj)

        return parray

    def plot(self, array):
        """ """

        # test arguments
        if array.shape[1] != 2:
            if self._config['pca']:
                array = self._pca2d(array)
            else: raise TypeError(
                "first argument is required to be an array of shape (n, 2)")

        x, y = array[:, 0], array[:, 1]

        # plot grid
        self._axes.grid(self._config['grid'])

        # plot scattered data
        self._axes.scatter(x, y)

        # (optional) plot title
        self.plot_title()

        return True

class Graph(Plot):

    _config = {
        'padding': (0.1, 0.1, 0.1, 0.1),
        'show_legend': False,
        'legend_fontsize': 9.0,
        'graph_layout': 'layer',
        'graph_direction': 'right',
        'node_style': 'o',
        'edge_width_enabled': True,
        'edge_curvature': 1.0
    }

    def plot(self, G):
        """Plot graph.

        Args:
            G: networkx graph instance
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
                color names see nemoa.base.nplot.get_color()
            edge_negcolor (string): name of color for edges with
                negative signed attribute. For a full list of specified
                color names see nemoa.base.nplot.get_color()
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
            import matplotlib.patches
        except ImportError as err:
            raise ImportError(
                "requires package matplotlib: "
                "https://matplotlib.org") from err

        try:
            import networkx as nx
        except ImportError as err:
            raise ImportError(
                "requires package networkx: "
                "https://networkx.github.io") from err

        from nemoa.base import ndict
        from nemoa.math import graph

        # adjust size of subplot
        fig = self._fig
        ax = self._axes
        ax.set_autoscale_on(False)
        figsize = fig.get_size_inches() * fig.dpi
        ax.set_xlim(0., figsize[0])
        ax.set_ylim(0., figsize[1])
        ax.set_aspect('equal', 'box')
        ax.axis('off')

        # get node positions and sizes
        layout_params = ndict.crop(self._config, 'graph_')
        del layout_params['layout']

        pos = graph.get_layout(
            G, layout=self._config['graph_layout'], size=figsize,
            padding=self._config['padding'], **layout_params)

        sizes = graph.get_layout_normsize(pos)
        node_size = sizes.get('node_size', None)
        node_radius = sizes.get('node_radius', None)
        line_width = sizes.get('line_width', None)
        edge_width = sizes.get('edge_width', None)
        font_size = sizes.get('font_size', None)

        # get nodes and groups sorted by node attribute group_id
        groups = graph.get_groups(G, attribute='group')
        sorted_groups = sorted(
            list(groups.keys()),
            key=lambda g: 0 if not isinstance(g, list) or not g \
            else G.node.get(g[0], {}).get('group_id', 0))

        # draw nodes, labeled by groups
        for group in sorted_groups:
            gnodes = groups.get(group, [])
            if not gnodes:
                continue
            refnode = G.node.get(gnodes[0])
            label = refnode['description'] or refnode['group'] or str(group)

            # draw nodes in group
            node_obj = nx.draw_networkx_nodes(
                G, pos, nodelist=gnodes, linewidths=line_width,
                node_size=node_size, node_shape=self._config['node_style'],
                node_color=get_color(refnode['color'], 'white'), label=label)
            node_obj.set_edgecolor(
                get_color(refnode['border_color'], 'black'))

        # draw node labels
        for node, data in G.nodes(data=True):

            # determine label, fontsize and color
            node_label = data.get('label', str(node).title())
            node_label_format = get_texlabel(node_label)
            node_label_size = np.sqrt(get_texlabel_width(node_label))
            font_color = get_color(data['font_color'], 'black')

            # draw node label
            nx.draw_networkx_labels(
                G, pos, labels={node: node_label_format},
                font_size=font_size / node_label_size, font_color=font_color,
                font_family='sans-serif', font_weight='normal')

            # patch node for edges
            circle = matplotlib.patches.Circle(
                pos.get(node), alpha=0., radius=node_radius)
            ax.add_patch(circle)
            G.node[node]['patch'] = circle

        # draw edges
        seen = {}
        if graph.is_directed(G):
            default_edge_style = '-|>'
        else: default_edge_style = '-'

        for (u, v, data) in G.edges(data=True):
            weight = data['weight']
            if weight == 0.:
                continue

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
                    if gdir in ['left', 'right']:
                        rad *= -1
            seen[(u, v)] = rad

            # determine style of edge from edge weight
            if weight is None:
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
            node_a = G.node[u]['patch']
            node_b = G.node[v]['patch']
            arrow = matplotlib.patches.FancyArrowPatch(
                posA=node_a.center, posB=node_b.center,
                patchA=node_a, patchB=node_b,
                arrowstyle=default_edge_style,
                connectionstyle='arc3,rad=%s' % rad,
                mutation_scale=linewidth * 12.,
                linewidth=linewidth, linestyle=linestyle,
                color=get_color(data.get('color', 'black')), alpha=alpha)
            ax.add_patch(arrow)

        # (optional) draw legend
        if self._config['show_legend']:
            num_groups = np.sum([1 for g in list(groups.values()) \
                if isinstance(g, list) and g])
            markerscale = 0.6 * self._config['legend_fontsize'] / font_size
            ax.legend(
                numpoints=1,
                loc='lower center',
                ncol=num_groups,
                borderaxespad=0.,
                framealpha=0.,
                bbox_to_anchor=(0.5, -0.1),
                fontsize=self._config['legend_fontsize'],
                markerscale=markerscale)

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
    try:
        from matplotlib import colors
    except ImportError as err:
        raise ImportError(
            "requires package matplotlib: "
            "https://matplotlib.org") from err

    if not args:
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

def get_texlabel(string):
    """Return formated node label as used for plots."""
    lstr = string.rstrip('1234567890')
    if len(lstr) == len(string):
        return '${%s}$' % (string)
    rnum = int(string[len(lstr):])
    lstr = lstr.strip('_')
    return '${%s}_{%i}$' % (lstr, rnum)

def get_texlabel_width(string):
    """Return estimated width for formated node labels."""
    lstr = string.rstrip('1234567890')
    if len(lstr) == len(string):
        return len(string)
    lstr = lstr.strip('_')
    rstr = str(int(string[len(lstr):]))
    return len(lstr) + 0.7 * len(rstr)

def filetypes():
    """Return supported image filetypes."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise ImportError(
            "requires package matplotlib: "
            "https://matplotlib.org") from err

    return plt.gcf().canvas.get_supported_filetypes()
