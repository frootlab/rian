# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import importlib
from typing import Any, Dict
import networkx
from flab.base import otree
import nemoa
from nemoa.core import log
from nemoa.base import nbase
from flab.base.types import Function

class Network(nbase.ObjectIP):
    """Network base class.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _attr: Dict[str, int] = {
        'nodes': 0b01, 'edges': 0b01, 'layers': 0b01
    }

    _copy: Dict[str, str] = {
        'graph': '_graph'
    }

    _default = {
        'name': None
    }

    _config  = None
    _graph   = None


    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize network with content from arguments."""

        # get attribute and storage defaults from parent
        self._attr = {**getattr(super(), '_attr', {}), **self._attr}
        self._copy = {**getattr(super(), '_copy', {}), **self._copy}

        super().__init__(*args, **kwds)

    def configure(self, dataset = None):
        """Configure network to dataset."""

        # check if dataset instance is available
        if not otree.has_base(dataset, 'Dataset'):
            raise TypeError("dataset is required to be of type dataset")

        log.info("configure network: '%s'" % (self._config['name']))

        # configure network to dataset
        groups = dataset.get('colgroups')
        changes = []
        for group in groups:
            if group not in self._config['nodes'] \
                or not (groups[group] == self._config['nodes'][group]):
                self._configure_graph(
                    nodelist = {'layer': group, 'list': groups[group]})

        return True

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
                if node not in self._config['nodes'][nodelist['layer']]:
                    add_nodes += 1

            # count number of nodes to delete from graph
            del_nodes = 0
            for node in self._config['nodes'][nodelist['layer']]:
                if node not in nodelist['list']: del_nodes += 1

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
        for i in range(len(layers) - 1):
            src_layer = layers[i]
            tgt_layer = layers[i + 1]
            edge_layer = (src_layer, tgt_layer)
            edges_filtered = []
            for src_node, tgt_node in edges[edge_layer]:
                if not (src_node in nodes[src_layer] \
                    and tgt_node in nodes[tgt_layer]): continue
                edges_filtered.append((src_node, tgt_node))
            edges[edge_layer] = edges_filtered

        # clear or create new instance of networkx directed graph
        if self._graph is None: self._graph = networkx.DiGraph()
        else: self._graph.clear()

        # add configuration as graph attributes
        self._graph.graph['params'] = self._config
        # update / set networkx module and class info
        # to allow export and import of graph to dict
        self._graph.graph['params']['networkx'] = {
            'module': self._graph.__module__,
            'class': self._graph.__class__.__name__ }

        # add nodes to graph
        order = 0
        for layerid, layer in enumerate(layers):
            for layersubid, node in enumerate(nodes[layer]):
                if 'labelencapsulate' in self._config \
                    and self._config['labelencapsulate'] == False:
                    node_name = node
                else:
                    node_name = layer + ':' + node

                # if node is already known, do not add node
                if node_name in self._graph.nodes(): continue

                # create dictionary with node parameters
                node_params = self._config['layers'][layer].copy()
                node_params['label'] = node
                node_params['layer'] = layer
                node_params['order'] = order
                node_params['layer_id'] = layerid
                node_params['layer_sub_id'] = layersubid

                self._graph.add_node(node_name,
                    label = node_name, params = node_params )

                order += 1

        # add edges to graph
        edge_order = 0
        for layer_id in range(len(layers) - 1):
            src_layer = layers[layer_id]
            tgt_layer = layers[layer_id + 1]
            edge_layer = (src_layer, tgt_layer)

            for (src_node, tgt_node) in edges[edge_layer]:
                if 'labelencapsulate' not in self._config \
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
                raise ValueError("""Feedforward networks do
                    not allow empty layers.""")

        # test if and only if the first and the last layer are visible
        for layer in self._get_layers():
            if not self._get_layer(layer)['visible'] \
                == (layer in [self._get_layers()[0],
                self._get_layers()[-1]]):
                raise ValueError("""The first and the last
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
        if len(self._get_layers()) < 3: raise ValueError(
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
        if not len(self._get_layers()) % 2 == 1:
            raise ValueError("""DBNs expect an odd
                number of layers.""")

        # test if the hidden layers are symmetric
        layers = self._get_layers()
        size = len(layers)
        for lid in range(1, (size - 1) / 2):
            symmetric = len(self._get_layer(layers[lid])['nodes']) \
                == len(self._get_layer(layers[-lid-1])['nodes'])
            if not symmetric: raise ValueError(
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
            raise ValueError("""Autoencoders expect
                identical input and output nodes""")

        return True

    def get(self, key = 'name', *args, **kwds):
        """Get meta information and content."""

        # get readable attributes
        if self._attr.get(key, 0b00) & 0b01:
            return getattr(self, '_get_' + key)(*args, **kwds)

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwds)
        if key == 'algorithms':
            return self._get_algorithms(
                attribute='about', *args, **kwds)

        # content
        if key == 'node': return self._get_node(*args, **kwds)
        if key == 'nodes': return self._get_nodes(*args, **kwds)
        if key == 'edge': return self._get_edge(*args, **kwds)
        if key == 'edges': return self._get_edges(*args, **kwds)
        if key == 'layer': return self._get_layer(*args, **kwds)
        if key == 'layers': return self._get_layers(*args, **kwds)

        # direct access
        if key == 'copy': return self._get_copy(*args, **kwds)
        if key == 'config': return self._get_config(*args, **kwds)
        if key == 'graph': return self._get_graph(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _get_algorithms(self, category = None, attribute = None):
        """Get algorithms provided by network."""
        funcs = otree.get_members_dict(networkx.algorithms, classinfo=Function)
        if attribute is None:
            return funcs

        return {k: v.get(attribute, None) for k, v in funcs.items()}

    def _get_algorithm(self, algorithm = None, *args, **kwds):
        """Get algorithm."""
        algorithms = self._get_algorithms(*args, **kwds)
        return algorithms.get(algorithm, None)

    def _get_node(self, node):
        """Return network information of single node."""
        return self._graph.node.get(node, None)

    def _get_nodes(self, groupby = None, **kwds):
        """Get nodes of network.

        Args:
            groupby (str or None): Name of a node attribute
                used to group nodes. If groupby is not
                None, the returned nodes are grouped by the different
                values of this attribute. Grouping is only
                possible if every node contains the attribute.
            **kwds: filter parameters of nodes. If kwds are given,
                only nodes that match the filter parameters are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of nodes is returned. If
            'groupby' is a valid node parameter, the nodes are grouped
            by the values of the grouping parameter.

        Examples:
            Get a list of all nodes grouped by layers:
                model.network.get('nodes', groupby = 'layer')
            Get a list of visible nodes:
                model.network.get('nodes', visible = True)

        """

        # filter nodes to given attributes
        nodes_sort_list = [None] * self._graph.number_of_nodes()
        for node, attr in self._graph.nodes(data = True):
            if not kwds == {}:
                passed = True
                for key in kwds:
                    if key not in attr['params'] \
                        or not kwds[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            nodes_sort_list[attr['params']['order']] = node
        nodes = [node for node in nodes_sort_list if node]
        if groupby is None: return nodes

        # group nodes by given attribute
        grouping_values = []
        for node in nodes:
            node_params = self._graph.node[node]['params']
            if groupby not in node_params:
                raise ValueError("""could not get nodes:
                    unknown node attribute '%s'.""" % (groupby))
            grouping_value = node_params[groupby]
            if grouping_value not in grouping_values:
                grouping_values.append(grouping_value)
        grouped_nodes = []
        for grouping_value in grouping_values:
            group = []
            for node in nodes:
                if self._graph.node[node]['params'][groupby] \
                    == grouping_value:
                    group.append(node)
            grouped_nodes.append(group)
        return grouped_nodes

    def _get_edge(self, edge):
        if edge not in self._graph.edges:
            raise ValueError(f"edge '{str(edge)}' is not valid")
        return self._graph.edges[edge]

    def _get_edges(self, groupby = None, **kwds):
        """Get edges of network.

        Args:
            groupby (str or None): Name of an edge attribute
                used to group edges. If groupby is not
                None, the returned edges are grouped by the different
                values of this attribute. Grouping is only
                possible if every edge contains the attribute.
            **kwds: filter attributs of edges. If kwds are given,
                only edges that match the filter attributes are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of edges is returned. If
            'groupby' is a valid edge attribute, the links are grouped
            by the values of this attribute.

        Examples:
            Get a list of all edges grouped by layers:
                model.system.get('edges', groupby = 'layer')
            Get a list of edges with negative sign:
                model.system.get('edges', sign = -1)

        """

        # filter efges to given attributes
        edge_sort_list = [None] * self._graph.number_of_edges()
        for src, tgt, attr in self._graph.edges(data = True):
            if not kwds == {}:
                passed = True
                for key in kwds:
                    if key not in attr['params'] \
                        or not kwds[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed: continue
            edge_sort_list[attr['params']['order']] = (src, tgt)
        edges = [edge for edge in edge_sort_list if edge]
        if groupby is None: return edges

        # group edges by given attribute
        grouping_values = []
        for edge in edges:
            edge_params = self._graph.edges[edge]['params']
            if groupby not in edge_params:
                raise ValueError("""could not get edges:
                    unknown edge attribute '%s'.""" % (groupby))
            grouping_value = edge_params[groupby]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_edges = []
        for grouping_value in grouping_values:
            group = []
            for edge in edges:
                if self._graph.edges[edge]['params'][groupby] \
                    == grouping_value:
                    group.append(edge)
            grouped_edges.append(group)
        return grouped_edges

    def _get_layer(self, layer):
        """Return dictionary containing information about a layer."""
        if layer not in self._config['layers']: return None
        retdict = self._config['layers'][layer]
        retdict['layer'] = layer
        retdict['nodes'] = self._get_nodes(layer = layer)
        retdict['layer_id'] = self._config['layer'].index(layer)
        return retdict

    def _get_layers(self, **kwds):
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
            if not kwds == {}:
                passed = True
                for key in kwds:
                    if key not in attr['params'] \
                        or kwds[key] != attr['params'][key]:
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

    def set(self, key = None, *args, **kwds):
        """Set meta information, parameters and data of network."""

        # set writeable attributes
        if self._attr.get(key, 0b00) & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwds)

        # import network configuration and graph
        if key == 'copy': return self._set_copy(*args, **kwds)
        if key == 'config': return self._set_config(*args, **kwds)
        if key == 'graph': return self._set_graph(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_copy(self, config = None, graph = None):
        """Set configuration and graph of network.

        Args:
            config (dict or None, optional): network configuration
            graph (dict or None, optional): network graph

        Returns:
            bool: True if no error occured, else False

        """

        retval = True

        if config: retval &= self._set_config(config)
        if graph: retval &= self._set_graph(graph)

        return retval

    def _set_config(self, config = None):
        """Set configuration from dictionary.

        Returns:
            bool: True if no error occured, else False

        """

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            self._config = {**self._config, **config}

            # reconfigure graph
            self._configure_graph()

        return True

    def _set_graph(self, graph = None):
        """Set configuration from dictionary.

        Returns:
            bool: True if no error occured, else False

        """
        # initialize graph
        if not hasattr(self, '_graph') or not self._graph:
            self._configure_graph()

        if not graph:
            return True

        # merge graph
        graph_copy = {**self._get_graph(), **graph}

        # create networkx graph instance
        object_type = graph['graph']['params']['networkx']
        module = importlib.import_module(object_type['module'])
        self._graph = getattr(module, object_type['class'])(
            graph_copy['edges'])
        self._graph.graph = graph_copy['graph']
        for node, attr in graph_copy['nodes']:
            self._graph.node[node].update(attr)

        return True

    def evaluate(self, name = None, *args, **kwds):
        """Evaluate network."""

        algorithms = self._get_algorithms(attribute = 'reference')
        if name not in algorithms:
            raise ValueError("""could not evaluate network:
                unknown networkx algorithm name '%s'.""" % (name))

        return algorithms[name](self._graph, *args, **kwds)

    def initialize(self, system = None):
        if not system:
            return False
        if not otree.has_base(system, 'System'):
            raise ValueError("system is not valid")

        # get edge parameters from system links
        for edge in self._graph.edges():
            params = system.get('link', edge)
            if not params:
                continue
            edge_dict = self._graph[edge[0]][edge[1]]
            edge_dict['params'] = {**edge_dict['params'], **params}
            edge_dict['weight'] = float(params['weight'])

        return True

    def save(self, *args, **kwds):
        """Export network to file."""
        return nemoa.network.save(self, *args, **kwds)

    def show(self, *args, **kwds):
        """Show network as image."""
        return nemoa.network.show(self, *args, **kwds)

    def copy(self, *args, **kwds):
        """Create copy of network."""
        return nemoa.network.copy(self, *args, **kwds)
