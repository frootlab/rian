# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import copy

class network:

    def __init__(self, config = {}, **kwargs):
        self.cfg = None
        self.graph = None
        self._setConfig(config)

    def _setConfig(self, config):
        """Configure network to given dictionary."""

        # create valid config config
        self.cfg = config.copy() if isinstance(config, dict) else {}

        # 2do -> move functionality to network configuration file!
        # type 'auto' is used for networks
        # wich include all dataset columns as visible units
        if self.cfg['type'] == 'auto':
            self.cfg = {'type': 'auto', 'name': '', 'id': 0}
            return True

        # 2do -> move functionality to network configuration file!
        # type 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self.cfg['type'] == 'autolayer':
            self._getNodesFromLayers()
            self._getEdgesFromNodesAndLayers()
            return self._createLayerGraph()

        # type 'layer' is used for networks
        # wich are manualy defined, using a file
        if self.cfg['type'].lower() in ['layer', 'multilayer']: return \
            self._createLayerGraph()

        return False

    def getConfig(self):
        """Return configuration as dictionary."""
        return self.cfg.copy()

    def _getNodesFromLayers(self):
        """Create nodes from layers."""
        self.cfg['nodes'] = {}
        self.cfg['label_format'] = 'generic:string'
        for layer in self.cfg['layer']:
            nodeNumber = self.cfg['params'][layer + '.size']
            self.cfg['nodes'][layer] = \
                [layer + str(i) for i in range(1, nodeNumber + 1)]
        return True

    def _getVisibleNodesFromDataset(self, dataset):
        """Create nodes from dataset."""

        self.cfg['visible'] = []
        self.cfg['label_format'] = 'generic:string'
        if not 'nodes' in self.cfg: self.cfg['nodes'] = {}
        if not 'layer' in self.cfg: self.cfg['layer'] = []
        groups = dataset.getColGroups()
        for group in groups:
            if not group in self.cfg['visible']:
                self.cfg['visible'].append(group)
            self.cfg['layer'].append(group)
            self.cfg['nodes'][group] = groups[group]
        return True

    def _getHiddenNodesFromSystem(self, system):
        """Create nodes from system."""

        self.cfg['hidden'] = []
        self.cfg['label_format'] = 'generic:string'
        if not 'nodes' in self.cfg: self.cfg['nodes'] = {}
        if not 'layer' in self.cfg: self.cfg['layer'] = []
        (visible, hidden) = system.getUnits()
        for unit in hidden:
            (group, label) = unit.split(':')
            if not group in self.cfg['layer']:
                self.cfg['layer'].append(group)
            if not group in self.cfg['hidden']:
                self.cfg['hidden'].append(group)
            if not group in self.cfg['nodes']:
                self.cfg['nodes'][group] = []
            self.cfg['nodes'][group].append(label)
        return True

    def _getEdgesFromNodesAndLayers(self):
        self.cfg['edges'] = {}
        for l in range(0, len(self.cfg['layer']) - 1):
            layerFrom = self.cfg['layer'][l]
            layerTo = self.cfg['layer'][l + 1]
            edgeLayer = layerFrom + '-' + layerTo
            if not edgeLayer in self.cfg['edges']:
                nodesFrom = self.cfg['nodes'][layerFrom]
                nodesTo = self.cfg['nodes'][layerTo]
                self.cfg['edges'][edgeLayer] = [(nodeFrom, nodeTo)
                    for nodeFrom in nodesFrom
                    for nodeTo in nodesTo]
        return True

    def configure(self, dataset, system):
        """Configure network to dataset and system."""

        # check if network instance is empty
        if self._isEmpty(): return nemoa.log(
            "configuration is not needed: network is 'empty'.")

        # check if dataset instance is available
        if not nemoa.type.isDataset(dataset): return nemoa.log(
            'error', """could not configure network:
            no valid dataset instance given:""")

         # check if system instance is available
        if not nemoa.type.isSystem(system): return nemoa.log(
            'error', """could not configure network:
            no valid system instance given.""")

        nemoa.log("configure network: '%s'" % (self.name()))
        nemoa.setLog(indent = '+1')

        # type: 'auto is used for networks
        # wich are created by datasets (visible units)
        # and systems (hidden units)
        if self.cfg['type'] == 'auto':
            self._getVisibleNodesFromDataset(dataset)
            self._getHiddenNodesFromSystem(system)
            self._getEdgesFromNodesAndLayers()
            self._createLayerGraph()
            nemoa.setLog(indent = '-1')
            return True

        # type: 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self.cfg['type'] == 'autolayer':
            self._getNodesFromLayers()
            self._getEdgesFromNodesAndLayers()
            self._createLayerGraph()
            nemoa.setLog(indent = '-1')
            return True

        # configure network to dataset
        groups = dataset.getColGroups()
        changes = []
        for group in groups:
            if not group in self.cfg['nodes'] \
                or not (groups[group] == self.cfg['nodes'][group]):
                self._createLayerGraph(
                    nodelist = {'type': group, 'list': groups[group]})

        nemoa.setLog(indent = '-1')
        return True

    def _isEmpty(self):
        """Return true if network type is 'empty'."""
        return self.cfg['type'] == 'empty'

    def _createLayerGraph(self, nodelist = None, edgelist = None):
        if not nodelist: nodelist = {'type': None, 'list': []}
        if not edgelist: edgelist = {'type': (None, None), 'list': []}

        # get differences between nodelist and self.cfg['nodes']
        if nodelist['type'] in self.cfg['layer']:
            # count number of nodes to add to nodes
            addNodes = sum([1 for node in nodelist['list']
                if not node in self.cfg['nodes'][nodelist['type']]])
            # count number of nodes to delete from graph
            addNodes = sum([1 for node in self.cfg['nodes'][nodelist['type']]
                if not node in nodelist['list']])

        # update edge list from keyword arguments
        if edgelist['type'][0] in self.cfg['layer'] \
            and edgelist['type'][1] in self.cfg['layer']:
            indexA = self.cfg['layer'].index(edgelist['type'][0])
            indexB = self.cfg['layer'].index(edgelist['type'][1])
            if indexB - indexA == 1:
                edgeLayer = edgelist['type'][0] + '-' + edgelist['type'][1]
                self.cfg['edges'][edgeLayer] = edgelist['list']

        # filter edges to valid nodes
        for i in range(len(self.cfg['layer']) - 1):
            layerA = self.cfg['layer'][i]
            layerB = self.cfg['layer'][i + 1]
            edgeLayer = layerA + '-' + layerB
            filtered = []
            for nodeA, nodeB in self.cfg['edges'][edgeLayer]:
                if not nodeA in self.cfg['nodes'][layerA]: continue
                if not nodeB in self.cfg['nodes'][layerB]: continue
                filtered.append((nodeA, nodeB))
            self.cfg['edges'][edgeLayer] = filtered

        # reset and create new NetworkX graph Instance
        if self.graph == None: self.graph = networkx.Graph()
        else: self.graph.clear()

        # set graph attributes
        self.graph.graph =  {
            'name': self.cfg['name'],
            'type': 'layer',
            'params': { 'layer': self.cfg['layer'] }
        }

        # add nodes to graph
        order = 0
        for layerId, layer in enumerate(self.cfg['layer']):
            visible = layer in self.cfg['visible']
            if nodelist['type'] in self.cfg['layer']:
                if layer == nodelist['type']:
                    if addNodes: nemoa.log("""adding %i nodes
                        to layer '%s'""" % (addNodes, layer))
                    if delNodes: nemoa.log("""deleting %i nodes
                        from layer '%s'""" % (delNodes, layer))
            else:
                if visible: nemoa.log('adding visible layer: \'' + layer + \
                    '\' (' + str(len(self.cfg['nodes'][layer])) + ' nodes)')
                else: nemoa.log('adding hidden layer: \'' + layer + \
                    '\' (' + str(len(self.cfg['nodes'][layer])) + ' nodes)')
            for layerNodeId, node in enumerate(self.cfg['nodes'][layer]):
                id = layer + ':' + node
                if id in self.graph.nodes(): continue

                self.graph.add_node(id,
                    label  = node,
                    order  = order,
                    params = {
                        'type': layer,
                        'layerId': layerId,
                        'layerNodeId': layerNodeId,
                        'visible': visible } )

                order += 1

        # add edges to graph
        order = 0
        for i in range(len(self.cfg['layer']) - 1):
            layerA = self.cfg['layer'][i]
            layerB = self.cfg['layer'][i + 1]
            edgeLayer = layerA + '-' + layerB
            type_id = i

            for (nodeA, nodeB) in self.cfg['edges'][edgeLayer]:
                src_node_id = layerA + ':' + nodeA
                tgt_node_id = layerB + ':' + nodeB

                self.graph.add_edge(
                    src_node_id, tgt_node_id,
                    weight = 0.0,
                    order  = order,
                    params = {'type': edgeLayer, 'layerId': type_id})

                order += 1

        return True

    # accessing nodes

    def node(self, node):
        """Return network information of single node."""
        return self.graph.node[node]

    def nodes(self, **kwargs):
        """get list of nodes with specific attributes
        example nodes(type = 'visible')"""

        # filter search criteria and order entries
        sortedList = [None] * self.graph.number_of_nodes()
        for node, attr in self.graph.nodes(data = True):
            if not kwargs == {}:
                passed = True
                for key in kwargs:
                    if not key in attr['params'] \
                        or not kwargs[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            sortedList[attr['order']] = node
        return [node for node in sortedList if node] # filter empty nodes

    def node_labels(self, **params):
        return [self.graph.node[node]['label'] \
            for node in self.nodes(**params)]

    def getNodeLabels(self, list):
        labels = []
        for node in list:
            if not node in self.graph.node: return None
            labels.append(self.graph.node[node]['label'])
        return labels

    def getNodeGroups(self, type = None):

        # get groups of specific node type
        if type:
            if not type in self.cfg: return nemoa.log('warning',
                "unknown node type '%s'." % (str(type)))
            return {group: self.node_labels(type = group)
                for group in self.cfg[type]}

        # get all groups
        allGroups = {}
        for type in ['visible', 'hidden']:
            groups = {}
            for group in self.cfg[type]:
                groups[group] = self.node_labels(type = group)
            allGroups[type] = groups
        return allGroups

    # accessing layers

    def layer(self, layer):
        """Return dictionary containing information about a layer."""
        nodes = self.nodes(type = layer)
        if not nodes: return None
        fistNode = self.node(nodes[0])['params']
        return {
            'id': fistNode['layerId'],
            'label': fistNode['type'],
            'visible': fistNode['visible'],
            'nodes': nodes}

    def layers(self, **kwargs):
        """Return ordered list of layers by label."""
        layerDict = {self.node(node)['params']['layerId']: \
            {'label': self.node(node)['params']['type']} \
            for node in self.nodes()}
        layerList = [layerDict[layer]['label'] for layer in range(0, len(layerDict))]
        return layerList

    # accessing edges

    def edge(self, edge):
        return self.graph.edge[edge]

    def edges(self, **params):

        # filter search criteria and order entries
        sorted_list = [None] * self.graph.number_of_edges()

        for src, tgt, attr in self.graph.edges(data = True):
            if not params == {}:

                passed = True
                for key in params:
                    if not key in attr['params'] \
                        or not params[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue

            # force order (visible, hidden)
            # TODO: why force order??
            # better force order from input to ouput
            srcLayer = src.split(':')[0]
            tgtLayer = tgt.split(':')[0]

            if srcLayer in self.cfg['visible'] \
                and tgtLayer in self.cfg['hidden']:
                sorted_list[attr['order']] = (src, tgt)
            elif srcLayer in self.cfg['hidden'] \
                and tgtLayer in self.cfg['visible']:
                sorted_list[attr['order']] = (tgt, src)

        # filter empty nodes
        return [edge for edge in sorted_list if edge]

    def edgeLabels(self, **kwargs):
        return [(self.graph.node[src]['label'],
            self.graph.node[tgt]['label']) for src, tgt in self.edges(**kwargs)]

    # get / set

    def _get(self, sec = None):
        dict = {
            'cfg': copy.deepcopy(self.cfg),
            'graph': copy.deepcopy(self.graph) }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set(self, **dict):
        if 'cfg' in dict: self.cfg = copy.deepcopy(dict['cfg'])
        if 'graph' in dict: self.graph = copy.deepcopy(dict['graph'])
        return True

    def save_graph(self, file = None, format = 'gml'):
        if file == None: nemoa.log('error', "no save path was given")

        # create path if not available
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        # everythink seems to be fine
        # nemoa.log("saving graph to %s" % (file))

        if format == 'gml':
            G = self.graph.copy()
            networkx.write_gml(G, file)

    def _isLFFCompatible(self):
        """Test compatibility to layered feed forward networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) All layers of the network are not empty
            (2) The first and last layer of the network are visible,
                the layers between them are hidden
        """

        # test if network contains empty layers
        for layer in self.layers():
            if not len(self.layer(layer)['nodes']) > 0: return nemoa.log(
                'error', 'Feedforward networks do not allow empty layers!')

        # test if and only if the first and the last layer are visible
        for layer in self.layers():
            if not self.layer(layer)['visible'] \
                == (layer in [self.layers()[0], self.layers()[-1]]):
                return nemoa.log('error', """The first and the last layer
                    of a Feedforward network have to be visible,
                    middle layers have to be hidden!""")

        return True

    def _isMLFFCompatible(self):
        """Test compatibility to multilayer feedforward networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is compatible to layered feedforward
                networks: see _isFeedforwardCompatible
            (2) The network contains at least three layers
        """

        # test if network is compatible to layered feedforward networks
        if not self._isLFFCompatible(): return False

        # test if network contains at least three layers
        if len(self.layers()) < 3: return nemoa.log('error',
            'Multilayer networks need at least three layers!')

        return True

    def _isDBNCompatible(self):
        """Test compatibility to deep beliefe networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is compatible to multilayer feedforward
                networks: see function _isMLFFCompatible
            (2) The network contains an odd number of layers
            (3) The hidden layers are symmetric to the central middle
                layer related to their number of nodes
        """

        # test if network is MLFF compatible
        if not self._isMLFFCompatible(): return False

        # test if the network contains odd number of layers
        if not len(self.layers()) % 2 == 1: return nemoa.log('error',
            'DBNs expect an odd number of layers!')

        # test if the hidden layers are symmetric
        layers = self.layers()
        size = len(layers)
        for lid in range(1, (size - 1) / 2):
            symmetric = len(self.layer(layers[lid])['nodes']) \
                == len(self.layer(layers[-lid-1])['nodes'])
            if not symmetric: return nemoa.log('error',
                """DBNs expect a symmetric number of hidden
                nodes, related to their central middle layer!""")

        return True

    def _isAutoencoderCompatible(self):
        """Test compatibility to autoencoder networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is DBN compatible:
                see function _isDBNCompatible
            (2) The visible input and output layers contain identical
                node labels
        """

        # test if network is DBN compatible
        if not self._isDBNCompatible(): return False

        # test if input and output layers contain identical nodes
        layers = self.layers()
        inputLayer = self.layer(layers[0])['nodes']
        outputLayer = self.layer(layers[0])['nodes']
        if not sorted(inputLayer) == sorted(outputLayer):
            return nemoa.log('error', """Autoencoders expect
                identical input and output nodes""")

        return True

    def about(self, *args):
        """Generic information about various parts of the network.

        Args:
            args: tuple of strings, containing a breadcrump trail to
                a specific information about the dataset

        Examples:
            about()"""

        if not args: return {
            'name': self.name(),
            'description': self.__doc__
        }

        if args[0] == 'name': return self.name()
        if args[0] == 'description': return self.__doc__
        return None

    def name(self):
        """Name of network (as string)."""
        return self.cfg['name'] if 'name' in self.cfg else ''
