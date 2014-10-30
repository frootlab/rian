# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def types():
    """Get supported layer network types for network building."""

    return {
        'autoencoder': 'Autoencoder',
        'dbn': 'Deep Beliefe Network',
        'factor': 'Factor Graph',
        'shallow': 'Shallow Network'
    }

def build(type = None, *args, **kwargs):
    """Build layered network from parameters and dataset."""

    if type == 'autoencoder': return AutoEncoder(**kwargs).build()
    if type == 'dbn': return DBN(**kwargs).build()
    if type == 'factor': return Factor(**kwargs).build()
    if type == 'shallow': return Shallow(**kwargs).build()

    return False

class AutoEncoder:
    """Build autoencoder compatible network from parameters."""

    settings = {
        'dataset': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def build(self):
        return {}

class DBN:
    """Build Deep Belife Network compatible network from parameters."""

    settings = {
        'dataset': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def build(self):
        return {}

class Factor:
    """Build factor graph from parameters."""

    settings = {
        'name': 'factor',
        'factors': None,
        'visible_nodes': ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
        'hidden_nodes': ['n1', 'n2', 'n3', 'n4'],
        'visible_layer': 'visible',
        'hidden_layer': 'hidden',
        'visible_type': 'gauss',
        'hidden_type': 'sigmoid',
        #'visible_params': {},
        #'hidden_params': {},
        'labelformat': 'generic:string',
        'labelencapsulate': False }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def build(self):
        network_name = self.settings['name']
        network_labelfmt = self.settings['labelformat']
        network_labelenc = self.settings['labelencapsulate']
        visible_nodes = self.settings['visible_nodes']
        hidden_nodes = self.settings['hidden_nodes']
        visible_layer = self.settings['visible_layer']
        hidden_layer = self.settings['hidden_layer']
        #visible_params = self.settings['visible_params']
        #hidden_params = self.settings['hidden_params']
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
        if not 'visible' in visible_params:
            visible_params['visible'] = True
        if not 'type' in visible_params:
            visible_params['type'] = visible_type
        if not 'visible' in hidden_params:
            hidden_params['visible'] = False
        if not 'type' in hidden_params:
            hidden_params['type'] = hidden_type

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
    """Build shallow network from parameters."""

    settings = {
        'dataset': None }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def build(self):
        return {}

    #def _get_nodes_from_layers(self):
        #"""Create nodes from layers."""
        #self._config['nodes'] = {}
        #self._config['labelformat'] = 'generic:string'
        #for layer in self._config['layer']:
            #nodeNumber = self._config['params'][layer + '.size']
            #self._config['nodes'][layer] = \
                #[layer + str(i) for i in xrange(1, nodeNumber + 1)]
        #return True

    #def _get_visible_nodes_from_dataset(self, dataset):
        #"""Create nodes from dataset."""

        #self._config['visible'] = []
        #self._config['labelformat'] = 'generic:string'
        #if not 'nodes' in self._config: self._config['nodes'] = {}
        #if not 'layer' in self._config: self._config['layer'] = []
        #groups = dataset.get('groups')
        #for group in groups:
            #if not group in self._config['visible']:
                #self._config['visible'].append(group)
            #self._config['layer'].append(group)
            #self._config['nodes'][group] = groups[group]
        #return True

    #def _get_hidden_nodes_from_system(self, system):
        #"""Create nodes from system."""

        #self._config['hidden'] = []
        #self._config['labelformat'] = 'generic:string'
        #if not 'nodes' in self._config: self._config['nodes'] = {}
        #if not 'layer' in self._config: self._config['layer'] = []
        #visible = system.get('units', layer = 'visible')
        #hidden = system.get('units', layer = 'hidden')
        #for unit in hidden:
            #(group, label) = unit.split(':')
            #if not group in self._config['layer']:
                #self._config['layer'].append(group)
            #if not group in self._config['hidden']:
                #self._config['hidden'].append(group)
            #if not group in self._config['nodes']:
                #self._config['nodes'][group] = []
            #self._config['nodes'][group].append(label)
        #return True

    #def _get_edges_from_layers(self):
        #self._config['edges'] = {}
        #for l in xrange(0, len(self._config['layer']) - 1):
            #layerFrom = self._config['layer'][l]
            #layerTo = self._config['layer'][l + 1]
            #edge_layer = (layerFrom, layerTo)
            #if not edge_layer in self._config['edges']:
                #nodesFrom = self._config['nodes'][layerFrom]
                #nodesTo = self._config['nodes'][layerTo]
                #self._config['edges'][edge_layer] = [(nodeFrom, nodeTo)
                    #for nodeFrom in nodesFrom
                    #for nodeTo in nodesTo]
        #return True
