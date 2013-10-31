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
            'node_caption': None,
            'edge_zoom': 2.0
        }

    def create(self, model, file = None):

        # get title
        if 'title' in self.settings:
            title = self.settings['title']
        else:
            title = model.getName()

        # use captions
        if self.settings['node_caption']:

            # get node captions
            node_caption = model._getUnitEval(func = self.settings['node_caption'])

            # get model caption
            funcName = model.system.getUnitEvalInfo(func = self.settings['node_caption'])['name']
            model_caption = float(sum([node_caption[u] for u in node_caption.keys()]))/len(node_caption)
            caption  = 'Average ' + funcName + ': $\mathrm{%.1f' % (100 * model_caption) + '\%}$'

        # get edge weights
        edge_weight = self.getEdgeWeights(model)

        # labels
        visibleLabels = model.network.getNodeGroups(type = 'visible')
        hiddenLabels = model.network.getNodeGroups(type = 'hidden')
        lbl = nemoa.common.dictMerge(visibleLabels, hiddenLabels)

        # graph
        G = model.network.graph

        # calculate sizes
        zoom = 1.0
        scale = min(250.0 / max([len(lbl[a]) for a in lbl.keys()]), 30.0)
        graph_node_size = scale ** 2
        graph_font_size = 0.4 * scale
        graph_caption_factor = 0.5 + 0.003 * scale
        graphLineWidth = 0.5

        # calculate node positions for 'stack layout'
        pos = {}
        pos_caption = {}
        for node, attr in G.nodes(data = True):
            i = 1.0 / len(lbl[attr['params']['type']])
            x_node = (attr['params']['type_node_id'] + 0.5) * i
            y_node = 1 - attr['params']['type_id'] * 0.5
            y_caption = (1 - attr['params']['type_id']) * graph_caption_factor + 0.5

            pos[node] = (x_node, y_node)
            pos_caption[node] = (x_node, y_caption)

        # create figure object
        fig = plt.figure()

        # draw labeled nodes
        for node, attr in G.nodes(data = True):
            type = attr['params']['type']
            typeid = attr['params']['type_id']
            isvisible = attr['params']['visible']
            label = attr['label']

            weight_sum = 0
            for (n1, n2, edge_attr) in G.edges(nbunch = [node], data = True):
                if not (n1, n2) in edge_weight:
                    continue
                weight_sum += np.abs(edge_weight[(n1, n2)])

            weight_sum = min(0.01 + 0.3 * weight_sum, 1)
            c = 1 - weight_sum
            color = {
                0: (1, c, c, 1),
                1: (c, 1, c,  1),
                2: (1, 1, c, 1)
            }[typeid]

            # draw node
            nx.draw_networkx_nodes(
                G, pos,
                node_size  = graph_node_size,
                linewidths = graphLineWidth,
                nodelist   = [node],
                node_shape = 'o',
                node_color = color)

            # draw node label
            node_font_size = \
                1.5 * graph_font_size / np.sqrt(max(len(node) - 1, 1))
            nx.draw_networkx_labels(
                G, pos,
                font_size = node_font_size,
                labels = {node: label},
                font_weight = 'normal')

            # draw node caption
            if self.settings['node_caption'] and isvisible:
                nx.draw_networkx_labels(
                    G, pos_caption,
                    font_size = 0.65 * graph_font_size,
                    labels = {node: ' $' + '%d' % (100 * node_caption[node]) + '\%$'},
                    font_weight = 'normal')

        # draw labeled edges
        for (v, h) in G.edges():

            if not (v, h) in edge_weight:
                continue

            if self.settings['edge_weight'] == 'adjacency':
                color = 'black'
            elif edge_weight[(v, h)] < 0:
                color = 'red'
            else:
                color = 'green'

            if np.abs(edge_weight[(v, h)]) > self.settings['edge_threshold']:

                edgeLineWidth = np.abs(edge_weight[(v, h)]) * graphLineWidth * self.settings['edge_zoom']

                # draw edges
                nx.draw_networkx_edges(
                    G, pos,
                    width = edgeLineWidth,
                    edgelist = [(v, h)],
                    edge_color = color,
                    alpha = 1.0)

                # draw edge labels
                if self.settings['edge_caption'] != 'none' and self.settings['edge_weight'] != 'adjacency':
                    size = graph_font_size / 1.5
                    label = ' $' + ('%.2g' % (np.abs(edge_weight[(v, h)]))) + '$'
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
            plt.figtext(.5, .92, title, fontsize = 10, ha = 'center')

            if self.settings['node_caption']:

                # draw caption
                if caption == None:
                    if edges == 'weights':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    elif edges == 'adjacency':
                        label_text = r'$\mathbf{Network:}\,\mathrm{%s}$' % (model.network.graph)
                    plt.figtext(.5, .06, label_text, fontsize = 10, ha = 'center')
                else:
                    plt.figtext(.5, .06, caption, fontsize = 10, ha = 'center')

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

    def getEdgeWeights(self, model):
        A = model.system.params['A']
        edge_weight = {}
        for v, v_label in enumerate(model.system.params['v']['label']):
            for h, h_label in enumerate(model.system.params['h']['label']):
                edge_weight[(h_label, v_label)] = A[v, h]
                edge_weight[(v_label, h_label)] = A[v, h]

        return edge_weight

    
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
