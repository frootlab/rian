# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import importlib
import os
import networkx as nx
import numpy as np
import nemoa
from flab.base import call, otree
from nemoa.plot import Plot, network, heatmap, histogram

def filetypes():
    """Get supported image filetypes."""
    return Plot.filetypes()

def save(model, path = None, filetype = None, plot = None, **kwds):
    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
    except ImportError:
        raise ValueError("""could not plot model '%s':
            plot type '%s' is not supported.""" %  (model.name, plot))

    # create plot of model
    plot = getattr(module, class_name)(**kwds)

    # assert units
    mapping = model.system.mapping
    in_units = model.system.get('units', layer=mapping[0])
    out_units = model.system.get('units', layer=mapping[-1])
    if not isinstance(plot._config['units'], tuple) \
        or not isinstance(plot._config['units'][0], list) \
        or not isinstance(plot._config['units'][1], list):
        plot._config['units'] = (in_units, out_units)

    # get information about relation
    if plot._config['show_title']:
        rel_id = call.parse(plot._config['relation'])[0]
        rel_dict = model.system.get('algorithm', rel_id,
            category = ('system', 'relation', 'evaluation'))
        rel_name = rel_dict['name']
        plot._config['title'] = rel_name.title()

    # create plot
    if plot.create(model): plot.save(path)

    plot.release()

    return path

def show(model, plot = None, *args, **kwds):

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
    except ImportError:
        raise ValueError("""could not plot model '%s':
            plot type '%s' is not supported.""" % (model.name, plot))

    # create plot of model
    plot = getattr(module, class_name)(*args, **kwds)

    # update units
    mapping = model.system.mapping
    in_units = model.system.get('units', layer = mapping[0])
    out_units = model.system.get('units', layer = mapping[-1])
    if not isinstance(plot._config.get('units', None), tuple) \
        or not isinstance(plot._config['units'][0], list) \
        or not isinstance(plot._config['units'][1], list):
        plot._config['units'] = (in_units, out_units)

    # get information about relation
    if plot._config['show_title']:
        rel_id = plot._config.get('relation', 'correlation').split('(')[0]
        rel_dict = model.system.get('algorithm', rel_id,
            category = ('system', 'relation', 'evaluation'))
        rel_name = rel_dict['name']
        plot._config['title'] = rel_name.title()

    # create and show plot
    if plot.create(model): plot.show()

    # clear figures and release memory
    plot.release()

    return True

class Graph(network.Graph2D):

    def create(self, model):
        # set plot defaults
        self.set_default({
            'show_legend': True,
            'legend_fontsize': 9.0,
            'graph_layout': 'layer',
            'units': (None, None),
            'relation': 'induction',
            'preprocessing': None,
            'measure': 'error',
            'statistics': 10000,
            'transform': '',
            'edge_normalize': 'auto',
            'sign': None,
            'filter': None,
            'cutoff': 0.5,
            'node_caption': 'accuracy' })

        # get observables from model
        units = self._config.get('units')
        if not isinstance(units, tuple) \
            or not isinstance(units[0], list) \
            or not isinstance(units[1], list):
            mapping = model.system.mapping
            src = model.system.get('units', layer = mapping[0])
            tgt = model.system.get('units', layer = mapping[-1])
            units = (src, tgt)
        edges = [(u, v) for u in units[0] for v in units[1] if v != u]

        # calculate edge weights from 'weight' relation
        relarg = self._config.get('relation', '')
        rel_name = relarg.split('(')[0]
        W = model.evaluate('system', 'relations', rel_name,
            preprocessing = self._config['preprocessing'],
            measure = self._config['measure'],
            statistics = self._config['statistics'],
            transform = self._config['transform'])
        if not isinstance(W, dict):
            raise ValueError(
                "could not create relation graph: "
                "invalid weight relation '%s'" % rel_name)
        rel_about = model.system.get('algorithm', rel_name,
            category = ('system', 'relation', 'evaluation'))

        # calculate edge filter from 'filter' relation
        # default: use the same relation, as used for weights
        if not self._config['filter'] or self._config['filter'] == \
            self._config['relation']: F = W
        else: F = model.evaluate('system', 'relations',
            self._config['filter'],
            preprocessing = self._config['preprocessing'],
            measure = self._config['measure'],
            statistics = self._config['statistics'])
        if not isinstance(F, dict): raise ValueError(
            "could not create relation graph: "
            "invalid filter relation '%s'!" % self._config['filter'])

        # create filter mask from filter relation (parameter: 'cutoff')
        # and update list of edges
        bound = self._config['cutoff'] * F['std']
        edges = [edge for edge in edges if not -bound < F[edge] < bound]
        if len(edges) == 0: raise Warning(
            "could not create relation graph: "
            "no relation passed threshold (%.2f)!" % bound)

        # calculate edge signs from 'sign' relation
        # default: use the same relation, as used for weights
        rel_sign_name = self._config.get('sign')
        if rel_sign_name is None:
            rel_sign_name = rel_name
            rel_sign_about = rel_about
        else:
            rel_sign_about = model.system.get(
                'algorithm', rel_sign_name,
                category = ('system', 'relation', 'evaluation'))
        signed = rel_sign_about.get('signed', False)
        if signed:
            if rel_sign_name == rel_name: sr = W
            else: sr = model.evaluate('system', 'relations',
                rel_sign_name,
                preprocessing = self._config['preprocessing'],
                measure = self._config['measure'],
                statistics = self._config['statistics'])
            if not isinstance(sr, dict): raise ValueError(
                "could not create relation graph: "
                "invalid sign relation!")
            S = {edge: 2. * (float(sr[edge] > 0.) - 0.5) \
                for edge in edges}

        # create graph and set attributes
        G = nx.DiGraph(name = rel_about.get('name'))

        # graph is directed if and only if relation is directed
        G.graph['directed'] = rel_about.get('directed')

        # add edges and edge attributes to graph
        if self._config['edge_normalize'] in [None, 'auto']:
            normalize = not rel_about.get('normal')
        elif self._config['edge_normalize'] in [True, False]:
            normalize = self._config['edge_normalize']
        else: raise ValueError(
            "could not create relation graph: "
            "invalid value for parameter 'edge_normalize'")

        # add nodes with attributes
        nodes = units[0] + units[1]
        for node in nodes:
            attr = model.network.get('node', node)
            if attr is None: continue
            params = attr.get('params', {})
            G.add_node(node,
                label = params.get('label'),
                group = params.get('layer'))
            issrc, istgt = node in units[0], node in units[1]
            if issrc and istgt: node_type = 'transit'
            elif issrc and not istgt: node_type = 'source'
            elif not issrc and istgt: node_type = 'target'
            else: node_type = 'isolated'
            layout = self.get_node_layout(node_type)
            G.node[node].update(layout)

        # add edges with attributes
        for (u, v) in edges:
            if u == v: continue
            value = W[(u, v)]
            weight = np.absolute(value / W['std'] \
                if normalize else value)
            if signed: color = \
                {1: 'green', 0: 'black', -1: 'red'}[S.get((u, v))]
            else: color = 'black'
            G.add_edge(u, v, weight = weight, color = color,
                visible = True)

        # normalize weights (optional)
        if normalize:
            mean = np.mean([data.get('weight', 0.) \
                for (u, v, data) in G.edges(data = True)])
            for (u, v, data) in G.edges(data = True):
                G.edges[u, v]['weight'] = data['weight'] / mean

        # graph layout specific attributes
        graph_layout = self._config.get('graph_layout', None)
        if graph_layout == 'layer':
            for node in G.nodes():
                attr = model.network.get('node', node)
                params = attr.get('params', {})
                G.node[node].update({
                    'layer': params.get('layer'),
                    'layer_id': params.get('layer_id'),
                    'layer_sub_id': params.get('layer_sub_id')})

        # create plot
        return self.plot(G)

class Heatmap(heatmap.Heatmap):

    def create(self, model):

        # set plot defaults
        self.set_default({
            'units': (None, None),
            'relation': 'correlation',
            'preprocessing': None,
            'measure': 'error',
            'statistics': 10000,
            'transform': '' })

        # get observables from model
        if not isinstance(self._config.get('units', None), tuple) \
            or not isinstance(self._config['units'][0], list) \
            or not isinstance(self._config['units'][1], list):
            mapping = model.system.mapping
            iunits = model.system.get('units', layer = mapping[0])
            ounits = model.system.get('units', layer = mapping[-1])
            self._config['units'] = (iunits, ounits)
        units = self._config['units']
        pairs = []
        for i in units[0]:
            for o in [u for u in units[1] if u != i]:
                pairs.append((i, o))

        # update y-labels from model inputs and x-labels from model outputs
        self._config['y_labels'] = units[0]
        self._config['x_labels'] = units[1]

        # evaluate relations
        R = model.evaluate('system', 'relations',
            self._config['relation'],
            preprocessing = self._config['preprocessing'],
            measure = self._config['measure'],
            statistics = self._config['statistics'],
            transform = self._config['transform'])
        if not isinstance(R, dict):
            raise ValueError(
                "could not create histogram: "
                "invalid relation '%s'!" % self._config['relation'])

        # convert relation dictionary to matrix
        matrix = np.zeros((len(units[0]), len(units[1])))
        for ni, i in enumerate(units[0]):
            for no, o in enumerate(units[1]):
                matrix[ni, no] = R[(i, o)]

        # update title by evaluated relation
        if self._config['show_title']:
            rel_id = call.parse(self._config['relation'])[0]
            rel_dict = model.system.get('algorithm', rel_id,
                category = ('system', 'relation', 'evaluation'))
            rel_name = rel_dict['name']
            self._config['title'] = rel_name.title()

        # create plot
        return self.plot(matrix)

class Histogram(histogram.Histogram):

    def create(self, model):

        # Set plot defaults
        self.set_default({
            'evaluation': 'correlation',
            'units': (None, None),
            'preprocessing': None,
            'measure': 'error',
            'statistics': 10000,
            'transform': '' })

        # Get information about evaluation algorithm
        rel_id = call.parse(self._config['evaluation'])[0]
        rel_dict = model.system.get('algorithm', rel_id,
            category = ('system', 'relation', 'evaluation'))

        # update title by evaluation name
        if self._config['show_title'] \
            and not isinstance(self._config['title'], str):
            self._config['title'] = rel_dict.get('name').title()

        # get observables from model
        if not isinstance(self._config.get('units', None), tuple) \
            or not isinstance(self._config['units'][0], list) \
            or not isinstance(self._config['units'][1], list):
            mapping = model.system.mapping
            iunits = model.system.get('units', layer = mapping[0])
            ounits = model.system.get('units', layer = mapping[-1])
            self._config['units'] = (iunits, ounits)
        units = self._config['units']
        pairs = []
        for i in units[0]:
            for o in [u for u in units[1] if u != i]:
                pairs.append((i, o))

        # update y-labels from model inputs and x-labels from model outputs
        self._config['y_labels'] = units[0]
        self._config['x_labels'] = units[1]

        # apply evaluation
        R = model.evaluate('system', 'relations',
            self._config['evaluation'],
            preprocessing = self._config['preprocessing'],
            measure = self._config['measure'],
            statistics = self._config['statistics'],
            transform = self._config['transform'])
        if not isinstance(R, dict):
            raise ValueError(
                "could not create histogram: "
                "invalid evaluation '%s'!" % self._config['evaluation'])

        # convert evaluation dictionary to data array
        data = np.array([R[pair] for pair in pairs])

        # create plot
        return self.plot(data)
