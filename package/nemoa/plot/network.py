#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base
import numpy, networkx

class graph(nemoa.plot.base.plot):

    @staticmethod
    def _settings(): return {
        'path': ('network', ),
        'graphCaption': True,
        'graphDirection': 'right',
        'nodeCaption': 'accuracy',
        'nodeSort': True,
        'edgeWeight': 'normal',
        'edgeSignNormalize': True,
        'edgeIntensify': 10.0,
        'edgeThreshold': 0.25,
        'edgeCaption': False,
        'edgeScale': 1.5 }

    def _create(self, model):

        # copy graph from system structure of model
        graph = model.network.graph.copy()

        # (optional) create node captions
        if self.settings['nodeCaption']:

            # get and check node caption relation
            method = self.settings['nodeCaption']
            fPath  = ('system', 'units', method)
            fAbout = model.about(*(fPath + ('name', )))

            if hasattr(fAbout, 'title'):
                fName    = model.about(*(fPath + ('name', ))).title()
                fFormat  = model.about(*(fPath + ('format', )))
                nCaption = model.eval(*fPath)
                for node in nCaption.keys(): graph.node[node]['caption'] = \
                    ' $' + '%i' % (round(100.0 * nCaption[node])) + '\%$'
                caption = 'Average ' + fName + ': $\mathrm{%.1f' \
                    % (round(1000.0 * float(sum([nCaption[u] for u in \
                    nCaption.keys()])) / float(len(nCaption))) / 10.0) \
                    + '\%}$'
                graph.graph['caption'] = caption

        # update edge weights
        for (n1, n2) in graph.edges():
            graph.edge[n1][n2]['weight'] = \
                graph.edge[n1][n2]['params'][self.settings['edgeWeight']]

            # (optional) intensify weights
            if self.settings['edgeIntensify'] > 0.0:
                graph.edge[n1][n2]['weight'] = \
                    nemoa.common.func.intensify(graph.edge[n1][n2]['weight'],
                        factor = self.settings['edgeIntensify'],
                        bound = 1.0) # 2do: set bound to mean value

            # (optional) threshold weights
            if self.settings['edgeThreshold'] > 0.0:
                if not numpy.abs(graph.edge[n1][n2]['weight']) \
                    > self.settings['edgeThreshold']:
                    graph.remove_edge(n1, n2)

        # (optional) normalize edge signs
        if self.settings['edgeSignNormalize']:
            signSum = sum([numpy.sign(graph.edge[n1][n2]['weight'])
                for (n1, n2) in graph.edges()])
            if signSum < 0:
                for (n1, n2) in graph.edges():
                    graph.edge[n1][n2]['weight'] *= -1.0

        # (optional) create edge captions
        if self.settings['edgeCaption']:
            for (v, h) in graph.edges():
                graph.edge[v][h]['caption'] = \
                    ' $' + ('%.2g' % (graph.edge[v][h]['weight'])) + '$'

        return nemoa.common.plot.layerGraph(graph, **self.settings)
