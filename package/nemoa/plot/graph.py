#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base
import numpy, networkx
import matplotlib, matplotlib.pyplot

class structure(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'path': ('system'),
        'dpi': 300,
        'showTitle': True,
        'title': None,
        'backgroundColor': 'none',
        'graphCaption': True,
        'nodeCaption': 'accuracy',
        'nodeSort': 'weight',
        'edges': 'interaction',
        'edgeCaption': False,
        'edgeThreshold': 0.1,
        'edgeContrastBoost': 1.0,
        'edgeZoom': 1.0
        }

    def _create(self, model):

        # create figure and axis objects
        fig = matplotlib.pyplot.figure()
        fig.patch.set_facecolor(self.settings['backgroundColor'])
        ax  = fig.add_subplot(111)
        ax.axis('off')
        ax.autoscale()

        # use captions
        if self.settings['nodeCaption']:

            # get and check node caption relation
            method = self.settings['nodeCaption']
            fPath  = ('system', 'units', method)
            fAbout = model.about(*(fPath + ('name', )))

            if hasattr(fAbout, 'title'):
                fName = model.about(*(fPath + ('name', ))).title()
                fFormat = model.about(*(fPath + ('format', )))
                nCaption = model.eval(*fPath)
                caption  = 'Average ' + fName + ': $\mathrm{%.1f' \
                    % (100 * float(sum([nCaption[u] \
                    for u in nCaption.keys()])) / len(nCaption)) + '\%}$'
            else:
                self.settings['nodeCaption'] = None
                caption = None

        # get unit labels
        units = model.units()
        xLen = max([len(u) for u in units])
        yLen = len(units)

        # calculate sizes
        zoom  = 1.0
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

        # graph
        G = model.network.graph

        # draw labeled nodes
        for gid, group in enumerate(units):
            for uid, unit in enumerate(group):
                attr = model.unit(unit)
                type = attr['params']['type']
                typeid = attr['params']['type_id']
                isVisible = attr['params']['visible']
                labelStr = attr['label'] if isVisible else 'n%d' % (uid + 1)
                label = nemoa.common.strToUnitStr(labelStr)

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
                    if not unit in nCaption: continue
                    networkx.draw_networkx_labels(
                        G, posCap, font_size = 0.75 * graphFontSize,
                        labels = {unit: ' $' + '%d' % (100 * nCaption[unit]) + '\%$'},
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
                weight = nemoa.common.func.boost(weight,
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
                if caption == None:
                    if edges == 'weight': label_text = \
                        r'$\mathbf{Network:}\,\mathrm{%s}$' % \
                        (model.network.graph)
                    elif edges == 'adjacency': label_text = \
                        r'$\mathbf{Network:}\,\mathrm{%s}$' % \
                        (model.network.graph)
                    matplotlib.pyplot.figtext(.5, .11,
                        label_text, fontsize = 9, ha = 'center')
                else: matplotlib.pyplot.figtext(.5, .11,
                    caption, fontsize = 9, ha = 'center')

        return True
