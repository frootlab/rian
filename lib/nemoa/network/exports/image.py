# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import networkx
import os
import importlib
import matplotlib.pyplot

def filetypes():
    """Get supported image filetypes for network export."""
    return matplotlib.pyplot.gcf().canvas.get_supported_filetypes()

def show(network, plot = None, **kwargs):

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot network '%s':
            plot type '%s' is not supported.""" % (network.name, plot))

    # create plot of network
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('text', usetex = plot.settings['usetex'])
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(network):

        # output
        matplotlib.pyplot.show()

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return True

def save(network, path = None, filetype = None, plot = None, **kwargs):

    # test if filetype is supported by matplotlib
    if not filetype in filetypes():
        return nemoa.log('error', """could not create plot:
            filetype '%s' is not supported by matplotlib.""" %
            (filetype))

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot network '%s':
            plot type '%s' is not supported.""" % (network.name, plot))

    # create plot of network
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('text', usetex = plot.settings['usetex'])
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(network):

        # output
        matplotlib.pyplot.savefig(path, dpi = plot.settings['dpi'])

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return path

class Graph:

    settings = None
    default = {
        'fileformat': 'pdf',
        'dpi': None,
        'usetex': False,
        'show_title': False,
        'show_legend': False,
        'title': None,
        'graph_layout': 'multilayer',
        'graph_caption': 'accuracy',
        'bg_color': 'none',
        'direction': 'right',
        'node_caption': 'accuracy',
        'node_groupby': 'visible',
        'node_groups': {
            True: {
                'label': 'Observable Variables',
                'color': 'marine blue',
                'font_color': 'white',
                'border_color': 'dark navy'},
            False: {
                'label': 'Latent Variables',
                'color': 'light grey',
                'font_color': 'dark grey',
                'border_color': 'grey'} },
        'node_color': True,
        'edge_color': False,
        'edge_caption': None,
        'edge_weight': 'intensity',
        'edge_threshold': 0.0,
        'edge_transform': 'softstep',
        'edge_sign_normalize': True }

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def create(self, network):

        import nemoa.common.graph as nmgraph
        import nemoa.common.plot  as nmplot
        import nemoa.common.math  as nmmath

        # copy graph from system structure of model
        graph = network.get('graph', type = 'graph')

        # create edge attribute 'weight'
        edgeattr  = self.settings.get('edge_weight', 'weight')
        normalize = self.settings.get('edge_normalize', None)
        threshold = self.settings.get('edge_threshold', None)
        transform = self.settings.get('edge_transform', None)

        # calculate maximum weight for normalization (optional)
        if bool(normalize):
            max_weight = 0.0
            for (u, v) in graph.edges():
                weight = graph.edge[u][v]['params'].get(edgeattr, 0.)
                if weight > max_weight: max_weight = weight

        for (u, v) in graph.edges():
            weight = graph.edge[u][v]['params'].get(edgeattr, 0.)

            # threshold weights (optional)
            if bool(threshold) and threshold > numpy.absolute(weight):
                graph.remove_edge(u, v)
                continue

            # create edge attribute 'color' (optional)
            if self.settings.get('edge_color', False):
                if weight > 0: graph.edge[u][v]['color'] = \
                    self.settings.get('edge_poscolor', 'green')
                else: graph.edge[u][v]['color'] = \
                    self.settings.get('edge_negcolor', 'red')

            # create edge attribute 'caption' (optional)
            if self.settings['edge_caption']:
                caption = ' $' + ('%.2g' % (weight)) + '$'
                graph.edge[u][v]['caption'] = caption

            # normalize weights (optional)
            if bool(normalize): weight /= max_weight

            # transform weights (optional)
            if transform == 'softstep': weight = nmmath.softstep(weight)

            graph.edge[u][v]['weight'] = weight

        # normalize signs of weights (optional)
        if self.settings['edge_sign_normalize']:
            number_of_layers = len(graph.graph['params']['layer'])
            if number_of_layers % 2 == 1:
                sign_sum = sum([numpy.sign(graph.edge[u][v]['weight'])
                    for (u, v) in graph.edges()])
                if sign_sum < 0:
                    for (u, v) in graph.edges():
                        graph.edge[u][v]['weight'] *= -1

        # create node attributes 'group', 'caption',
        # 'color', 'font_color', 'border_color'
        groupby = self.settings.get('node_groupby', None)
        groups = nmgraph.nx_get_groups(graph, param = groupby)
        nodes = {n: data for n, data in graph.nodes(data = True)}
        for group in sorted(groups.keys()):
            if group == None: continue
            layout = self.settings['node_groups'].get(group, {})
            group_label = layout.get('label', {
                True: str(groupby).title(),
                False: 'not ' + str(groupby).title()}[group] \
                if isinstance(group, bool) else str(group).title())
            color = layout.get('color', 'white')
            font_color = layout.get('font_color', 'black')
            border_color = layout.get('border_color', 'black')
            for node in groups[group]:
                node_label = nodes[node]['params'].get('label', str(node))
                graph.node[node]['label'] = node_label
                graph.node[node]['color'] = color
                graph.node[node]['group'] = group_label
                graph.node[node]['font_color'] = font_color
                graph.node[node]['border_color'] = border_color

        # prepare parameters
        if self.settings.get('title') == None:
            self.settings['title'] = network.fullname.title()

        # prepare graph layout specific parameters
        graph_layout = self.settings.get('graph_layout', None)
        if graph_layout == 'multilayer':
            if not 'graph_layout_minimize' in self.settings:
                self.settings['graph_layout_minimize'] = 'weight'
            if not 'graph_layout_minimize' in self.settings:
                self.settings['graph_layout_direction'] = \
                    self.settings.get('direction', 'right')

        # plot graph
        return nmplot.layergraph(graph, **self.settings)
