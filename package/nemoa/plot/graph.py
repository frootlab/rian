#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base, numpy, networkx, matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyArrowPatch, Circle

class structure(nemoa.plot.base.plot):

    @staticmethod
    def _snake(x, factor = 1.0):
        return numpy.abs(x) * (1.0 / (1.0 + numpy.exp(-10.0 * factor
            * (x + 0.5))) + 1.0 / (1.0 + numpy.exp(-10.0 * factor
            * (x - 0.5))) - 1.0)

    @staticmethod
    def _default():
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 300,
            'showTitle': True,
            'title': None,
            'graphCaption': True,
            'nodeCaption': 'performance',
            'nodeSort': 'weight',
            'edges': 'interaction',
            'edgeCaption': False,
            'edgeThreshold': 0.1,
            'edgeContrastBoost': 1.0,
            'edgeZoom': 1.0
        }

    def _create(self, model):

        # use captions
        if self.settings['nodeCaption']:

            # get and check node caption relation
            method = self.settings['nodeCaption']
            fPath = ('system', 'units', 'method', method)
            fAbout = model.about(*(fPath + ('name', )))
            
            if hasattr(fAbout, 'title'):
                fName = model.about(*(fPath + ('name', ))).title()
                fFormat = model.about(*(fPath + ('format', )))
                nodeCaption = model.evalUnits(func = method)
                caption  = 'Average ' + fName + ': $\mathrm{%.1f' \
                    % (100 * float(sum([nodeCaption[u] \
                    for u in nodeCaption.keys()])) / len(nodeCaption)) + '\%}$'
            else:
                self.settings['nodeCaption'] = None
                caption = None

        # get unit labels
        units = model.units()
        xLen = max([len(u) for u in units])
        yLen = len(units)

        # calculate sizes
        zoom = 1.0
        scale = min(250.0 / xLen, 150.0 / yLen, 30.0)
        graphNodeSize = scale ** 2
        graphFontSize = 0.4 * scale
        graphCaptionFactor = 0.5 + 0.003 * scale
        graphLineWidth = 0.3

        # sort units (optional)
        if isinstance(self.settings['nodeSort'], str):
            sortUnits = list(units)
            sortParam = self.settings['nodeSort']
            for gid, group in enumerate(sortUnits):
                if not gid: continue
                sort = []
                for uid, u in enumerate(group):
                    sort.append((numpy.sum([float(puid) \
                        * numpy.abs(model.link((pu, u))['params'][sortParam]) \
                        for puid, pu in enumerate(sortUnits[gid - 1])]), u))
                sortGroup = [pu[1] for pu in sorted(sort, key = lambda x: x[0])]
                sortUnits[gid] = sortGroup
            units = tuple(sortUnits)

        # calculate node positions for stacked graph layout
        pos = {}
        posCap = {}
        for gid, group in enumerate(units):
            for uid, unit in enumerate(group):
                x = (uid + 0.5) / len(group)
                y = 1.0 - gid / (yLen - 1.0)
                c = (1.0 - gid) * graphCaptionFactor + 0.5
                pos[unit] = (x, y)
                posCap[unit] = (x, c)

        # create figure object
        fig = plt.figure()

        # graph
        G = model.network.graph

        # draw labeled nodes
        for gid, group in enumerate(units):
            for uid, unit in enumerate(group):
                attr = model.unit(unit)
                type = attr['params']['type']
                typeid = attr['params']['type_id']
                isVisible = attr['params']['visible']
                if not isVisible: label = \
                    nemoa.common.strToUnitStr('n%d' % (uid + 1))
                else: label = nemoa.common.strToUnitStr(attr['label']) 

                color = {
                    True: {
                        'bg':   (0.27, 0.51, 0.70, 1.0),
                        'font': (0.0, 0.0, 0.0, 1.0) },
                    False: {
                        'bg':   (0.8, 0.8, 0.8, 1.0),
                        'font': (0.0, 0.0, 0.0, 1.0) }
                }[isVisible]

                # draw node
                networkx.draw_networkx_nodes(
                    G, pos,
                    node_size  = graphNodeSize,
                    linewidths = graphLineWidth,
                    nodelist   = [unit],
                    node_shape = 'o',
                    node_color = color['bg'])

                # draw node label
                nodeFontSize = \
                    2.0 * graphFontSize / numpy.sqrt(max(len(unit) - 1, 1))
                networkx.draw_networkx_labels(
                    G, pos,
                    font_size = nodeFontSize,
                    labels = {unit: label},
                    font_weight = 'normal',
                    font_color = color['font'])

                # draw node caption
                if self.settings['nodeCaption'] and isVisible:
                    if not unit in nodeCaption: continue 
                    networkx.draw_networkx_labels(
                        G, posCap, font_size = 0.75 * graphFontSize,
                        labels = {unit: ' $' + '%d' % (100 * nodeCaption[unit]) + '\%$'},
                        font_weight = 'normal')

        # draw labeled edges
        for (v, h) in G.edges():

            # get weight
            attr = model.system.getLink((v, h))
            if not attr: attr = model.system.getLink((h, v))
            if not attr: continue

            weight = attr[self.settings['edges']]

            # boost edge contrast
            if self.settings['edgeContrastBoost'] > 0.0:
                weight = self._snake(weight,
                    factor = self.settings['edgeContrastBoost'])

            # check if weight satisfies threshold
            if not numpy.abs(weight) > self.settings['edgeThreshold']: continue

            # get edge color and line width (from weight)
            if self.settings['edges'] == 'adjacency':
                color = 'black'
                edgeLineWidth = graphLineWidth * self.settings['edgeZoom']
            else:
                color = 'green' if weight > 0.0 else 'red'
                edgeLineWidth = \
                    weight * graphLineWidth * self.settings['edgeZoom']

            # draw edges
            networkx.draw_networkx_edges(
                G, pos,
                width = edgeLineWidth,
                edgelist = [(v, h)],
                edge_color = color,
                arrows = False,
                alpha = 1.0)

            # draw edge labels
            if not self.settings['edgeCaption']: continue
            size = graphFontSize / 1.5
            label = ' $' + ('%.2g' % (numpy.abs(weight))) + '$'
            networkx.draw_networkx_edge_labels(
                G, pos,
                edge_labels = {(v, h): label},
                font_color = color,
                clip_on = False,
                font_size = size,
                font_weight = 'normal')

        # draw caption
        if self.settings['graphCaption']:
            if self.settings['nodeCaption']:

                # draw caption
                if caption == None:
                    if edges == 'weight':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    elif edges == 'adjacency':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    plt.figtext(.5, .11, label_text, fontsize = 9, ha = 'center')
                else:
                    plt.figtext(.5, .11, caption, fontsize = 9, ha = 'center')

        plt.axis('off')
        return True

class relation(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'dpi': 300,
        'show_figure_caption': True,
        'interpolation': 'nearest' }

    def _create(self, model, **params):

        # default settings
        settings = {
            'units': 'visible',
            'relation': 'knockout_relapprox_setmean',
            'threshold': 2.0,
            'filter': None,
            'sign': 'correlation',
            'statistics': 10000,
            'edge_zoom': 1.0,
            'dpi': 300,
            'layout': 'fruchterman_reingold',
            'show_figure_caption': True,
            'title': None
        }

        # overwrite default settings with parameters
        for key, value in params.items():
            if key in settings: settings[key] = value

        # set default settings for filter and sign
        if not settings['sign']: settings['sign'] = settings['relation']
        if not settings['filter']: settings['filter'] = settings['relation']

        # get lists of visible and hidden units
        visible, hidden = model.system.getUnits()
        if settings['units'] == 'visible': settings['units'] = visible
        elif settings['units'] == 'hidden': settings['units'] = hidden

        # get title of model
        if settings['show_figure_caption']: settings['title'] = model.cfg['name']

        # get number of units and relations
        numUnits = len(settings['units'])
        numRelations = numUnits ** 2

        #
        # GET FILTER MASK FOR RELATIONS
        #

        if settings['filter'] == None:
            M = np.ones((numUnits, numUnits), dtype = 'bool')
        else:
            nemoa.log("calculate filter mask: %s > %.1f sigma" % \
                (settings['filter'], settings['threshold']))

            # get filter relation matrix
            F = model.getUnitRelationMatrix(
                units = settings['units'],
                relation = settings['filter'],
                statistics = settings['statistics'])

            # get sigma and mu
            mu, sigma = model.getUnitRelationMatrixMuSigma(
                matrix = F,
                relation = settings['filter'])

            # set boolean filter mask using threshold
            M = np.abs(F - mu) > settings['threshold'] * sigma

            # ignore self relation
            for i in range(numUnits): M[i, i] = False

            # info
            numFilter = np.sum(M)
            if numFilter == 0:
                nemoa.log('warning', "no relation passed filter")
                return False

            nemoa.log("%i relations passed filter (%.1f%%)" % \
                (numFilter, float(numFilter) / float(numRelations - numUnits) * 100))

        #
        # GET WEIGHTS
        #

        nemoa.log("calculate edge weights: " + settings['relation'])

        # use filter results if relation and filter are the same
        if settings['relation'] == settings['filter']:
            R = F
        else:
            R = model.getUnitRelationMatrix(
                units = settings['units'],
                relation = settings['relation'],
                statistics = settings['statistics'])

        # get weights from relations and filter by mask
        W = np.abs(R) * M

        # normalize weights
        if np.max(W) == 0: return nemoa.log('error', 'no weights > 0 found')
        else: W = W / np.max(W)

        #
        # GET SIGN OF RELATIONS
        #

        if settings['sign'] == settings['relation']: S = np.sign(R) * M
        elif settings['sign'] == settings['filter']: S = np.sign(F) * M
        else: S = model.getUnitRelationMatrix(
            units = settings['units'],
            relation = settings['sign'],
            statistics = settings['statistics'])

        #
        # CREATE GRAPH AND FIND DISCONNECTED SUBGRAPHS
        #

        # create graph
        G = networkx.MultiDiGraph()

        # add edges and attributes
        for i, n1 in enumerate(visible):
            for j, n2 in enumerate(visible):
                if n2 == n1:
                    continue
                if not W[i, j]:
                    continue
                if S[i, j] > 0:
                    color = 'green'
                else:
                    color = 'red'

                G.add_edge(
                    n1, n2,
                    weight = float(W[i, j]),
                    sign = S[i, j],
                    color = color)

        # find disconnected subgraphs
        Gsub = networkx.connected_component_subgraphs(G.to_undirected())
        numSub = len(Gsub)
        if numSub > 1:
            nemoa.log("   %i disconnected complexes found" % (numSub))

        for sub in range(numSub):
            for node in Gsub[sub].nodes():
                mNode = model.network.node(node)
                G.node[node]['label'] = mNode['label']
                G.node[node]['type'] = mNode['params']['type']
                G.node[node]['complex'] = sub
                G.node[node]['color'] = {
                    'e': 'lightgreen',
                    's': 'lightblue'
                }[mNode['params']['type']]

        #
        # CREATE PLOT
        #

        self._plotGraph(graph = G, **settings)

        return True

    def _plotGraph(self, graph, file = None, **params):
        ax = plt.subplot(1, 1, 1)

        # calculate positions
        if params['layout'] == 'random':
            pos = networkx.random_layout(graph)
        elif params['layout'] == 'spring':
            pos = networkx.spring_layout(graph)
        elif params['layout'] == 'circular':
            pos = networkx.circular_layout(graph)
        elif params['layout'] == 'fruchterman_reingold':
            pos = networkx.fruchterman_reingold_layout(graph)
        elif params['layout'] == 'spectral':
            pos = networkx.spectral_layout(graph)
        else:
            # warning unknown layout -> using spring
            pos = networkx.spring_layout(graph)

        # colors
        colors = {
            'black': (0.0, 0.0, 0.0, 1.0),
            'white': (1.0, 1.0, 1.0, 1.0),
            'red': (1.0, 0.0, 0.0, 1.0),
            'green': (0.0, 0.5, 0.0, 1.0),
            'blue': (0.0, 0.0, 0.7, 1.0),
            'lightgreen': (0.600, 0.800, 0.196, 0.7),
            'lightblue': (0.439, 0.502, 0.565, 0.7),
        }

        # calculate sizes of nodes, fonts and lines depending to Graph size
        maxNodeSize = 800.0
        maxFontSize = 18.0
        maxLineSize = 1.0
        arrSize  = 2.5
        nodeNum  = float(len(graph))
        nodeSize = maxNodeSize / nodeNum
        nodeRad  = np.sqrt(nodeSize) / 1500.0
        fontSize = maxFontSize * np.sqrt(nodeSize / maxNodeSize)
        lineSize = maxLineSize / nodeNum

        # draw nodes
        for node, attr in graph.nodes(data = True):
            label = attr['label']

            # calculate sizes of fontsize depending to length of labels
            nodeFontSize = fontSize / np.sqrt(len(label)) * 0.9

            # set backcolor (depending on type) and facecolor
            backcolor = colors[attr['color']]
            facecolor = colors['black']

            # draw node
            networkx.draw_networkx_nodes(
                graph, pos,
                node_size  = nodeSize,
                linewidths = lineSize,
                nodelist   = [node],
                node_shape = 'o',
                node_color = backcolor)

            # draw label
            networkx.draw_networkx_labels(
                graph, pos,
                font_size = nodeFontSize,
                labels = {node: label},
                font_color = facecolor,
                font_weight = 'normal')

            # patch node for edges
            c = Circle(
                pos[node],
                radius = nodeRad,
                alpha = 0.0)

            ax.add_patch(c)
            graph.node[node]['patch'] = c

    ##    # scale edges
    ##    maxWeight = 0.0
    ##    minWeight = 1.0
    ##    for (u, v, attr) in graph.edges(data = True):
    ##        if attr['weight'] > maxWeight:
    ##            maxWeight = attr['weight']
    ##        if attr['weight'] < minWeight:
    ##            minWeight = attr['weight']
    ##
    ##    print maxWeight
    ##    print minWeight

        # draw edges using 'fancy arrows'
        seen = {}
        for (u, v, attr) in graph.edges(data = True):
            n1  = graph.node[u]['patch']
            n2  = graph.node[v]['patch']
            rad = 0.1 # radius of arrow
            linewidth = float(lineSize) * attr['weight'] * params['edge_zoom'] * 5.0
            linecolor = list(colors[attr['color']])
    ##        linecolor[3] = 2.0 ** attr['weight'] / 2.0
    ##        linecolor = tuple(linecolor)

            if (u, v) in seen:
                rad = seen.get((u, v))
                rad = (rad + np.sign(rad) * 0.2) * -1

            arrow = matplotlib.patches.FancyArrowPatch(
                posA = n1.center,
                posB = n2.center,
                patchA = n1,
                patchB = n2,
                arrowstyle = '-|>',
                connectionstyle = 'arc3,rad=%s' % rad,
                mutation_scale = arrSize,
                linewidth = linewidth,
                color = linecolor
            )

            seen[(u, v)] = rad
            ax.add_patch(arrow)

        ax.autoscale()
        ax.axis('off')
        plt.axis('equal')

        return True
