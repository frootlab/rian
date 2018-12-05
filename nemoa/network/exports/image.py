# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import importlib
import numpy as np
from nemoa.plot import Plot, network

def filetypes():
    """Get supported image filetypes."""
    return Plot.filetypes()

def show(network, plot=None, **kwds):

    # get class for plotting from attribute 'plot'
    if not plot:
        plot = 'graph'

    # get plot class and module name
    cname = plot.lower().title()
    mname = save.__module__
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname):
            raise ImportError()
    except ImportError:
        raise ValueError(
            "could not plot graph '%s': "
            "plot type '%s' is not supported." % (network.name, plot))

    # create and show plot
    plot = getattr(module, cname)(**kwds)
    if plot.create(network):
        plot.show()

    plot.release()
    return True

def save(network, path=None, filetype=None, plot=None, **kwds):

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # get class for plotting from attribute 'plot'
    if not plot:
        plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):
            raise ImportError()
    except ImportError:
        raise ValueError("""could not plot network '%s':
            plot type '%s' is not supported.""" % (network.name, plot))

    # create plot instance
    plot = getattr(module, class_name)(**kwds)

    # create plot and save to file
    if plot.create(network):
        plot.save(path)

    # clear figures and release memory
    plot.release()

    return path

class Graph(network.Graph2D):

    def create(self, network):
        from nemoa.math import curve, graph

        # set plot defaults
        self.set_default({
            'show_legend': True,
            'legend_fontsize': 9.0,
            'graph_layout': 'layer',
            'node_caption': 'accuracy',
            'node_groupby': None,
            'node_color': True,
            'edge_color': False,
            'edge_caption': None,
            'edge_weight': 'intensity',
            'edge_threshold': 0.,
            'edge_transform': 'softstep',
            'edge_sign_normalize': True})

        # copy graph from model graph
        G = network.get('graph', type='graph')

        # copy graph attributes from graph 'params'
        params = G.graph.get('params', {})
        if 'directed' in params:
            G.graph['directed'] = params['directed']

        # create edge attribute 'weight'
        edgeattr = self._config.get('edge_weight', None)
        normalize = self._config.get('edge_normalize', None)
        threshold = self._config.get('edge_threshold', None)
        transform = self._config.get('edge_transform', None)

        # calculate mean weight for normalization (optional)
        if bool(normalize):
            absmean = np.absolute(np.mean(
                [data['params'].get(edgeattr, 0.) \
                for (u, v, data) in G.edges(data=True)]))
            if absmean == 0.:
                normalize = None

        for (u, v, data) in G.edges(data=True):
            weight = data['params'].get(edgeattr, None)
            if weight is None:
                if 'weight' in data:
                    data.pop('weight')
                continue

            # threshold weights (optional)
            if bool(threshold) and threshold > np.absolute(weight):
                G.remove_edge(u, v)
                continue

            # create edge attribute 'color' (optional)
            if self._config.get('edge_color', False):
                if weight > 0.:
                    G.edges[u, v]['color'] = \
                        self._config.get('edge_poscolor', 'green')
                else:
                    G.edges[u, v]['color'] = \
                        self._config.get('edge_negcolor', 'red')

            # create edge attribute 'caption' (optional)
            if self._config.get('edge_caption'):
                caption = ' $' + ('%.2g' % (weight)) + '$'
                G.edges[u, v]['caption'] = caption

            # normalize weights (optional)
            if bool(normalize):
                weight /= absmean

            # transform weights (optional)
            if transform == 'softstep':
                weight = curve.softstep(weight)

            G.edges[u, v]['weight'] = weight

        # normalize signs of weights (optional)
        if self._config.get('edge_sign_normalize'):
            number_of_layers = len(G.graph['params']['layer'])
            if number_of_layers % 2 == 1:
                sign_sum = np.sum(
                    [np.sign(G.edges[edge].get('weight', 0.))
                    for edge in G.edges()])
                if sign_sum < 0.:
                    for edge in G.edges():
                        if 'weight' in G.edges[edge]:
                            G.edges[edge]['weight'] *= -1

        nodes = {n: data for n, data in G.nodes(data=True)}

        # copy node attributes 'label' and 'visible' from unit params
        for node, data in G.nodes(data=True):
            params = data.get('params', {})
            data.update({
                'label': params.get('label', str(node)),
                'visible': params.get('visible', True),
                'layer': params.get('layer', None),
                'layer_id': params.get('layer_id', None),
                'layer_sub_id': params.get('layer_sub_id', None)})

        # update node attribute 'group'
        groupby = self._config.get('node_groupby', None)
        if groupby is not None:
            for node, data in G.nodes(data=True):
                node_params = data.get('params', {})
                data['group'] = node_params.get(groupby)
        else:
            is_layer = graph.is_layered(G)
            is_directed = graph.is_directed(G)
            if is_layer and not is_directed:
                for node, data in G.nodes(data=True):
                    gid = int(data.get('visible', True))
                    data['group'] = {0: 'latent', 1: 'observable'}[gid]
            elif is_layer and is_directed:
                layers = graph.get_layers(G)
                ilayer, olayer = layers[0], layers[-1]
                for node, data in G.nodes(data=True):
                    gid = int(node in ilayer) \
                        + 2 * int(node in olayer)
                    data['group'] = {0: 'latent', 1: 'source',
                        2: 'target', 3: 'transit'}[gid]
            else:
                for node, data in G.nodes(data=True):
                    gid = int(data.get('visible', True))
                    data['group'] = {0: 'latent', 1: 'observable'}[gid]

        # update node attributes for layout
        groups = graph.get_groups(G, attribute='group')
        for group in sorted(groups.keys()):
            if group == '':
                continue
            layout = self.get_node_layout(group)
            group_label = layout.get('label', {
                True: str(groupby),
                False: 'not ' + str(groupby)}[group] \
                if isinstance(group, bool) else str(group).title())
            for node in groups.get(group, []):
                node_params = nodes[node].get('params')
                G.node[node].update({
                    'label': node_params.get('label', str(node)),
                    'group': group_label})
                G.node[node].update(layout)

        # prepare parameters
        if self._config.get('title') is None:
            self._config['title'] = network.fullname

        # create plot
        return self.plot(G)
