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

def save(network, path = None, plot = None, output = 'file', **kwargs):

    if output.lower() == 'file':

        # extract filetype from path
        filetype = nemoa.common.get_file_extension(path).lower()

        # test if filetype is supported by matplotlib
        if not filetype in filetypes():
            return nemoa.log('error', """could not create plot:
                filetype '%s' is not supported by matplotlib.""" %
                (filetype))

    # get class for plotting from attribute 'plot'
    if plot == None: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot network '%s':
            plot type '%s' is not supported.""" %
            (network.get('name'), plot))

    # create plot of network
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
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
            else: title = '' # TODO: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        if output.lower() == 'file':
            matplotlib.pyplot.savefig(
                path, dpi = plot.settings['dpi'])
        elif output.lower() == 'display':
            matplotlib.pyplot.show()

    # clear figures and release memory
    matplotlib.pyplot.clf()

    if output.lower() == 'file':
        return path
    return True

class Graph:

    settings = {
        'fileformat': 'pdf',
        'dpi': 300,
        'show_title': True,
        'title': None,
        'bg_color': 'none',
        'graph_caption': 'accuracy',
        'graph_direction': 'right',
        'node_caption': 'accuracy',
        'node_sort': True,
        'edge_caption': None,
        'edge_weight': 'normal',
        'edge_sign_normalize': True,
        'edge_contrast': 10.,
        'edge_threshold': 0.25,
        'edge_scale': 1.5 }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def create(self, network):

        # copy graph from system structure of model
        graph = network.get('graph', type = 'graph')

        ## (optional) calculate node captions
        #if self.settings['node_caption']:
            #caption = model.evaluate('system', 'units',
                #self.settings['node_caption'])
            #if caption:
                #for node in caption.keys():
                    #graph.node[node]['caption'] = \
                        #' $%i' % (round(100. * caption[node])) + '\%$'

        ## (optional) calculate graph caption
        #if self.settings['graph_caption']:
            #caption = model.evaluate('system',
                #self.settings['graph_caption'])
            #if caption:
                #name = model.about('system',
                    #self.settings['graph_caption'])['name'].title()
                #graph.graph['caption'] = \
                    #name + ': $%i' % (round(100. * caption)) + '\%$'

        # update edge weights
        for (u, v) in graph.edges():
            edge = graph.edge[u][v]

            weight_params = self.settings['edge_weight']
            if  weight_params in edge['params']:
                edge['weight'] = edge['params'][weight_params]
            else:
                edge['weight'] = 1.

            # (optional) intensify weights
            if self.settings['edge_contrast'] > 0.:
                edge['weight'] = \
                    nemoa.common.intensify(edge['weight'],
                        factor = self.settings['edge_contrast'],
                        bound = 1.) # TODO: set bound to mean value

            # (optional) threshold weights
            if self.settings['edge_threshold'] > 0.:
                if not numpy.abs(edge['weight']) \
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
