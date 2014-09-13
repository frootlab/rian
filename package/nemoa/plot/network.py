#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base, numpy, networkx

class graph(nemoa.plot.base.plot):

    @staticmethod
    def _settings(): return {
        'path': ('network', ),
        'graphCaption': 'accuracy',
        'graphDirection': 'right',
        'nodeCaption': 'accuracy',
        'nodeSort': True,
        'edgeCaption': None,
        'edgeWeight': 'normal',
        'edgeSignNormalize': True,
        'edgeIntensify': 10.0,
        'edgeThreshold': 0.25,
        'edgeScale': 1.5 }

    def _create(self, model):

        # copy graph from system structure of model
        graph = model.network.graph.copy()

        # (optional) calculate node captions
        if self.settings['nodeCaption']:
            caption = model.eval('system', 'units', self.settings['nodeCaption'])
            if caption:
                for node in caption.keys(): graph.node[node]['caption'] = \
                    ' $%i' % (round(100.0 * caption[node])) + '\%$'

        # (optional) calculate graph caption
        if self.settings['graphCaption']:
            caption = model.eval('system', self.settings['graphCaption'])
            if caption:
                name = model.about('system', self.settings['graphCaption'])['name'].title()
                graph.graph['caption'] = \
                    name + ': $%i' % (round(100.0 * caption)) + '\%$'

        # update edge weights
        for (u, v) in graph.edges():
            graph.edge[u][v]['weight'] = \
                graph.edge[u][v]['params'][self.settings['edgeWeight']]

            # (optional) intensify weights
            if self.settings['edgeIntensify'] > 0.0:
                graph.edge[u][v]['weight'] = \
                    nemoa.common.func.intensify(graph.edge[u][v]['weight'],
                        factor = self.settings['edgeIntensify'],
                        bound = 1.0) # 2do: set bound to mean value

            # (optional) threshold weights
            if self.settings['edgeThreshold'] > 0.0:
                if not numpy.abs(graph.edge[u][v]['weight']) \
                    > self.settings['edgeThreshold']:
                    graph.remove_edge(u, v)

        # (optional) normalize edge signs
        if self.settings['edgeSignNormalize']:
            signSum = sum([numpy.sign(graph.edge[u][v]['weight'])
                for (u, v) in graph.edges()])
            if signSum < 0:
                for (u, v) in graph.edges():
                    graph.edge[u][v]['weight'] *= -1

        # (optional) create edge captions
        if self.settings['edgeCaption']:
            for (u, v) in graph.edges():
                graph.edge[u][v]['caption'] = \
                    ' $' + ('%.2g' % (graph.edge[u][v]['weight'])) + '$'

        return nemoa.common.plot.layerGraph(graph, **self.settings)
