#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyArrowPatch, Circle

class graph(nemoa.plot.base.plot):

    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'interpolation': 'nearest'
        }


def plotUnitRelationGraph(model, file = None, **params):

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
        if key in settings:
            settings[key] = value

    # set default settings for filter and sign
    if not settings['sign']:
        settings['sign'] = settings['relation']
    if not settings['filter']:
        settings['filter'] = settings['relation']

    # get lists of visible and hidden units
    visible, hidden = model.system.getUnits()
    if settings['units'] == 'visible':
        settings['units'] = visible
    elif settings['units'] == 'hidden':
        settings['units'] = hidden

    # get title of model
    if settings['show_figure_caption']:
        settings['title'] = model.cfg['name']

    # get number of units and relations
    numUnits = len(settings['units'])
    numRelations = numUnits ** 2

    #
    # GET FILTER MASK FOR RELATIONS
    #

    if settings['filter'] == None:
        M = np.ones((numUnits, numUnits), dtype = 'bool')
    else:
        nemoa.log("   calculate filter mask: %s > %.1f sigma" % \
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
        for i in range(numUnits):
            M[i, i] = False

        # info
        numFilter = np.sum(M)
        if numFilter == 0:
            nemoa.log('warning', "   no relation passed filter")
            return False

        nemoa.log("   %i relations passed filter (%.1f%%)" % \
            (numFilter, float(numFilter) / float(numRelations - numUnits) * 100))

    #
    # GET WEIGHTS
    #

    nemoa.log("   calculate edge weights: " + settings['relation'])

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
    if np.max(W) == 0:
        nemoa.log('warning', '   no weights > 0 found')
        return False
    else:
        W = W / np.max(W)

    #
    # GET SIGN OF RELATIONS
    #

    if settings['sign'] == settings['relation']:
        S = np.sign(R) * M
    elif settings['sign'] == settings['filter']:
        S = np.sign(F) * M
    else:
        S = model.getUnitRelationMatrix(
            units = settings['units'],
            relation = settings['sign'],
            statistics = settings['statistics'])

    #
    # CREATE GRAPH AND FIND DISCONNECTED SUBGRAPHS
    #

    # create graph
    G = nx.MultiDiGraph()

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
    Gsub = nx.connected_component_subgraphs(G.to_undirected())
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

    return plotGraph(graph = G, file = file, **settings)

def plotGraph(graph, file = None, **params):
    ax = plt.subplot(1, 1, 1)

    # calculate positions
    if params['layout'] == 'random':
        pos = nx.random_layout(graph)
    elif params['layout'] == 'spring':
        pos = nx.spring_layout(graph)
    elif params['layout'] == 'circular':
        pos = nx.circular_layout(graph)
    elif params['layout'] == 'fruchterman_reingold':
        pos = nx.fruchterman_reingold_layout(graph)
    elif params['layout'] == 'spectral':
        pos = nx.spectral_layout(graph)
    else:
        # warning unknown layout -> using spring
        pos = nx.spring_layout(graph)

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
        nx.draw_networkx_nodes(
            graph, pos,
            node_size  = nodeSize,
            linewidths = lineSize,
            nodelist   = [node],
            node_shape = 'o',
            node_color = backcolor)

        # draw label
        nx.draw_networkx_labels(
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

    # draw figure title / caption
    if params['title']:
        plt.figtext(.5, .92, title, fontsize = 10, ha = 'center')

    # output
    if file:
        plt.savefig(file, dpi = params['dpi'])
    else:
        plt.show()

    # clear current figure object and release memory
    plt.clf()

    return True
