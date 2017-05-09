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

        # (optional) draw title
        if plot.settings['show_title']:
            if 'title' in plot.settings \
                and isinstance(plot.settings['title'], str):
                title = plot.settings['title']
            else: title = '' # Todo: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # (optional) draw legend
        if plot.settings['show_legend']:
            matplotlib.pyplot.legend(numpoints = 1,
                loc = 'lower center', ncol = 4, borderaxespad = 0. )

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

        # (optional) draw title
        if plot.settings['show_title']:
            if 'title' in plot.settings \
                and isinstance(plot.settings['title'], str):
                title = plot.settings['title']
            else: title = '' # Todo: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # (optional) draw legend
        if plot.settings['show_legend']:
            matplotlib.pyplot.legend(numpoints = 1,
                loc = 'lower center', ncol = 4, borderaxespad = 0. )

        # output
        matplotlib.pyplot.savefig(path, dpi = plot.settings['dpi'])

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return path

class Graph:

    settings = None
    default = {
        'fileformat': 'pdf',
        'dpi': 300,
        'usetex': False,
        'show_title': False,
        'show_legend': False,
        'title': None,
        'layout': 'multilayer',
        'bg_color': 'none',
        'graph_caption': 'accuracy',
        'graph_direction': 'right',
        'node_caption': 'accuracy',
        'node_sort': True,
        'edge_caption': None,
        'edge_weight': 'intensity',
        'edge_threshold': 0.75,
        'edge_sign_normalize': True }

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def create(self, network):

        # copy graph from system structure of model
        graph = network.get('graph', type = 'graph')

        # update edge weights
        for (u, v) in graph.edges():
            edge = graph.edge[u][v]

            weightparam = self.settings['edge_weight']
            if  weightparam in edge['params']:
                edge['weight'] = edge['params'][weightparam]
            else:
                edge['weight'] = 1.

            # (optional) threshold weights
            if self.settings['edge_threshold'] > 0.:
                if not numpy.absolute(edge['weight']) \
                    > self.settings['edge_threshold']:
                    graph.remove_edge(u, v)

        # (optional) normalize edge signs
        if self.settings['edge_sign_normalize']:
            number_of_layers = len(graph.graph['params']['layer'])
            if number_of_layers % 2 == 1:
                sign_sum = sum([numpy.sign(graph.edge[u][v]['weight'])
                    for (u, v) in graph.edges()])
                if sign_sum < 0:
                    for (u, v) in graph.edges():
                        graph.edge[u][v]['weight'] *= -1

        # (optional) create edge captions
        if self.settings['edge_caption']:
            for (u, v) in graph.edges():
                graph.edge[u][v]['caption'] = \
                    ' $' + ('%.2g' % (graph.edge[u][v]['weight'])) + '$'

        # plot model
        return nemoa.common.plot.layergraph(graph, **self.settings)
