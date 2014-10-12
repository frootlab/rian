# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import networkx

class graph(nemoa.plot.base.plot):

    @staticmethod
    def _settings(): return {
        'path': ('network', ),
        'graph_caption': 'accuracy',
        'graph_direction': 'right',
        'node_caption': None,
        'node_sort': True,
        'edge_caption': None,
        'edge_weight': 'normal',
        'edge_sign_normalize': True,
        'edge_contrast': 10.,
        'edge_threshold': 0.25,
        'edge_scale': 1.5 }

    def _create(self, model):

        # copy graph from model
        graph = model.network.get('graph', type = 'graph')

        # (optional) calculate node captions
        if self.settings['node_caption']:
            caption = model.evaluate('system', 'units',
                self.settings['node_caption'])
            if caption:
                for node in caption.keys():
                    graph.node[node]['caption'] = \
                        ' $%i' % (round(100. * caption[node])) + '\%$'

        # (optional) calculate graph caption
        if self.settings['graph_caption']:
            caption = model.evaluate('system',
                self.settings['graph_caption'])
            if caption:
                name = model.about('system',
                    self.settings['graph_caption'])['name'].title()
                graph.graph['caption'] = \
                    name + ': $%i' % (round(100. * caption)) + '\%$'

        # update edge weights
        for (u, v) in graph.edges():
            graph.edge[u][v]['weight'] = \
                graph.edge[u][v]['params'][self.settings['edge_weight']]

            # (optional) intensify weights
            if self.settings['edge_contrast'] > 0.:
                graph.edge[u][v]['weight'] = \
                    nemoa.common.intensify(graph.edge[u][v]['weight'],
                        factor = self.settings['edge_contrast'],
                        bound = 1.) # TODO: set bound to mean value

            # (optional) threshold weights
            if self.settings['edge_threshold'] > 0.:
                if not numpy.abs(graph.edge[u][v]['weight']) \
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

        return nemoa.common.plot.layergraph(graph, **self.settings)
