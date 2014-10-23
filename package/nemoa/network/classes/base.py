# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import copy
import importlib
import json

class Network:

    _default = { 'name': None }
    _config = None
    _graph = None

    def __init__(self, **kwargs):
        """Import network from dictionary."""
        self._set_copy(**kwargs)

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

        # configure network to dataset
        groups = dataset.get('colgroups')
        changes = []
        for group in groups:
            if not group in self._config['nodes'] \
                or not (groups[group] == self._config['nodes'][group]):
                self._configure_graph(
                    nodelist = {'layer': group, 'list': groups[group]})

        nemoa.log('set', indent = '-1')
        return True

    def _is_empty(self):
        """Return true if network type is 'empty'."""
        return self._config['type'] == 'empty'

    def _configure_graph(self, nodelist = None, edgelist = None):
        """Configure and create layered NetworkX graph."""

        if not nodelist:
            nodelist = {'layer': None, 'list': []}
        if not edgelist:
            edgelist = {'layer': (None, None), 'list': []}

        # find new nodes to add and old nodes to delete
        if nodelist['layer'] in self._config['layer']:

            # count number of new nodes to add to graph
            add_nodes = 0
            for node in nodelist['list']:
                if not node in self._config['nodes'][nodelist['layer']]:
                    add_nodes += 1

            # count number of nodes to delete from graph
            del_nodes = 0
            for node in self._config['nodes'][nodelist['layer']]:
                if not node in nodelist['list']:
                    del_nodes += 1

        # add edges from edgelist
        layers = self._config['layer']
        src_layer_name = edgelist['layer'][0]
        tgt_layer_name = edgelist['layer'][1]
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
            self._graph = networkx.DiGraph()
        else:
            self._graph.clear()

        # add configuration as graph attributes
        self._graph.graph['params'] = self._config
        # update / set networkx module and class info
        # to allow export and import of graph to dict
        self._graph.graph['params']['networkx'] = {
            'module': self._graph.__module__,
            'class': self._graph.__class__.__name__ }


        # add nodes to graph
        node_order = 0
        for layer_id, layer in enumerate(layers):
            is_visible = self._config['layers'][layer]['visible']
            node_type = self._config['layers'][layer]['type']

            if nodelist['layer'] in layers:
                if layer == nodelist['layer']:
                    if add_nodes: nemoa.log("""adding %i nodes
                        to layer '%s'""" % (add_nodes, layer))
                    if del_nodes: nemoa.log("""deleting %i nodes
                        from layer '%s'""" % (del_nodes, layer))
            else:
                if is_visible:
                    nemoa.log("adding visible layer '%s' (%s nodes)"
                        % (layer, len(nodes[layer])))
                else:
                    nemoa.log("adding hidden layer '%s' (%s nodes)"
                        % (layer, len(nodes[layer])))

            for layer_node_id, node in enumerate(nodes[layer]):
                if 'labelencapsulate' in self._config \
                    and self._config['labelencapsulate'] == False:
                    node_name = node
                else:
                    node_name = layer + ':' + node

                # if node is allready known, do not add node
                if node_name in self._graph.nodes(): continue

                self._graph.add_node(
                    node_name,
                    label = node_name,
                    params = {
                        'label': node,
                        'layer': layer,
                        'order': node_order,
                        'layer_id': layer_id,
                        'layer_sub_id': layer_node_id,
                        'visible': is_visible,
                        'type': node_type } )

                node_order += 1

        # add edges to graph
        edge_order = 0
        for layer_id in xrange(len(layers) - 1):
            src_layer = layers[layer_id]
            tgt_layer = layers[layer_id + 1]
            edge_layer = (src_layer, tgt_layer)

            for (src_node, tgt_node) in edges[edge_layer]:
                if not 'labelencapsulate' in self._config \
                    or self._config['labelencapsulate'] == True:
                    src_node_name = src_layer + ':' + src_node
                    tgt_node_name = tgt_layer + ':' + tgt_node
                else:
                    src_node_name = src_node
                    tgt_node_name = tgt_node

                self._graph.add_edge(
                    src_node_name, tgt_node_name,
                    weight = 0.,
                    params = {
                        'order': edge_order,
                        'layer': edge_layer,
                        'layer_id': layer_id })

                edge_order += 1

        return True

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
        input_layer = self._get_layer(layers[0])['nodes']
        output_layer = self._get_layer(layers[0])['nodes']
        if not sorted(input_layer) == sorted(output_layer):
            return nemoa.log('error', """Autoencoders expect
                identical input and output nodes""")

        return True

    def get(self, key = 'name', *args, **kwargs):
        """Get meta information, parameters and data of network."""

        # get meta information of network
        if key == 'fullname': return self._get_fullname()
        if key == 'name': return self._get_name()
        if key == 'branch': return self._get_branch()
        if key == 'version': return self._get_version()
        if key == 'about': return self._get_about()
        if key == 'author': return self._get_author()
        if key == 'email': return self._get_email()
        if key == 'license': return self._get_license()
        if key == 'type': return self._get_type()

        # get network parameters and data
        if key == 'node': return self._get_node(*args, **kwargs)
        if key == 'nodes': return self._get_nodes(*args, **kwargs)
        if key == 'edge': return self._get_edge(*args, **kwargs)
        if key == 'edges': return self._get_edges(*args, **kwargs)
        if key == 'layer': return self._get_layer(*args, **kwargs)
        if key == 'layers': return self._get_layers(*args, **kwargs)

        # export network configuration and graph
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'graph': return self._get_graph(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_fullname(self):
        """Get fullname of network."""
        fullname = ''
        name = self._get_name()
        if name: fullname += name
        branch = self._get_branch()
        if branch: fullname += '.' + branch
        version = self._get_version()
        if version: fullname += '.' + str(version)
        return fullname

    def _get_name(self):
        """Get name of network."""
        if 'name' in self._config: return self._config['name']
        return None

    def _get_branch(self):
        """Get branch of network."""
        if 'branch' in self._config: return self._config['branch']
        return None

    def _get_version(self):
        """Get version number of network branch."""
        if 'version' in self._config: return self._config['version']
        return None

    def _get_about(self):
        """Get description of network."""
        if 'about' in self._config: return self._config['about']
        return None

    def _get_author(self):
        """Get author of network."""
        if 'author' in self._config: return self._config['author']
        return None

    def _get_email(self):
        """Get email of author of network."""
        if 'email' in self._config: return self._config['email']
        return None

    def _get_license(self):
        """Get license of network."""
        if 'license' in self._config: return self._config['license']
        return None

    def _get_type(self):
        """Get type of network, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_node(self, node):
        """Return network information of single node."""
        return self._graph.node[node]

    def _get_nodes(self, grouping = None, **kwargs):
        """Get nodes of network.

        Args:
            grouping: grouping parameter of nodes. If grouping is not
                None, the returned nodes are grouped by the different
                values of the grouping parameter. Grouping is only
                possible if every node has the parameter.
            **kwargs: filter parameters of nodes. If kwargs are given,
                only nodes that match the filter parameters are
                returned.

        Returns:
            If the argument 'grouping' is not set, a list of strings
            containing name identifiers of nodes is returned. If
            'grouping' is a valid node parameter, the nodes are grouped
            by the values of the grouping parameter.

        Examples:
            Get a list of all nodes grouped by layers:
                model.network.get('nodes', grouping = 'layer')
            Get a list of visible nodes:
                model.network.get('nodes', visible = True)

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
            nodes_sort_list[attr['params']['order']] = node
        nodes = [node for node in nodes_sort_list if node]
        if grouping == None: return nodes

        # group nodes
        grouping_values = []
        for node in nodes:
            node_params = self._graph.node[node]['params']
            if not grouping in node_params:
                return nemoa.log('error', """could not get nodes:
                    unknown parameter '%s'.""" % (grouping))
            grouping_value = node_params[grouping]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_nodes = []
        for grouping_value in grouping_values:
            group = []
            for node in nodes:
                if self._graph.node[node]['params'][grouping] \
                    == grouping_value:
                    group.append(node)
            grouped_nodes.append(group)
        return grouped_nodes

    def _get_edge(self, edge):
        if not isinstance(edge, tuple):
            return nemoa.log('error', """could not get edge:
                edge '%s' is unkown.""" % (edge))
        src_node, tgt_node = edge
        if not src_node in self._graph.edge \
            or not tgt_node in self._graph.edge[src_node]:
            return nemoa.log('error', """could not get edge:
                edge ('%s', '%s') is unkown.""" % (src_node, tgt_node))
        return self._graph.edge[src_node][tgt_node]

    def _get_edges(self, grouping = None, **kwargs):

        # filter edges by attributes and order entries
        edge_sort_list = [None] * self._graph.number_of_edges()
        for src, tgt, attr in self._graph.edges(data = True):
            if not kwargs == {}:
                passed = True
                for key in kwargs:
                    if not key in attr['params'] \
                        or not kwargs[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            edge_sort_list[attr['params']['order']] = (src, tgt)
        edges = [edge for edge in edge_sort_list if edge]
        if grouping == None: return edges

        # group edges
        grouping_values = []
        for edge in edges:
            src, tgt = edge
            edge_params = self._graph.edge[src][tgt]['params']
            if not grouping in edge_params:
                return nemoa.log('error', """could not get edges:
                    unknown parameter '%s'.""" % (grouping))
            grouping_value = edge_params[grouping]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_edges = []
        for grouping_value in grouping_values:
            group = []
            for edge in edges:
                src, tgt = edge
                if self._graph.edge[src][tgt]['params'][grouping] \
                    == grouping_value:
                    group.append(edge)
            grouped_edges.append(group)

        return grouped_edges

    def _get_layer(self, layer):
        """Return dictionary containing information about a layer."""
        nodes = self._get_nodes(layer = layer)
        if not nodes: return None
        first_node = self._get_node(nodes[0])['params']
        return {
            'layer_id': first_node['layer_id'],
            'layer': first_node['layer'],
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
            nodes_sort_list[attr['params']['order']] = node
        nodes = [node for node in nodes_sort_list if node]

        # get ordered list of layers
        layers = []
        for node in nodes:
            layer = graph.node[node]['params']['layer']
            if layer in layers: continue
            layers.append(layer)

        return layers

    def _get_copy(self, key = None, *args, **kwargs):
        """Get network copy as dictionary."""

        if key == None: return {
            'config': self._get_config(), 'graph': self._get_graph() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'graph': return self._get_graph(*args, **kwargs)

        return nemoa.log('error', """could not get network copy:
            unknown key '%s'.""" % (key))

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in self._config.keys():
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        return nemoa.log('error', """could not get configuration:
            unknown key '%s'.""" % (key))

    def _get_graph(self, type = 'dict'):
        """Get graph as dictionary or networkx graph."""

        graph = self._graph.copy()

        if type == 'graph': return graph
        if type == 'dict':
            return {
                'graph': graph.graph,
                'nodes': graph.nodes(data = True),
                'edges': networkx.to_dict_of_dicts(graph) }

        return None

    def set(self, key = None, *args, **kwargs):
        """Set meta information, parameters and data of network."""

        # set meta information of network
        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'branch': return self._set_branch(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)
        if key == 'about': return self._set_about(*args, **kwargs)
        if key == 'author': return self._set_author(*args, **kwargs)
        if key == 'email': return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)

        # import network configuration and graph
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'graph': return self._set_graph(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_name(self, network_name):
        """Set name of network."""
        if not isinstance(network_name, str): return False
        self._config['name'] = network_name
        return True

    def _set_branch(self, network_branch):
        """Set branch of network."""
        if not isinstance(network_branch, str): return False
        self._config['branch'] = network_branch
        return True

    def _set_version(self, network_version):
        """Set version number of network branch."""
        if not isinstance(network_version, int): return False
        self._config['version'] = network_version
        return True

    def _set_about(self, network_about):
        """Get description of network."""
        if not isinstance(network_about, str): return False
        self._config['about'] = network_about
        return True

    def _set_author(self, network_author):
        """Set author of network."""
        if not isinstance(network_author, str): return False
        self._config['author'] = network_author
        return True

    def _set_email(self, network_author_email):
        """Set email of author of network."""
        if not isinstance(network_author_email, str): return False
        self._config['email'] = network_author_email
        return True

    def _set_license(self, network_license):
        """Set license of network."""
        if not isinstance(network_license, str): return False
        self._config['license'] = network_license
        return True

    def _set_copy(self, config = None, graph = None):
        """Set configuration and graph of network.

        Args:
            config (dict or None, optional): network configuration
            graph (dict or None, optional): network graph

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if graph: retval &= self._set_graph(graph)

        return retval

    def _set_config(self, config = None):
        """Set configuration from dictionary."""

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            config_copy = copy.deepcopy(config)
            nemoa.common.dict_merge(config_copy, self._config)
            # reconfigure graph
            self._configure_graph()
        return True

    def _set_graph(self, graph = None):
        """Set configuration from dictionary."""

        # initialize graph
        if not hasattr(self, '_graph') or not self._graph:
            self._configure_graph()

        if not graph: return True

        # merge graph
        graph_copy = self._get_graph()
        nemoa.common.dict_merge(graph, graph_copy)

        # create networkx graph instance
        object_type = graph['graph']['params']['networkx']
        module = importlib.import_module(object_type['module'])
        self._graph = getattr(module, object_type['class'])(
            graph_copy['edges'])
        self._graph.graph = graph_copy['graph']
        for node, attr in graph_copy['nodes']:
            self._graph.node[node] = attr

        return True

    def _update(self, **kwargs):
        if not 'system' in kwargs: return False
        system = kwargs['system']
        if not nemoa.type.is_system(system):
            return nemoa.log('error', """could not update network:
                system is invalid.""")

        # get edge parameters from system links
        for edge in self._graph.edges():
            params = system.get('link', edge)
            if not params: continue
            nemoa.common.dict_merge(
                params, self._graph[edge[0]][edge[1]]['params'])
            self._graph[edge[0]][edge[1]]['weight'] \
                = float(params['weight'])

        return True

    def save(self, *args, **kwargs):
        """Export network to file."""
        return nemoa.network.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show network as image."""
        return nemoa.network.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of network."""
        return nemoa.network.copy(self, *args, **kwargs)
