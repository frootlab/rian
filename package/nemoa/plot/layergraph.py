# -*- coding: utf-8 -*-
import nemoa
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from nemoa.plot.base import plot

class layerGraph(plot):

    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'edge_caption': 'weights',
            'edge_threshold': 0.0,
            'edge_weight': None,
            'edge_color': False,
            'edge_zoom': 1.0,
            'node_caption': None
        }

    def create(self, model, file = None):

        # get title
        if 'title' in self.settings:
            title = self.settings['title']
        else:
            title = model.name()

        # use captions
        if self.settings['node_caption']:

            # get node captions
            method = self.settings['node_caption']
            nodeCaption = model.getUnitEval(eval = method)

            # get model caption
            fPath = ('system', 'units', 'method', method)
            fName = model.about(*(fPath + ('name', ))).title()
            fFormat = model.about(*(fPath + ('format', )))
            caption  = 'Average ' + fName + ': $\mathrm{%.1f' \
                % (100 * float(sum([nodeCaption[u] \
                for u in nodeCaption.keys()])) / len(nodeCaption)) + '\%}$'

        # get unit labels
        units = model.units()
        xLen = max([len(u) for u in units])
        yLen = len(units)

        # calculate sizes
        zoom = 1.0
        scale = min(250.0 / xLen, 30.0)
        graph_node_size = scale ** 2
        graph_font_size = 0.4 * scale
        graph_caption_factor = 0.5 + 0.003 * scale
        graphLineWidth = 0.3

        # graph
        G = model.network.graph

        # calculate node positions for 'stack layout'
        pos = {}
        pos_caption = {}
        for node, attr in G.nodes(data = True):
            xID = attr['params']['type_node_id']
            yID = attr['params']['type_id']
            gSize = len(units[yID])

            x = (xID + 0.5) / gSize
            y = 1.0 - yID / (yLen - 1.0)
            yC = (1.0 - yID) * graph_caption_factor + 0.5

            pos[node] = (x, y)
            pos_caption[node] = (x, yC)

        # create figure object
        fig = plt.figure()

        # draw labeled nodes
        for node, attr in G.nodes(data = True):
            type = attr['params']['type']
            typeid = attr['params']['type_id']
            isvisible = attr['params']['visible']
            label = attr['label']

            #weight_sum = 0.0
            #for (n1, n2, edge_attr) in G.edges(nbunch = [node], data = True):
                #weight_sum += np.abs(G[n1][n2]['weight'])

            #weight_sum = min(0.01 + 0.3 * weight_sum, 1)
            ##c = 1 - weight_sum
            #c = 0.5
            #print isvisible
            color = {
                True: {
                    'bg':   (0.27, 0.51, 0.70, 1.0),
                    'font': (0.0, 0.0, 0.0, 1.0) },
                False: {
                    'bg':   (0.8, 0.8, 0.8, 1.0),
                    'font': (0.0, 0.0, 0.0, 1.0) }
            }[isvisible]

            # draw node
            nx.draw_networkx_nodes(
                G, pos,
                node_size  = graph_node_size,
                linewidths = graphLineWidth,
                nodelist   = [node],
                node_shape = 'o',
                node_color = color['bg'])

            # draw node label
            node_font_size = \
                1.5 * graph_font_size / np.sqrt(max(len(node) - 1, 1))
            nx.draw_networkx_labels(
                G, pos,
                font_size = node_font_size,
                labels = {node: label},
                font_weight = 'normal',
                font_color = color['font'])

            # draw node caption
            if self.settings['node_caption'] and isvisible:
                if not node in nodeCaption:
                    continue 
                nx.draw_networkx_labels(
                    G, pos_caption,
                    font_size = 0.75 * graph_font_size,
                    labels = {node: ' $' + '%d' % (100 * nodeCaption[node]) + '\%$'},
                    font_weight = 'normal')

        # draw labeled edges
        for (v, h) in G.edges():

            if self.settings['edge_weight'] == 'adjacency' \
                or not self.settings['edge_color']:
                color = 'black'
            elif G[v][h]['weight'] < 0.0:
                color = 'red'
            else:
                color = 'green'

            if np.abs(G[v][h]['weight']) > self.settings['edge_threshold']:

                if self.settings['edge_color']:
                    edgeLineWidth = np.abs(np.abs(G[v][h]['weight'])) \
                        * graphLineWidth * self.settings['edge_zoom']
                else:
                    edgeLineWidth = graphLineWidth

                # draw edges
                nx.draw_networkx_edges(
                    G, pos,
                    width = edgeLineWidth,
                    edgelist = [(v, h)],
                    edge_color = color,
                    arrows = True,
                    alpha = 1.0)

                # draw edge labels
                if self.settings['edge_caption'] != 'none' and self.settings['edge_weight'] != 'adjacency':
                    size = graph_font_size / 1.5
                    label = ' $' + ('%.2g' % (np.abs(G[v][h]['weight']))) + '$'
                    nx.draw_networkx_edge_labels(
                        G, pos,
                        edge_labels = {(v, h): label},
                        font_color = color,
                        clip_on = False,
                        font_size = size,
                        font_weight = 'normal')

        # draw figure title / caption
        if self.settings['show_figure_caption']:
            
            # draw title
            plt.figtext(.5, .85, title, fontsize = 10, ha = 'center')

            if self.settings['node_caption']:

                # draw caption
                if caption == None:
                    if edges == 'weights':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    elif edges == 'adjacency':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    plt.figtext(.5, .11, label_text, fontsize = 9, ha = 'center')
                else:
                    plt.figtext(.5, .11, caption, fontsize = 9, ha = 'center')

        plt.axis('off')

        # output
        if file:
            plt.savefig(file, dpi = self.settings['dpi'])
        else:
            plt.show()

        # clear current figure object and release memory
        plt.clf()
        plt.close(fig)

        return True
    
class adjacencyGraph(layerGraph):
    
    def getDefaults(self):
        return {
            'edge_threshold': 0.0,
            'edge_weight': 'adjacency',
            'node_caption': None,
            'edge_caption': None }
    
    def getEdgeWeights(self, model):
        params = model.system.getParams()
        A = params['A']
        edge_weight = {}
        for v, v_label in enumerate(params['v']['label']):
            for h, h_label in enumerate(params['h']['label']):
                edge_weight[(h_label, v_label)] = A[v, h] * 0.1
                edge_weight[(v_label, h_label)] = A[v, h] * 0.1

        return edge_weight

class weightGraph(layerGraph):

    def getDefaults(self):
        return {
            'edge_threshold': 0.0,
            'edge_weight': 'weights',
            'node_caption': 'relapprox',
            'edge_caption': None }
    
    def getEdgeWeights(self, model):
        
        params = model.system.getLinkParams()
        weights = {}
        
        for edge in params:
            if params[edge]['A']:
                weights[(edge[0], edge[1])] = params[edge]['W']
                weights[(edge[1], edge[0])] = params[edge]['W']

        return weights
