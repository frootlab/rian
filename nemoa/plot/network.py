# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Plot Graph."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import matplotlib.patches
import networkx as nx
import numpy as np
from flab.base import mapping
from nemoa.math import graph
from nemoa.plot import Plot
from flab.base.types import Any, OptBool, OptStr, OptTuple, FloatPair, Type

#
# Structural Types
#

DiGraph = nx.classes.digraph.DiGraph

#
# Graph2D Class
#

class Graph2D(Plot):

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

    def plot(self, G: DiGraph) -> None:
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
                color names see :meth:`~nemoa.plot.Plot.get_color`
            edge_negcolor (string): name of color for edges with
                negative signed attribute. For a full list of specified
                color names see :meth:`~nemoa.plot.Plot.get_color`
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
        layout_params = mapping.crop(self._config, 'graph_')
        del layout_params['layout']

        pos = graph.get_layout(
            G, layout=self._config['graph_layout'], size=figsize,
            padding=self._config['padding'], **layout_params)

        sizes = self.get_layout_normsize(pos)
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
                node_size=node_size,
                node_shape=self._config['node_style'],
                node_color=self.get_color(refnode['color'], 'white'),
                label=label)
            node_obj.set_edgecolor(
                self.get_color(refnode['border_color'], 'black'))

        # draw node labels
        for node, data in G.nodes(data=True):

            # determine label, fontsize and color
            node_label = data.get('label', str(node).title())
            node_label_format = self.get_texlabel(node_label)
            node_label_size = np.sqrt(self.get_texlabel_width(node_label))
            font_color = self.get_color(data['font_color'], 'black')

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
                color=self.get_color(data.get('color', 'black')), alpha=alpha)
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

    @classmethod
    def get_node_layout(cls, ntype: str) -> dict:
        """Get plot layout for node type.

        Args:
            ntype: Name of node type. Accepted values are:
                'observable', 'latent', 'source', 'target', 'isolated'

        """
        # named layouts
        layouts = {
            'dark blue': {
                'color': 'marine blue', 'font_color': 'white',
                'border_color': 'dark navy'},
            'light grey': {
                'color': 'light grey', 'font_color': 'dark grey',
                'border_color': 'grey'},
            'dark grey': {
                'color': 'dark grey', 'font_color': 'white',
                'border_color': 'black'}}

        # named node types
        types = {
            'observable': {
                'description': 'Observable', 'groupid': 0,
                'layout': 'dark blue'},
            'source': {
                'description': 'Source', 'groupid': 1,
                'layout': 'dark blue'},
            'latent': {
                'description': 'Latent', 'groupid': 2,
                'layout': 'light grey'},
            'target': {
                'description': 'Target', 'groupid': 3,
                'layout': 'dark grey'},
            'isolated': {
                'description': 'Isolated', 'groupid': 4,
                'layout': 'dark grey'}}

        t = types.get(ntype, {})
        layout = layouts.get(t.get('layout', None), {})
        layout['description'] = t.get('description', 'Unknown')
        layout['groupid'] = t.get('groupid', 'none')

        return layout

    @classmethod
    def get_layout_normsize(cls, pos: dict) -> dict:
        """Calculate normal sizes for given node positions.

        Args:
            pos:

        """
        # Calculate scaling normalization factor
        scale = cls.get_scaling_factor(pos)

        return {
            'node_size': 0.0558 * scale ** 2,
            'node_radius': 23. * (0.01 * scale - 0.2),
            'line_width': 0.0030 * scale,
            'edge_width': 0.0066 * scale,
            'font_size': 0.1200 * scale
        }

    @classmethod
    def get_scaling_factor(cls, pos: dict) -> float:
        """Calculate normalized scaling factor for given node positions.

        Args:
            pos: dictionary with node positions

        Return:
            float containing a normalized scaling factor

        """
        # calculate euclidean distances between node positions
        norm = lambda x: np.sqrt(np.sum(x ** 2))
        dist = lambda u, v: norm(np.array(pos[u]) - np.array(pos[v]))
        dl = []
        for i, u in enumerate(pos.keys()):
            for j, v in enumerate(list(pos.keys())[i + 1:], i + 1):
                dl.append(dist(u, v))
        da = np.array(dl)

        # calculate maximal scaling factor for non overlapping nodes
        # by minimal euklidean distance between node positions
        smax = 2.32 * np.amin(da)

        # calculate minimal scaling factor
        # by average euklidean distance between node positions
        smin = 0.20 * np.mean(da)

        # if some nodes are exceptional close
        # the overlapping of those nodes is not avoided
        scale = smin if smin > smax else smin * (2. - smin / smax)

        return scale

    @classmethod
    def get_layout(
            cls, G: DiGraph, layout: str = 'spring',
            size: OptTuple = None, padding: tuple = (0., 0., 0., 0.),
            rotate: float = 0.0, **kwds: Any) -> dict:
        """Calculate positions of nodes, depending on graph layout.

        Args:
            G: networkx graph instance
            layout: graph layout name. Default is "spring"
            size: size in pixel (x, y). Default is None, which means no rescale
            padding: padding in percentage in format (up, down, left, right)
                Default is (0., 0., 0., 0.), which means no padding
            rotate: Rotation Angle in degrees. Default is 0.0,
                which means no rotation

        Return:
            dictionary containing node positions for graph layout

        Todo:
            * allow layouts from pygraphviz_layout
            * determine layout by graph type if layout is None

        """
        if layout == 'layer':
            pos = cls.get_layer_layout(G, **kwds)
        elif layout + '_layout' in nx.drawing.layout.__all__:
            pos = getattr(nx.drawing.layout, layout + '_layout')(G, **kwds)
        else:
            raise ValueError(f"layout '{layout}' is not supported")

        # rescale node positions to given figure size, padding and rotation angle
        pos = cls.rescale_layout(pos, size=size, padding=padding, rotate=rotate)

        return pos

    @classmethod
    def get_layer_layout(
            cls, G: DiGraph, direction: str = 'right',
            minimize: str = 'weight') -> dict:
        """Calculate node positions for layer layout.

        Args:
            G: networkx graph instance
            direction:
            minimize:

        Return:

        """
        def _orientate(p: FloatPair, d: str) -> FloatPair:
            """Oriantate node positions."""
            if d == 'right':
                return (p[0], p[1])
            if d == 'up':
                return (p[1], p[0])
            if d == 'left':
                return (1. - p[0], p[1])
            if d == 'down':
                return (p[1], 1. - p[0])
            return (p[0], p[1])

        if not graph.is_layered(G):
            raise ValueError("graph is not layered")

        if not G:
            return {}
        if len(G) == 1:
            return {G.nodes()[0]: (.5, .5)}

        # get list of node lists, sorted by layer (list of lists)
        stack = graph.get_layers(G)

        # sort node stack to minimize the euclidean distances
        # of connected nodes
        if isinstance(minimize, str):
            edges = {(u, v): data for (u, v, data) in G.edges(data=True)}

            for lid, tgt in enumerate(stack[1:], 1):
                src = stack[lid - 1]
                slen = len(src)
                tlen = len(tgt)

                # calculate cost matrix for positions by weights
                cost = np.zeros((tlen, tlen))
                for sid, u in enumerate(src):
                    for tid, v in enumerate(tgt):
                        data = edges.get((u, v))
                        if data is None:
                            data = edges.get((v, u))
                        if not isinstance(data, dict):
                            continue
                        value = data.get(minimize)
                        if not isinstance(value, float):
                            continue
                        weight = np.absolute(value)
                        for pid in range(tlen):
                            dist = np.absolute(
                                (pid + .5) / (tlen + 1.) \
                                - (sid + .5) / (slen + 1.))
                            cost[pid, tid] += dist * weight

                # choose (node, position) pair with maximum savings
                # thereby penalize large distances by power two
                # repeat until all nodes have positions
                nsel = list(range(tlen)) # node select list
                psel = list(range(tlen)) # position select list
                sort = [None] * tlen
                for i in range(tlen):
                    cmax = np.amax(cost[psel][:, nsel], axis=0)
                    cmin = np.amin(cost[psel][:, nsel], axis=0)
                    diff = cmax ** 2 - cmin ** 2
                    nid = nsel[np.argmax(diff)]
                    pid = psel[np.argmin(cost[psel][:, nid])]
                    sort[pid] = tgt[nid]
                    nsel.remove(nid)
                    psel.remove(pid)
                stack[lid] = sort

        # calculate node positions in box [0, 1] x [0, 1]
        pos = {}
        for l, layer in enumerate(stack):
            for n, node in enumerate(layer):
                x = float(l) / (len(stack) - 1)
                y = (float(n) + .5) / len(layer)
                pos[node] = _orientate((x, y), direction)

        return pos

    @classmethod
    def rescale_layout(
            cls, pos: dict, size: OptTuple = None,
            padding: tuple = (0., 0., 0., 0.), rotate: float = 0.) -> dict:
        """Rescale node positions.

        Args:
            pos: dictionary with node positions
            size: size in pixel (x, y). Default is None, which means no rescale
            padding: padding in percentage in format (up, down, left, right).
                Default is (0., 0., 0., 0.), which means no padding
            rotate: Rotation Angle in degrees. Default is 0.0, which means no
                rotation

        Return:
            dictionary containing rescaled node positions.

        """
        # create numpy array with positions
        a = np.array([(x, y) for x, y in list(pos.values())])

        # rotate positions around its center by a given rotation angle
        if bool(rotate):
            theta = np.radians(rotate)
            cos, sin = np.cos(theta), np.sin(theta)
            R = np.array([[cos, -sin], [sin, cos]])
            mean = a.mean(axis=0)
            a = np.dot(a - mean, R.T) + mean

        # rescale positions with padding
        if size:
            dmin, dmax = np.amin(a, axis=0), np.amax(a, axis=0)
            u, r, d, l = padding
            pmin, pmax = np.array([l, d]), 1. - np.array([r, u])
            a = (pmax - pmin) * (a - dmin) / (dmax - dmin) + pmin
            a = np.array(size) * a

        pos = {node: tuple(a[i]) for i, node in enumerate(pos.keys())}

        return pos
