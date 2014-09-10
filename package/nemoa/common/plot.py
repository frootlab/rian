#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, networkx
import matplotlib, matplotlib.pyplot
from matplotlib.patches import FancyArrowPatch, Circle

# create A4 figure object figsize = (8.27, 11.69)

def heatmap(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create heatmap
    cax = ax.imshow(array,
        cmap = matplotlib.cm.hot_r,
        interpolation = kwargs['interpolation'],
        extent = (0, array.shape[1], 0, array.shape[0]))

    # create labels for axis
    maxFontSize = 12.0
    yLabels = [nemoa.common.strToUnitStr(label.split(':')[1]) \
        for label in kwargs['units'][0]]
    xLabels = [nemoa.common.strToUnitStr(label.split(':')[1]) \
        for label in kwargs['units'][1]]
    fontsize = min(maxFontSize, \
        400.0 / float(max(len(xLabels), len(yLabels))))
    matplotlib.pyplot.xticks(
        numpy.arange(len(xLabels)) + 0.5,
        tuple(xLabels), fontsize = fontsize, rotation = 65)
    matplotlib.pyplot.yticks(
        len(yLabels) - numpy.arange(len(yLabels)) - 0.5,
        tuple(yLabels), fontsize = fontsize)

    # create colorbar
    cbar = fig.colorbar(cax)
    for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

    return True

def histogram(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create histogram
    cax = ax.hist(array,
        normed    = False,
        bins      = kwargs['bins'],
        facecolor = kwargs['facecolor'],
        histtype  = kwargs['histtype'],
        linewidth = kwargs['linewidth'],
        edgecolor = kwargs['edgecolor'])

    return True

def graph(graph, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate positions
    if kwargs['layout'] == 'random':
        pos = networkx.random_layout(graph)
    elif kwargs['layout'] == 'circular':
        pos = networkx.circular_layout(graph)
    elif kwargs['layout'] == 'shell':
        pos = networkx.shell_layout(graph)
    elif kwargs['layout'] == 'spring':
        pos = networkx.spring_layout(graph)
    elif kwargs['layout'] == 'fruchterman_reingold':
        pos = networkx.fruchterman_reingold_layout(graph)
    elif kwargs['layout'] == 'spectral':
        pos = networkx.spectral_layout(graph)
    else:
        # warning unknown layout -> using spring
        pos = networkx.spring_layout(graph)

    # colors
    colors = {
        'black': (0.0, 0.0, 0.0, 1.0),
        'white': (1.0, 1.0, 1.0, 1.0),
        'red':   (1.0, 0.0, 0.0, 1.0),
        'green': (0.0, 0.5, 0.0, 1.0),
        'blue':  (0.0, 0.0, 0.7, 1.0),
        'lightgreen': (0.600, 0.800, 0.196, 0.7),
        'lightblue': (0.439, 0.502, 0.565, 0.7) }

    # calculate sizes of nodes, fonts and lines depending on graph size
    nodeSizeMax = 800.0                            # maximum node size
    nodeSizeFactor = 1500.0
    nCount   = float(len(graph))                # number of nodes
    nSize    = max(nodeSizeMax, nodeSizeFactor / nCount)   # node size
    nRadius  = numpy.sqrt(nSize) / 480.0        # node radius
    fSizeMax = 18.0                             # maximum font size
    fSize    = fSizeMax * numpy.sqrt(nSize / nodeSizeMax)
    nodeFontSizeMax = fSize * 0.9               # maximum node font size
    lineWidth = 2.0 / nCount                    # line width
    edgeLineWidth = 10.0 / nCount               # maximum edge line with
    eArrSize = 8.0                              # edge arrow size

    # draw nodes
    for node, attr in graph.nodes(data = True):
        label = attr['label']

        # calculate node fontsize depending on label
        clLabel = label.replace('{', '').replace('}', '')
        if '_' in clLabel: lenLabel = len('_'.split(clLabel)[0]) \
            + 0.5 * len('_'.split(clLabel)[0])
        else: lenLabel = len(clLabel)
        nodeFontSize = nodeFontSizeMax / numpy.sqrt(lenLabel)

        # set backcolor (depending on type) and facecolor
        backcolor = colors[attr['color']]
        facecolor = colors['black']

        # draw node
        networkx.draw_networkx_nodes(graph, pos,
            node_size  = nSize,
            linewidths = lineWidth,
            nodelist   = [node],
            node_shape = 'o',
            node_color = backcolor)

        # draw node label
        networkx.draw_networkx_labels(graph, pos,
            font_size   = nodeFontSize,
            labels      = {node: label},
            font_color  = facecolor,
            font_weight = 'normal')

        # patch node for edges
        c = Circle(pos[node], radius = nRadius, alpha  = 0.0)
        ax.add_patch(c)
        graph.node[node]['patch'] = c

    # draw edges using 'fancy arrows'
    seen = {}
    for (u, v, attr) in graph.edges(data = True):
        n1  = graph.node[u]['patch']
        n2  = graph.node[v]['patch']
        rad = 0.15
        linewidth = edgeLineWidth * attr['weight']
        linecolor = list(colors[attr['color']])
##        linecolor[3] = 2.0 ** attr['weight'] / 2.0
##        linecolor = tuple(linecolor)

        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = (rad + float(numpy.sign(rad)) * 0.2) * -1.0

        arrow = matplotlib.patches.FancyArrowPatch(
            posA   = n1.center,
            posB   = n2.center,
            patchA = n1,
            patchB = n2,
            arrowstyle = '-|>',
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = eArrSize,
            linewidth = linewidth,
            color = linecolor
        )

        seen[(u, v)] = rad
        ax.add_patch(arrow)

    return True
