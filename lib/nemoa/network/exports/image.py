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
        'figure_size': (6.4, 4.8),
        'dpi': None,
        'bg_color': 'none',
        'usetex': False,
        'show_title': False,
        'title': None,
        'title_fontsize': 14.0,
        'show_legend': False,
        'legend_fontsize': 9.0,
        'graph_layout': 'multilayer',
        #'graph_caption': 'accuracy',
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

        # calculate mean weight for normalization (optional)
        if bool(normalize):
            mean = numpy.mean([data['params'].get(edgeattr, 0.) \
                for (u, v, data) in graph.edges(data = True)])

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
            if bool(normalize): weight /= mean

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
            for node in groups.get(group, []):
                node_params = nodes[node].get('params')
                graph.node[node].update({
                    'label': node_params.get('label', str(node)),
                    'color': color,
                    'group': group_label,
                    'font_color': font_color,
                    'border_color': border_color })

        # prepare parameters
        if self.settings.get('title') == None:
            self.settings['title'] = network.fullname.title()

        # graph layout specific attributes and parameters
        graph_layout = self.settings.get('graph_layout', None)
        if graph_layout == 'multilayer':
            for node, data in graph.nodes(data = True):
                graph.node[node].update({
                    'layer': data['params'].get('layer'),
                    'layer_id': data['params'].get('layer_id'),
                    'layer_sub_id': data['params'].get('layer_sub_id')})

        # plot graph
        return nmplot.graph(graph, **self.settings)
