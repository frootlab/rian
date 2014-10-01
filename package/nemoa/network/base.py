# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import copy

class network:

    _config = None
    _graph = None

    def __init__(self, config = {}):
        self._set_config(config)

    def _set_config(self, config):
        """Configure network to given dictionary."""

        # create valid config config
        self._config = config.copy()

        # 2do -> move functionality to network configuration file!
        # type 'auto' is used for networks
        # wich include all dataset columns as visible units
        if self._config['type'] == 'auto':
            self._config = {'type': 'auto', 'name': '', 'id': 0}
            return True

        # 2do -> move functionality to network configuration file!
        # type 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self._config['type'] == 'autolayer':
            self._get_nodes_from_layers()
            self._get_edges_from_layers()
            return self._create_layergraph()

        # type 'layer' is used for layered networks
        # wich are manualy defined, by using a dictionary
        if self._config['type'].lower() in ['layer', 'multilayer']:
            return self._create_layergraph()

        return False

    def _get_config(self):
        """Return configuration as dictionary."""
        return self._config.copy()

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
        groups = dataset._get_col_groups()
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
        (visible, hidden) = system.getUnits()
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

    def configure(self, dataset, system):
        """Configure network to dataset and system."""

        # check if network instance is empty
        if self._is_empty(): return nemoa.log(
            "configuration is not needed: network is 'empty'.")

        # check if dataset instance is available
        if not nemoa.type.is_dataset(dataset): return nemoa.log(
            'error', """could not configure network:
            no valid dataset instance given:""")

         # check if system instance is available
        if not nemoa.type.is_system(system): return nemoa.log(
            'error', """could not configure network:
            no valid system instance given.""")

        nemoa.log("configure network: '%s'" % (self.name()))
        nemoa.log('set', indent = '+1')

        # type: 'auto is used for networks
        # wich are created by datasets (visible units)
        # and systems (hidden units)
        if self._config['type'] == 'auto':
            self._get_visible_nodes_from_dataset(dataset)
            self._get_hidden_nodes_from_system(system)
            self._get_edges_from_layers()
            self._create_layergraph()
            nemoa.log('set', indent = '-1')
            return True

        # type: 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self._config['type'] == 'autolayer':
            self._get_nodes_from_layers()
            self._get_edges_from_layers()
            self._create_layergraph()
            nemoa.log('set', indent = '-1')
            return True

        # configure network to dataset
        groups = dataset._get_col_groups()
        changes = []
        for group in groups:
            if not group in self._config['nodes'] \
                or not (groups[group] == self._config['nodes'][group]):
                self._create_layergraph(
                    nodelist = {'type': group, 'list': groups[group]})

        nemoa.log('set', indent = '-1')
        return True

    def _is_empty(self):
        """Return true if network type is 'empty'."""
        return self._config['type'] == 'empty'

    def _create_layergraph(self, nodelist = None, edgelist = None):
        if not nodelist: nodelist = {'type': None, 'list': []}
        if not edgelist: edgelist = {'type': (None, None), 'list': []}

        # get differences between nodelist and self._config['nodes']
        if nodelist['type'] in self._config['layer']:
            # count number of nodes to add to nodes
            addNodes = sum([1 for node in nodelist['list']
                if not node in self._config['nodes'][nodelist['type']]])
            # count number of nodes to delete from graph
            addNodes = sum([1 for node in self._config['nodes'][nodelist['type']]
                if not node in nodelist['list']])

        # update edge list from keyword arguments
        if edgelist['type'][0] in self._config['layer'] \
            and edgelist['type'][1] in self._config['layer']:
            indexA = self._config['layer'].index(edgelist['type'][0])
            indexB = self._config['layer'].index(edgelist['type'][1])
            if indexB - indexA == 1:
                edge_layer = (edgelist['type'][0], edgelist['type'][1])
                self._config['edges'][edge_layer] = edgelist['list']

        # filter edges to valid nodes
        for i in xrange(len(self._config['layer']) - 1):
            src_layer = self._config['layer'][i]
            tgt_layer = self._config['layer'][i + 1]
            edge_layer = (src_layer, tgt_layer)
            filtered = []

            for src_node, tgt_node in self._config['edges'][edge_layer]:
                if not src_node in self._config['nodes'][src_layer]: continue
                if not tgt_node in self._config['nodes'][tgt_layer]: continue
                filtered.append((src_node, tgt_node))
            self._config['edges'][edge_layer] = filtered

        # reset and create new NetworkX graph Instance
        if self._graph == None: self._graph = networkx.Graph()
        else: self._graph.clear()

        # set graph attributes
        self._graph.graph =  {
            'name': self._config['name'],
            'type': 'layer',
            'params': { 'layer': self._config['layer'] }
        }

        # add nodes to graph
        order = 0
        for layerId, layer in enumerate(self._config['layer']):
            visible = layer in self._config['visible']
            if nodelist['type'] in self._config['layer']:
                if layer == nodelist['type']:
                    if addNodes: nemoa.log("""adding %i nodes
                        to layer '%s'""" % (addNodes, layer))
                    if delNodes: nemoa.log("""deleting %i nodes
                        from layer '%s'""" % (delNodes, layer))
            else:
                if visible: nemoa.log('adding visible layer: \'' + layer + \
                    '\' (' + str(len(self._config['nodes'][layer])) + ' nodes)')
                else: nemoa.log('adding hidden layer: \'' + layer + \
                    '\' (' + str(len(self._config['nodes'][layer])) + ' nodes)')
            for layerNodeId, node in enumerate(self._config['nodes'][layer]):
                if 'add_layer_to_node_labels' in self._config \
                    and self._config['add_layer_to_node_labels'] == False:
                    id = node
                else:
                    id = layer + ':' + node
                if id in self._graph.nodes(): continue

                self._graph.add_node(id,
                    label = node,
                    order = order,
                    params = {
                        'type': layer,
                        'layer_id': layerId,
                        'layerNodeId': layerNodeId,
                        'visible': visible } )

                order += 1

        # add edges to graph
        order = 0
        for i in xrange(len(self._config['layer']) - 1):
            src_layer = self._config['layer'][i]
            tgt_layer = self._config['layer'][i + 1]
            edge_layer = (src_layer, tgt_layer)
            type_id = i

            for (src_node, tgt_node) in self._config['edges'][edge_layer]:
                if 'add_layer_to_node_labels' in self._config \
                    and self._config['add_layer_to_node_labels'] == False:
                    src_node_id = src_node
                    tgt_node_id = tgt_node
                else:
                    src_node_id = src_layer + ':' + src_node
                    tgt_node_id = tgt_layer + ':' + tgt_node

                self._graph.add_edge(
                    src_node_id, tgt_node_id,
                    weight = 0.,
                    order  = order,
                    params = {'type': edge_layer, 'layer_id': type_id})

                order += 1

        return True

    def node(self, node):
        """Return network information of single node."""
        return self._graph.node[node]

    def nodes(self, group_by_layer = False, **kwargs):
        """get list of nodes with specific attributes
        example nodes(type = 'visible')"""

        if group_by_layer: return self._nodes_group_by_layer(**kwargs)

        # filter search criteria and order entries
        sortedList = [None] * self._graph.number_of_nodes()
        for node, attr in self._graph.nodes(data = True):
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

    def _node_labels(self, **kwargs):
        return [self._graph.node[node]['label'] \
            for node in self.nodes(**kwargs)]

    def _nodes_group_by_layer(self, type = None):

        # get layers of specific node type
        if type:
            if not type in self._config: return nemoa.log('warning',
                "unknown node type '%s'." % (str(type)))
            return {group: self._node_labels(type = group)
                for group in self._config[type]}

        # get all groups
        allGroups = {}
        for type in ['visible', 'hidden']:
            groups = {}
            for group in self._config[type]:
                groups[group] = self._node_labels(type = group)
            allGroups[type] = groups
        return allGroups

    def layer(self, layer):
        """Return dictionary containing information about a layer."""
        nodes = self.nodes(type = layer)
        if not nodes: return None
        first_node = self.node(nodes[0])['params']
        return {
            'id': first_node['layer_id'],
            'label': first_node['type'],
            'visible': first_node['visible'],
            'nodes': nodes}

    def layers(self, **kwargs):
        """Return ordered list of layers by label."""
        layerDict = {self.node(node)['params']['layer_id']: \
            {'label': self.node(node)['params']['type']} \
            for node in self.nodes()}
        layerList = [layerDict[layer]['label'] for layer in xrange(0, len(layerDict))]
        return layerList

    def edge(self, edge):
        return self._graph.edge[edge]

    def edges(self, **params):

        # filter search criteria and order entries
        sorted_list = [None] * self._graph.number_of_edges()

        for src, tgt, attr in self._graph.edges(data = True):
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

            if srcLayer in self._config['visible'] \
                and tgtLayer in self._config['hidden']:
                sorted_list[attr['order']] = (src, tgt)
            elif srcLayer in self._config['hidden'] \
                and tgtLayer in self._config['visible']:
                sorted_list[attr['order']] = (tgt, src)

        # filter empty nodes
        return [edge for edge in sorted_list if edge]

    def _get(self, sec = None):
        dict = {
            'cfg': copy.deepcopy(self._config),
            'graph': copy.deepcopy(self._graph) }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set(self, **dict):
        if 'cfg' in dict: self._config = copy.deepcopy(dict['cfg'])
        if 'graph' in dict: self._graph = copy.deepcopy(dict['graph'])
        return True

    def _export_graph(self, file = None, format = 'gml'):
        if file == None: nemoa.log('error', "no save path was given")

        # create path if not available
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        if format == 'gml':
            G = self._graph.copy()
            networkx.write_gml(G, file)

    def _is_compatible_lff(self):
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

    def _is_compatible_mlff(self):
        """Test compatibility to multilayer feedforward networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is compatible to layered feedforward
                networks: see _isFeedforwardCompatible
            (2) The network contains at least three layers
        """

        # test if network is compatible to layered feedforward networks
        if not self._is_compatible_lff(): return False

        # test if network contains at least three layers
        if len(self.layers()) < 3: return nemoa.log('error',
            """incompatible network: multilayer networks need at least
            one hidden layer.""")

        return True

    def _is_compatible_dbn(self):
        """Test compatibility to deep beliefe networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is compatible to multilayer feedforward
                networks: see function _is_compatible_mlff
            (2) The network contains an odd number of layers
            (3) The hidden layers are symmetric to the central middle
                layer related to their number of nodes
        """

        # test if network is MLFF compatible
        if not self._is_compatible_mlff(): return False

        # test if the network contains odd number of layers
        if not len(self.layers()) % 2 == 1: return nemoa.log('error',
            'DBNs expect an odd number of layers!')

        # test if the hidden layers are symmetric
        layers = self.layers()
        size = len(layers)
        for lid in xrange(1, (size - 1) / 2):
            symmetric = len(self.layer(layers[lid])['nodes']) \
                == len(self.layer(layers[-lid-1])['nodes'])
            if not symmetric: return nemoa.log('error',
                """DBNs expect a symmetric number of hidden
                nodes, related to their central middle layer!""")

        return True

    def _is_compatible_autoencoder(self):
        """Test compatibility to autoencoder networks.

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The network is DBN compatible:
                see function _is_compatible_dbn
            (2) The visible input and output layers contain identical
                node labels
        """

        # test if network is DBN compatible
        if not self._is_compatible_dbn(): return False

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
        return self._config['name'] if 'name' in self._config else ''

    def update(self, **kwargs):
        if 'system' in kwargs:
            system = kwargs['system']
            if not nemoa.type.is_system(system):
                return nemoa.log('error',
                    'could not update network: system is invalid.')

            for u, v, d in self._graph.edges(data = True):
                params = system._get_link((u, v))
                if not params: params = system._get_link((v, u))
                if not params: continue
                nemoa.common.dict_merge(
                    params, self._graph[u][v]['params'])
                self._graph[u][v]['weight'] = params['weight']

            return True
