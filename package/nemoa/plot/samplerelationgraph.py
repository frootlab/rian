# -*- coding: utf-8 -*-
import nemoa

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# plot sample relation graph
def plotSampleRelationGraph(model, file = None, **params):

    # get dataset
    dataset = model.dataset

    # default settings
    settings = {
        'samples': '*',
        'relation': 'correlation',
        'filter_threshold': 2.0,
        'edge_zoom': 1.0,
        'dpi': 300,
        'show_figure_caption': True }

    # overwrite default settings with parameters
    for key, value in params.items():
        if key in settings:
            settings[key] = value

    # calculate 1-dimensional sample relation matrix
    R = model.getSampleRelationMatrix(
        samples = settings['samples'],
        relation = settings['relation'])

    mu, sigma = model.getSampleRelationMatrixMuSigma(
        matrix = R,
        relation = settings['relation'])

    relInfo = model.getSampleRelationInfo(settings['relation'])

    # set boolean filter mask using threshold
    M = np.abs(R - mu) > settings['filter_threshold'] * sigma

    # ignore self relation
    for i in range(R.shape[0]):
        M[i, i] = False

    # info
    numFilter = np.sum(M)
    if numFilter == 0:
        nemoa.log('warning', "   no relation passed filter")
        return False
    else:
        nemoa.log("   %i relations passed filter (%.1f%%)" % \
            (numFilter, float(numFilter) / float(M.shape[0] ** 2 - M.shape[0]) * 100))

    # get weights from relations and filter by mask
    W = np.abs(R) * M
    S = np.sign(R * M)

    # import necessary libs
    from matplotlib.patches import FancyArrowPatch, Circle
    labels = model.dataset.getRowLabels()

    # create graph
    G = nx.MultiDiGraph()

    # add edges
    for i, n1 in enumerate(labels):
        for j, n2 in enumerate(labels):
            if n2 == n1:
                continue
            if not W[i, j]:
                continue
            G.add_edge(n1, n2, weight = W[i, j], sign = S[i, j])

    # find disconnected subgraphs
    Gsub = nx.connected_component_subgraphs(G.to_undirected())
    numSub = len(Gsub)
    numRows = int(np.sqrt(numSub) * 3 / 4) + 1
    numCols = int(np.sqrt(numSub) * 4 / 3)

    if numSub > 1:
        nemoa.log("   %i complexes found" % (numSub))

    # create plots for all subgraphs
    for sub in range(numSub):
        H = G.subgraph(Gsub[sub].nodes())
        ax = plt.subplot(numRows, numCols, sub + 1)

        # calculate positions
        pos = nx.spring_layout(H)
        #pos = nx.circular_layout(H)

        # draw labeled nodes
        maxNodeSize = 800.0
        maxFontSize = 18.0
        nodeSize = maxNodeSize / len(H)
        fontSize = maxFontSize / np.sqrt(len(H))
        maxLineSize = 1.0
        lineSize = maxLineSize / len(H)

        for node in H.nodes():
            backcolor = (0.600, 0.800, 0.196, 0.7)
            facecolor = (0.0, 0.0, 0.0, 0.0, 1.0)
            nodeFontSize = fontSize / np.sqrt(len(node))

            # draw node
            nx.draw_networkx_nodes(
                H, pos,
                node_size  = nodeSize,
                linewidths = lineSize,
                nodelist   = [node],
                node_shape = 'o',
                node_color = backcolor)

            # draw node label
            nx.draw_networkx_labels(
                H, pos,
                font_size = nodeFontSize,
                labels = {node: node},
                font_color = facecolor,
                font_weight = 'normal')

            # patch node for links
            if not relInfo['properties']['symmetric']:
                c = Circle(pos[node], radius = 0.05, alpha = 0.0)
                ax.add_patch(c)
                H.node[node]['patch'] = c

        # draw edges
        maxLineWidth = 1.0 * settings['edge_zoom']
        lineWidth = maxLineWidth / np.sqrt(len(H))

        if relInfo['properties']['symmetric']:

            # draw undirected edges
            for (u, v, d) in H.edges(data = True):

                if d['sign'] > 0:
                    color = 'green'
                else:
                    color = 'red'

                edgeLineWidth = lineWidth * d['weight']

                nx.draw_networkx_edges(
                    H, pos,
                    width = edgeLineWidth,
                    edgelist = [(u, v)],
                    edge_color = color,
                    arrows = False,
                    alpha = 1)

        else:

            # patch nodes for directed edges
            for n in H:
                c = Circle(pos[n], radius = 0.05, alpha = 0.0)
                ax.add_patch(c)
                H.node[n]['patch'] = c

            # draw directed edges
            seen = {}
            for (u, v, d) in H.edges(data = True):
                n1  = H.node[u]['patch']
                n2  = H.node[v]['patch']
                rad = 0.1
                if (u, v) in seen:
                    rad = seen.get((u, v))
                    rad = (rad + np.sign(rad) * 0.2) * -1

                if d['sign'] > 0:
                    color = 'green'
                else:
                    color = 'red'

                arrow = matplotlib.patches.FancyArrowPatch(
                    n1.center, n2.center, patchA = n1, patchB = n2,
                    arrowstyle = '-|>',
                    connectionstyle = 'arc3,rad=%s' % rad,
                    mutation_scale = 35.0 * np.sqrt(d['weight']) * settings['edge_zoom'],
                    linewidth = 2.5 * d['weight'],
                    color = color )

                seen[(u, v)] = rad
                ax.add_patch(arrow)

        ax.autoscale()
        ax.axis('off')

    plt.axis('equal')

    # draw figure title / caption
    if settings['show_figure_caption']:

        # draw title
        title = model.cfg['name']
        plt.figtext(.5, .92, title, fontsize = 10, ha = 'center')

    # output
    if file:
        plt.savefig(file, dpi = settings['dpi'])
    else:
        plt.show()

    # clear current figure object and release memory
    plt.clf()

    return True
