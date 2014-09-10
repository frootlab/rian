#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base
import numpy, networkx
import matplotlib, matplotlib.pyplot

class graph(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'path': ('system', 'relations'),
        'dpi': 300,
        'backgroundColor': 'none',
        'graphCaption': True,
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'normalizeWeights': 'auto',
        'sign': None,
        'filter': None,
        'cutoff': 0.5,
        'nodeCaption': 'accuracy',
        'layout': 'spring'}

    def _create(self, model):

        # get units and edges
        units = self.settings['units']
        edges = []
        for i in units[0]:
            for o in [u for u in units[1] if not u == i]:
                edges.append((i, o))

        ################################################################
        # calculate relations for edge attributes                      #
        ################################################################

        # calculate edge weights from 'weight' relation
        W = model.eval('system', 'relations', self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(W, dict): return nemoa.log('error', """
            could not create relation graph:
            invalid weight relation '%s'!""" % (self.settings['relation']))
        relInfo = model.about('system', 'relations',
            nemoa.common.strSplitParams(self.settings['relation'])[0])

        # calculate edge filter from 'filter' relation
        # default: use the same relation, as used for weights
        # get filter relation
        if not self.settings['filter'] or self.settings['filter'] == \
            self.settings['relation']: F = W
        else: F = model.eval('system', 'relations', self.settings['filter'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'])
        if not isinstance(F, dict): return nemoa.log('error', """
            could not create relation graph:
            invalid filter relation '%s'!""" % (self.settings['filter']))
        # create filter mask from filter relation (parameter: 'cutoff')
        # and update list of edges
        bound = self.settings['cutoff'] * F['std']
        edges = [edge for edge in edges if not -bound < F[edge] < bound]
        if len(edges) == 0: return nemoa.log('warning', """
            could not create relation graph:
            no relation passed filter (threshold = %.2f)!""" % (bound))

        # calculate edge signs from 'sign' relation
        # default: use the same relation, as used for weights
        if self.settings['sign'] == None \
            or self.settings['sign'] == self.settings['relation']: SR = W
        else: SR = model.eval('system', 'relations', self.settings['sign'],
            preprocessing = self.settings['preprocessing'],
            measure       = self.settings['measure'],
            statistics    = self.settings['statistics'])
        if not isinstance(SR, dict): return nemoa.log('error',
            'could not create relation graph: invalid sign relation!')
        S = {edge: 2.0 * (float(SR[edge] > 0.0) - 0.5) for edge in edges}

        ################################################################
        # calculate unit attributes                                    #
        ################################################################

        ## calculate values for node captions
        #if self.settings['nodeCaption']:

            ## get and check node caption relation
            #method = self.settings['nodeCaption']
            #fPath  = ('system', 'units', method)
            #fAbout = model.about(*fPath)

            #if isinstance(fAbout, dict) and 'name' in fAbout.keys():
                #fName    = model.about(*(fPath + ('name', ))).title()
                #fFormat  = model.about(*(fPath + ('format', )))
                #nCaption = model.eval(*fPath)
            #else:
                #nCaption = None

        # create graph and set name
        graph = networkx.MultiDiGraph(name = relInfo['name'])

        # add edges and edge attributes to graph
        if self.settings['normalizeWeights'] in [None, 'auto']:
            normalize = not relInfo['normal']
        elif self.settings['normalizeWeights'] in [True, False]:
            normalize = self.settings['normalizeWeights']
        else: return nemoa.log('error', """
            could not create relation graph:
            invalid value for parameter 'normalizeWeights'!""")
        for edge in edges: graph.add_edge(*edge,
            weight = abs(W[edge] / W['std'] if normalize else W[edge]),
            color = {1: 'green', 0: 'black', -1: 'red'}[S[edge]])

        # find (disconected) complexes in graph
        graphs = networkx.connected_component_subgraphs(
            graph.to_undirected())
        if len(graphs) > 1: nemoa.log(
            '%i complexes found' % (len(graphs)))

        # update node attributes
        for i in range(len(graphs)):
            for n in graphs[i].nodes():
                node  = model.network.node(n)
                label = nemoa.common.strToUnitStr(node['label'])
                ntype = node['params']['type']
                graph.node[n]['label'] = label
                graph.node[n]['type'] = ntype
                graph.node[n]['complex'] = i
                graph.node[n]['color'] = {
                    'i': 'lightgreen', 'o': 'lightblue'}[ntype]

        # create plot
        return nemoa.common.plot.graph(graph, **self.settings)

class heatmap(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'path': ('system', 'relations'),
        'dpi': 300,
        'backgroundColor': 'none',
        'graphCaption': True,
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'layer': None,
        'interpolation': 'nearest' }

    def _create(self, model):

        # calculate and test relation matrix
        R = model.eval('system', 'relations', self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'],
            format = 'array')
        if not isinstance(R, numpy.ndarray): return nemoa.log('error',
            'could not plot heatmap: relation matrix is not valid!')

        # create plot
        return nemoa.common.plot.heatmap(R, **self.settings)

class histogram(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'path': ('system', 'relations'),
        'dpi': 300,
        'backgroundColor': 'none',
        'graphCaption': True,
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'layer': None,
        'bins': 50,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def _create(self, model):

        # get units and edges
        units = self.settings['units']
        edges = []
        for i in units[0]:
            for o in [u for u in units[1] if not u == i]:
                edges.append((i, o))

        # calculate relation
        R = model.eval('system', 'relations', self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(R, dict): return nemoa.log('error', """
            could not create relation histogram:
            invalid relation '%s'!""" % (self.settings['relation']))

        # create data array
        data = numpy.array([R[edge] for edge in edges])

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
