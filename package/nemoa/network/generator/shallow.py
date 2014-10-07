# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

class Generator:

    def __init__(self):
        pass

    def _get_nodes_from_layers(self):
        """Create nodes from layers."""
        self._config['nodes'] = {}
        self._config['label_format'] = 'generic:string'
        for layer in self._config['layer']:
            nodeNumber = self._config['params'][layer + '.size']
            self._config['nodes'][layer] = \
                [layer + str(i) for i in xrange(1, nodeNumber + 1)]
        return True

    def _get_visible_nodes_from_dataset(self, dataset):
        """Create nodes from dataset."""

        self._config['visible'] = []
        self._config['label_format'] = 'generic:string'
        if not 'nodes' in self._config: self._config['nodes'] = {}
        if not 'layer' in self._config: self._config['layer'] = []
        groups = dataset.get('groups')
        for group in groups:
            if not group in self._config['visible']:
                self._config['visible'].append(group)
            self._config['layer'].append(group)
            self._config['nodes'][group] = groups[group]
        return True

    def _get_hidden_nodes_from_system(self, system):
        """Create nodes from system."""

        self._config['hidden'] = []
        self._config['label_format'] = 'generic:string'
        if not 'nodes' in self._config: self._config['nodes'] = {}
        if not 'layer' in self._config: self._config['layer'] = []
        visible = system.get('units', layer = 'visible')
        hidden = system.get('units', layer = 'hidden')
        for unit in hidden:
            (group, label) = unit.split(':')
            if not group in self._config['layer']:
                self._config['layer'].append(group)
            if not group in self._config['hidden']:
                self._config['hidden'].append(group)
            if not group in self._config['nodes']:
                self._config['nodes'][group] = []
            self._config['nodes'][group].append(label)
        return True

    def _get_edges_from_layers(self):
        self._config['edges'] = {}
        for l in xrange(0, len(self._config['layer']) - 1):
            layerFrom = self._config['layer'][l]
            layerTo = self._config['layer'][l + 1]
            edge_layer = (layerFrom, layerTo)
            if not edge_layer in self._config['edges']:
                nodesFrom = self._config['nodes'][layerFrom]
                nodesTo = self._config['nodes'][layerTo]
                self._config['edges'][edge_layer] = [(nodeFrom, nodeTo)
                    for nodeFrom in nodesFrom
                    for nodeTo in nodesTo]
        return True
