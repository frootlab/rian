# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
from flab.base import otree

def types():
    """Get supported layer network types for network building."""

    return {
        'autoencoder': 'Autoencoder',
        'factor': 'Factor Graph',
        'multilayer': 'Feedforward MultiLayer Network',
        'shallow': 'Shallow Network'
    }

def build(type = None, *args, **kwds):
    """Build layered network from parameters and dataset."""

    if type == 'factor': return Factor(*args, **kwds).build()
    if type == 'multilayer': return MultiLayer(*args, **kwds).build()
    if type == 'autoencoder': return AutoEncoder(*args, **kwds).build()
    if type == 'shallow': return Shallow(*args, **kwds).build()

    return False

class AutoEncoder:
    """Build autoencoder network from given columns or dataset.

    Example:

        network = nemoa.network.create('autoencoder',
            columns = ['i1', 'i2', 'o1'],
            shape = [6, 3, 6])

    """

    settings = None
    default = {'name': 'autoencoder'}

    def __init__(self, dataset = None, *args, **kwds):
        self.settings = {**self.default, **kwds}

        # columns
        if 'columns' in self.settings: columns = self.settings['columns']
        elif otree.has_base(dataset, 'Dataset'): columns = dataset.columns
        else: columns = ['i1', 'i2', 'i3', 'i4', 'o1', 'o2']

        self.settings['inputs'] = columns
        self.settings['outputs'] = columns

        # shape
        if 'shape' not in self.settings:
            size = len(columns)
            self.settings['shape'] = [2 * size, size, 2 * size]

    def build(self):
        return MultiLayer(**self.settings).build()

class MultiLayer:
    """Build multilayer network."""

    settings = None
    default = {
        'name': 'multilayer',
        'inputs': ['i1', 'i2', 'i3', 'i4'],
        'outputs': ['o1', 'o2'],
        'shape': [4, 2, 4],
        'visibletype': 'gauss',
        'hiddentype': 'sigmoid',
        'labelformat': 'generic:string' }

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def build(self):
        name = self.settings['name']
        lblfmt = self.settings['labelformat']
        inputs = self.settings['inputs']
        outputs = self.settings['outputs']
        hidden = self.settings['shape']

        # layers
        layers = ['i']
        layers += ['h%i' % (l + 1) for l in range(len(hidden))]
        layers += ['o']

        # layer parameters
        params = {}
        for lid, layer in enumerate(layers):
            if lid in [0, len(layers) - 1]:
                params[layer] = {
                    'visible': True,
                    'type': self.settings['visibletype'] }
            else:
                params[layer] = {
                    'visible': False,
                    'type': self.settings['hiddentype'] }

        # nodes
        nodes = {
            'i': self.settings['inputs'],
            'o': self.settings['outputs'] }
        for lid, lsize in enumerate(hidden):
            nodes['h%i' % (lid + 1)] = ['n%i' % (n)
                for n in range(1, lsize + 1)]

        # edges
        edges = {}
        for lid in range(0, len(layers) - 1):
            srclayer = layers[lid]
            tgtlayer = layers[lid + 1]
            srcnodes = nodes[srclayer]
            tgtnodes = nodes[tgtlayer]
            edgelayer = (srclayer, tgtlayer)
            edges[edgelayer] = []
            for src in srcnodes:
                for tgt in tgtnodes:
                    edges[edgelayer].append((src, tgt))

        # create network configuration
        return {
            'config': {
                'name': name,
                'type': 'layer.MultiLayer',
                'layer': layers,
                'layers': params,
                'nodes': nodes,
                'edges': edges,
                'labelformat': lblfmt,
                'labelencapsulate': True }}

class Factor:
    """Build factor graph from parameters."""

    settings = None
    default = {
        'name': 'factor',
        'factors': None,
        'visible_nodes': ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
        'hidden_nodes': ['n1', 'n2', 'n3', 'n4'],
        'visible_layer': 'visible',
        'hidden_layer': 'hidden',
        'visible_type': 'gauss',
        'hidden_type': 'sigmoid',
        'labelformat': 'generic:string',
        'labelencapsulate': False }

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def build(self):
        network_name = self.settings['name']
        network_labelfmt = self.settings['labelformat']
        network_labelenc = self.settings['labelencapsulate']
        visible_nodes = self.settings['visible_nodes']
        hidden_nodes = self.settings['hidden_nodes']
        visible_layer = self.settings['visible_layer']
        hidden_layer = self.settings['hidden_layer']
        visible_params = {}
        hidden_params = {}
        visible_type = self.settings['visible_type']
        hidden_type = self.settings['hidden_type']

        if isinstance(self.settings['factors'], int):
            hidden_nodes = ['n%s' % (n)
                for n in range(1, self.settings['factors'] + 1)]
        network_layer = [visible_layer, hidden_layer]
        network_nodes = {
            visible_layer: visible_nodes,
            hidden_layer: hidden_nodes}
        edge_layer = tuple(network_layer)
        network_edges = {edge_layer: []}
        for v in visible_nodes:
            for h in hidden_nodes:
                network_edges[edge_layer].append((v, h))
        if 'visible' not in visible_params: visible_params['visible'] = True
        if 'type' not in visible_params: visible_params['type'] = visible_type
        if 'visible' not in hidden_params: hidden_params['visible'] = False
        if 'type' not in hidden_params: hidden_params['type'] = hidden_type

        # create network configuration
        network_dict = {
            'config': {
                'name': network_name,
                'type': 'layer.Factor',
                'layer': network_layer,
                'layers': {
                    visible_layer: visible_params,
                    hidden_layer: hidden_params },
                'nodes': network_nodes,
                'edges': network_edges,
                'labelencapsulate': network_labelenc,
                'labelformat': network_labelfmt }}

        return network_dict

class Shallow:
    """Build shallow network."""

    settings = None

    def __init__(self, inputs = None, outputs = None, *args, **kwds):
        self.settings = kwds.copy()
        if inputs: self.settings['inputs'] = inputs
        if outputs: self.settings['outputs'] = outputs
        self.settings['shape'] = []

    def build(self):
        return MultiLayer(**self.settings).build()
