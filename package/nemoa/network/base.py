# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import copy

class Network:

    _config = None
    _graph = None

    def __init__(self, config = {}):
        """Configure network to given dictionary."""

        # create copy of config
        self._config = config.copy()
        if not 'name' in self._config: self._config['name'] = None

        # TODO: move functionality to network configuration file!
        # type 'auto' is used for networks
        # wich include all dataset columns as visible units
        if self._config['type'] == 'auto':
            self._config = {'type': 'auto', 'name': '', 'id': 0}
            return

        # TODO: move functionality to network configuration file!
        # type 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self._config['type'] == 'autolayer':
            self._get_nodes_from_layers()
            self._get_edges_from_layers()
            self._configure_layergraph()

        # type 'layer' is used for layered networks
        # wich are manualy defined, by using a dictionary
        if self._config['type'].lower() == 'layer':
            self._configure_layergraph()

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
        visible = system.get('units', group = 'visible')
        hidden = system.get('units', group = 'hidden')
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

    def _configure(self, dataset, system):
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

        nemoa.log("configure network: '%s'" % (self._config['name']))
        nemoa.log('set', indent = '+1')

        # type: 'auto is used for networks
        # wich are created by datasets (visible units)
        # and systems (hidden units)
        if self._config['type'] == 'auto':
            self._get_visible_nodes_from_dataset(dataset)
            self._get_hidden_nodes_from_system(system)
            self._get_edges_from_layers()
            self._configure_layergraph()
            nemoa.log('set', indent = '-1')
            return True

        # type: 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self._config['type'] == 'autolayer':
            self._get_nodes_from_layers()
            self._get_edges_from_layers()
            self._configure_layergraph()
            nemoa.log('set', indent = '-1')
            return True

        # configure network to dataset
        groups = dataset.get('groups')
        changes = []
        for group in groups:
            if not group in self._config['nodes'] \
                or not (groups[group] == self._config['nodes'][group]):
                self._configure_layergraph(
                    nodelist = {'type': group, 'list': groups[group]})

        nemoa.log('set', indent = '-1')
        return True

    def _is_empty(self):
        """Return true if network type is 'empty'."""
        return self._config['type'] == 'empty'

    def _configure_layergraph(self, nodelist = None, edgelist = None):
        """Configure and create layered NetworkX graph."""

        if not nodelist:
            nodelist = {'type': None, 'list': []}
        if not edgelist:
            edgelist = {'type': (None, None), 'list': []}

        # find new nodes to add and old nodes to delete
        if nodelist['type'] in self._config['layer']:

            # count number of new nodes to add to graph
            add_nodes = 0
            for node in nodelist['list']:
                if not node in self._config['nodes'][nodelist['type']]:
                    add_nodes += 1

            # count number of nodes to delete from graph
            del_nodes = 0
            for node in self._config['nodes'][nodelist['type']]:
                if not node in nodelist['list']:
                    del_nodes += 1

        # add edges from edgelist
        layers = self._config['layer']
        src_layer_name = edgelist['type'][0]
        tgt_layer_name = edgelist['type'][1]
        if src_layer_name in layers and tgt_layer_name in layers:
            src_layer_id = layers.index(src_layer_name)
            tgt_layer_id = layers.index(tgt_layer_name)
            if tgt_layer_id - src_layer_id == 1:
                edge_layer = (src_layer_name, tgt_layer_name)
                self._config['edges'][edge_layer] = edgelist['list']

        # filter edges to valid nodes
        nodes = self._config['nodes']
        edges = self._config['edges']
        for i in xrange(len(layers) - 1):
            src_layer = layers[i]
            tgt_layer = layers[i + 1]
            edge_layer = (src_layer, tgt_layer)
            edges_filtered = []
            for src_node, tgt_node in edges[edge_layer]:
                if not src_node in nodes[src_layer]: continue
                if not tgt_node in nodes[tgt_layer]: continue
                edges_filtered.append((src_node, tgt_node))
            edges[edge_layer] = edges_filtered

        # clear or create new instance of networkx directed graph
        if self._graph == None:
            #self._graph = networkx.Graph()
            self._graph = networkx.DiGraph()
        else:
            self._graph.clear()

        # set graph attributes
        self._graph.graph = {
            'name': self._config['name'],
            'type': 'layer',
            'params': {
                'layer': layers }}

        # add nodes to graph
        node_order = 0
        for layer_id, layer in enumerate(layers):
            isvisible = layer in self._config['visible']
            if nodelist['type'] in layers:
                if layer == nodelist['type']:
                    if add_nodes: nemoa.log("""adding %i nodes
                        to layer '%s'""" % (add_nodes, layer))
                    if del_nodes: nemoa.log("""deleting %i nodes
                        from layer '%s'""" % (del_nodes, layer))
            else:
                if isvisible:
                    nemoa.log("adding visible layer '%s' (%s nodes)"
                        % (layer, len(nodes[layer])))
                else:
                    nemoa.log("adding hidden layer '%s' (%s nodes)"
                        % (layer, len(nodes[layer])))

            for layer_node_id, node in enumerate(nodes[layer]):
                if 'encapsulate_nodes' in self._config \
                    and self._config['encapsulate_nodes'] == False:
                    node_name = node
                else:
                    node_name = layer + ':' + node

                # if node is allready known, do not add node
                if node_name in self._graph.nodes(): continue

                self._graph.add_node(
                    node_name,
                    label = node,
                    order = node_order,
                    params = {
                        'type': layer, # TODO: remove parameter: use layer
                        'layer': layer,
                        'layer_id': layer_id,
                        'layer_node_id': layer_node_id,
                        'visible': isvisible } )

                node_order += 1

        # add edges to graph
        edge_order = 0
        for layer_id in xrange(len(layers) - 1):
            src_layer = layers[layer_id]
            tgt_layer = layers[layer_id + 1]
            edge_layer = (src_layer, tgt_layer)

            for (src_node, tgt_node) in edges[edge_layer]:
                if not 'encapsulate_nodes' in self._config \
                    or self._config['encapsulate_nodes'] == True:
                    src_node_name = src_layer + ':' + src_node
                    tgt_node_name = tgt_layer + ':' + tgt_node
                else:
                    src_node_name = src_node
                    tgt_node_name = tgt_node

                self._graph.add_edge(
                    src_node_name, tgt_node_name,
                    order = edge_order,
                    direction = (src_node_name, tgt_node_name),
                    weight = 0.,
                    params = {
                        'type': edge_layer,
                        'layer_id': layer_id })

                edge_order += 1

        return True

    def _get_node(self, node):
        """Return network information of single node."""
        return self._graph.node[node]

    def _get_nodes(self, grouping = None, **kwargs):
        """get list of nodes with specific attributes.

        Examples:
            nodes(type = 'visible')

        """

        # filter nodes by attributes and order entries
        nodes_sort_list = [None] * self._graph.number_of_nodes()
        for node, attr in self._graph.nodes(data = True):
            if not kwargs == {}:
                passed = True
                for key in kwargs:
                    if not key in attr['params'] \
                        or not kwargs[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            nodes_sort_list[attr['order']] = node
        nodes = [node for node in nodes_sort_list if node]
        if grouping == None: return nodes

        # get grouping values
        grouping_values = []
        for node in nodes:
            node_params = self._graph.node[node]['params']
            if not grouping in node_params:
                return nemoa.log('error', """could not get nodes:
                    unknown parameter '%s'.""" % (grouping))
            grouping_value = node_params[grouping]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)

        # create list of groups
        grouped_nodes = []
        for grouping_value in grouping_values:
            group = []
            for node in nodes:
                if self._graph.node[node]['params'][grouping] \
                    == grouping_value:
                    group.append(node)
            grouped_nodes.append(group)

        return grouped_nodes

    def _get_layer(self, layer):
        """Return dictionary containing information about a layer."""
        nodes = self._get_nodes(type = layer)
        if not nodes: return None
        first_node = self._get_node(nodes[0])['params']
        return {
            'id': first_node['layer_id'],
            'label': first_node['type'],
            'visible': first_node['visible'],
            'nodes': nodes}

    def _get_layers(self, **kwargs):
        """Get node layers of network.

        Returns:
            List of strings containing labels of node layers that match
            a given property. The order is from input to output.

        Examples:
            return visible node layers:
                model.network.get('layers', visible = True)

            search for node layer 'test':
                model.network.get('layers', type = 'test')

        """

        graph = self._graph

        # get ordered list of nodes
        nodes_sort_list = [None] * graph.number_of_nodes()
        for node, attr in graph.nodes(data = True):
            if not kwargs == {}:
                passed = True
                for key in kwargs:
                    if not key in attr['params'] \
                        or not kwargs[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            nodes_sort_list[attr['order']] = node
        nodes = [node for node in nodes_sort_list if node]

        # get ordered list of layers
        layers = []
        for node in nodes:
            layer = graph.node[node]['params']['type']
            if layer in layers: continue
            layers.append(layer)

        return layers

    def _get_edge(self, edge):
        return self._graph.edge[edge]

    def _get_edges(self, **kwargs):

        # filter search criteria and order entries
        sorted_list = [None] * self._graph.number_of_edges()

        for src, tgt, attr in self._graph.edges(data = True):
            if not kwargs == {}:

                passed = True
                for key in kwargs:
                    if not key in attr['params'] \
                        or not kwargs[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue

            src_layer = src.split(':')[0]
            tgt_layer = tgt.split(':')[0]
            layers = self._get_layers()

            if src_layer in layers and tgt_layer in layers:
                sorted_list[attr['order']] = (src, tgt)

        # filter empty nodes
        return [edge for edge in sorted_list if edge]

    def _get_backup(self, sec = None):
        dict = {
            'config': copy.deepcopy(self._config),
            'graph': copy.deepcopy(self._graph) }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set_backup(self, **kwargs):
        if 'config' in kwargs:
            self._config = copy.deepcopy(kwargs['config'])
        if 'graph' in kwargs:
            self._graph = copy.deepcopy(kwargs['graph'])
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
        for layer in self._get_layers():
            if not len(self._get_layer(layer)['nodes']) > 0:
                return nemoa.log('error', """Feedforward networks do
                    not allow empty layers.""")

        # test if and only if the first and the last layer are visible
        for layer in self._get_layers():
            if not self._get_layer(layer)['visible'] \
                == (layer in [self._get_layers()[0],
                self._get_layers()[-1]]):
                return nemoa.log('error', """The first and the last
                    layer of a Feedforward network have to be visible,
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
        if len(self._get_layers()) < 3: return nemoa.log('error',
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
        if not len(self._get_layers()) % 2 == 1: return nemoa.log('error',
            'DBNs expect an odd number of layers!')

        # test if the hidden layers are symmetric
        layers = self._get_layers()
        size = len(layers)
        for lid in xrange(1, (size - 1) / 2):
            symmetric = len(self._get_layer(layers[lid])['nodes']) \
                == len(self._get_layer(layers[-lid-1])['nodes'])
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
        layers = self._get_layers()
        inputLayer = self._get_layer(layers[0])['nodes']
        outputLayer = self._get_layer(layers[0])['nodes']
        if not sorted(inputLayer) == sorted(outputLayer):
            return nemoa.log('error', """Autoencoders expect
                identical input and output nodes""")

        return True

    def get(self, key = None, *args, **kwargs):

        if key == 'name': return self._config['name']
        if key == 'about': return self.__doc__
        if key == 'backup': return self._get_backup(*args, **kwargs)
        if key == 'edge': return self._get_edge(*args, **kwargs)
        if key == 'edges': return self._get_edges(*args, **kwargs)
        if key == 'node': return self._get_node(*args, **kwargs)
        if key == 'nodes': return self._get_nodes(*args, **kwargs)
        if key == 'layer': return self._get_layer(*args, **kwargs)
        if key == 'layers': return self._get_layers(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def set(self, key = None, *args, **kwargs):

        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'backup': return self._set_backup(*args, **kwargs)

        if not key == None: nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def _set_name(self, name):
        """Set name of network."""

        if not isinstance(self._config, dict): return False
        self._config['name'] = name
        return True

    def _update(self, **kwargs):
        if 'system' in kwargs:
            system = kwargs['system']
            if not nemoa.type.is_system(system):
                return nemoa.log('error', """could not update network:
                    system is invalid.""")

            for u, v, d in self._graph.edges(data = True):
                params = system._get_link((u, v))
                if not params: params = system._get_link((v, u))
                if not params: continue
                nemoa.common.dict_merge(
                    params, self._graph[u][v]['params'])
                self._graph[u][v]['weight'] = params['weight']

            return True
