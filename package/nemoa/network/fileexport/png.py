# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import networkx
import os
import matplotlib.pyplot

class Png:

    def __init__(self, workspace = None):
        self.settings = self._settings()

    @staticmethod
    def _settings(): return {
        'fileformat': 'pdf',
        'dpi': 300,
        'output': 'file',
        'show_title': True,
        'title': None,
        'bg_color': 'none',
        'path': ('network', ),
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

    def save(self, network, path):

        # copy graph from system structure of model
        graph = network.get('graph', type = 'graph')

        # common matplotlib settings
        matplotlib.rc('font', family = 'sans-serif')

        # close previous figures
        matplotlib.pyplot.close('all')

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
        nemoa.common.plot.layergraph(graph, **self.settings)

        # (optional) draw title
        if self.settings['show_title']:
            if 'title' in self.settings \
                and isinstance(self.settings['title'], str):
                title = self.settings['title']
            else: title = ''#self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        matplotlib.pyplot.savefig(
            path, dpi = self.settings['dpi'])

        # clear figures and release memory
        matplotlib.pyplot.clf()

        return True
