#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa
import networkx, copy

class network:
    """Base class for networks."""

    #
    # NETWORK CONFIGURATION
    #

    def __init__(self, config = {}, **kwargs):
        self.cfg = None
        self.graph = None
        self.setConfig(config)

    def setConfig(self, config):
        """Configure network to given dictionary."""

        # create valid config config
        if not isinstance(config, dict):
            self.cfg = {}
        else:
            self.cfg = config.copy()
        if not 'type' in self.cfg or self.cfg['type'] == 'empty':
            self.cfg = {'type': 'empty', 'name': '', 'id': 0}
            return True

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
            self.__getNodesFromLayers()
            self.__getEdgesFromNodesAndLayers()
            return self.updateGraph()

        # type 'layer' is used for networks
        # wich are manualy defined, using a file
        if self.cfg['type'].lower() in ['layer', 'multilayer']:
            return self.updateGraph()

        return False

    def getConfig(self):
        """Return configuration as dictionary."""
        return self.cfg.copy()

    def __getNodesFromLayers(self):
        """Create nodes from layers."""
        self.cfg['nodes'] = {}
        self.cfg['label_format'] = 'generic:string'
        for layer in self.cfg['layer']:
            nodeNumber = self.cfg['params'][layer + '.size']
            self.cfg['nodes'][layer] = \
                [layer + str(i) for i in range(1, nodeNumber + 1)]
        return True

    def __getVisibleNodesFromDataset(self, dataset):
        """Create nodes from dataset."""

        self.cfg['visible'] = []
        self.cfg['label_format'] = 'generic:string'
        if not 'nodes' in self.cfg:
            self.cfg['nodes'] = {}
        if not 'layer' in self.cfg:
            self.cfg['layer'] = []
        groups = dataset.getColGroups()
        for group in groups:
            if not group in self.cfg['visible']:
                self.cfg['visible'].append(group)
            self.cfg['layer'].append(group)
            self.cfg['nodes'][group] = groups[group]
        return True

    def __getHiddenNodesFromSystem(self, system):
        """Create nodes from system."""

        self.cfg['hidden'] = []
        self.cfg['label_format'] = 'generic:string'
        if not 'nodes' in self.cfg:
            self.cfg['nodes'] = {}
        if not 'layer' in self.cfg:
            self.cfg['layer'] = []
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

    def __getEdgesFromNodesAndLayers(self):
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
        if self.isEmpty():
            nemoa.log('info', 'configuration is not needed: network is \'empty\'')
            return True

        # check if dataset instance is available
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error', 'could not configure network: no valid dataset instance given!')
            return False
 
         # check if system instance is available
        if not nemoa.type.isSystem(system):
            nemoa.log('error', 'could not configure network: no valid system instance given!')
            return False

        nemoa.log('info', 'configure network: \'%s\'' % (self.getName()))
        nemoa.setLog(indent = '+1')

        # type: 'auto is used for networks
        # wich are created by datasets (visible units)
        # and systems (hidden units)
        if self.cfg['type'] == 'auto':
            self.__getVisibleNodesFromDataset(dataset)
            self.__getHiddenNodesFromSystem(system)
            self.__getEdgesFromNodesAndLayers()
            self.updateGraph()
            nemoa.setLog(indent = '-1')
            return True

        # type: 'autolayer' is used for networks
        # wich are created by layers and sizes
        if self.cfg['type'] == 'autolayer':
            self.__getNodesFromLayers()
            self.__getEdgesFromNodesAndLayers()
            self.updateGraph()
            nemoa.setLog(indent = '-1')
            return True

        # configure network to dataset
        groups = dataset.getColGroups()
        changes = []
        for group in groups:
            if not group in self.cfg['nodes'] \
                or not (groups[group] == self.cfg['nodes'][group]):
                self.updateGraph(nodelist = {'type': group, 'list': groups[group]})

        nemoa.setLog(indent = '-1')
        return True

    def getName(self):
        """Return name of network (as string)."""
        return self.cfg['name'] if 'name' in self.cfg else ''

    def isEmpty(self):
        """Return true if network type is 'empty'."""
        return self.cfg['type'] == 'empty'

    def updateGraph(self,
        nodelist = {'type': None, 'list': []},
        edgelist = {'type': (None, None), 'list': []}):
        """Create NetworkX graph instance."""

        # update node list from keyword arguments
        if nodelist['type'] in self.cfg['layer']:
            # count new nodes
            addNodes = 0
            for node in nodelist['list']:
                if not node in self.cfg['nodes'][nodelist['type']]:
                    newNodes += 1
            delNodes = 0
            for node in self.cfg['nodes'][nodelist['type']]:
                if not node in nodelist['list']:
                    delNodes += 1
            self.cfg['nodes'][nodelist['type']] = nodelist['list']

        # update edge list from keyword arguments
        if edgelist['type'][0] in self.cfg['layer'] and edgelist['type'][1] in self.cfg['layer']:
            indexA = self.cfg['layer'].index(edgelist['type'][0])
            indexB = self.cfg['layer'].index(edgelist['type'][1])
            if indexB - indexA == 1:
                edge_type = edgelist['type'][0] + '-' + edgelist['type'][1]
                self.cfg['edges'][edge_type] = edgelist['list']

        # filter edges to valid nodes
        for i in range(len(self.cfg['layer']) - 1):
            layerA = self.cfg['layer'][i]
            layerB = self.cfg['layer'][i + 1]
            edge_type = layerA + '-' + layerB
            filtered = []
            for nodeA, nodeB in self.cfg['edges'][edge_type]:
                if not nodeA in self.cfg['nodes'][layerA]:
                    continue
                if not nodeB in self.cfg['nodes'][layerB]:
                    continue
                filtered.append((nodeA, nodeB))
            self.cfg['edges'][edge_type] = filtered

        # reset and create new NetworkX graph Instance
        try:
            self.graph.clear()
            self.graph['name'] = self.cfg['name']
        except:
            self.graph = networkx.Graph(name = self.cfg['name'])

        # add nodes to graph
        sort_id = 0
        for layer_id, layer in enumerate(self.cfg['layer']):
            visible = layer in self.cfg['visible']
            if nodelist['type'] in self.cfg['layer']:
                if layer == nodelist['type']:
                    if addNodes > 0:
                        nemoa.log('info', 'adding %i nodes to layer: \'%s\'' % (addNodes, layer))
                    if delNodes > 0:
                        nemoa.log('info', 'deleting %i nodes from layer: \'%s\'' % (delNodes, layer))
            else:
                if visible:
                    nemoa.log('info', 'adding visible layer: \'' + layer + \
                        '\' (' + str(len(self.cfg['nodes'][layer])) + ' nodes)')
                else:
                    nemoa.log('info', 'adding hidden layer: \'' + layer + \
                        '\' (' + str(len(self.cfg['nodes'][layer])) + ' nodes)')
            for layer_node_id, node in enumerate(self.cfg['nodes'][layer]):
                id = layer + ':' + node

                if id in self.graph.nodes():
                    continue

                self.graph.add_node(
                    id,
                    label = node,
                    sort_id = sort_id,
                    params = {
                        'type': layer,
                        'type_id': layer_id,
                        'type_node_id': layer_node_id,
                        'visible': visible } )

                sort_id += 1

        # add edges to graph
        sort_id = 0
        for i in range(len(self.cfg['layer']) - 1):
            layerA = self.cfg['layer'][i]
            layerB = self.cfg['layer'][i + 1]
            edge_type = layerA + '-' + layerB
            type_id = i
            
            for (nodeA, nodeB) in self.cfg['edges'][edge_type]:
                src_node_id = layerA + ':' + nodeA
                tgt_node_id = layerB + ':' + nodeB
                
                self.graph.add_edge(
                    src_node_id, tgt_node_id,
                    weight = 0,
                    sort_id = sort_id,
                    params = {'type': edge_type, 'type_id': type_id})
                    
                sort_id += 1

        return True

    #
    # accessing nodes
    #
    
    # get network information of single node
    def node(self, node):
        return self.graph.node[node]

    # get list of nodes with specific attributes
    # example nodes(type = 'visible')
    def nodes(self, **params):

        # filter search criteria and order entries
        sorted_list = [None] * self.graph.number_of_nodes()

        for node, attr in self.graph.nodes(data = True):
            if not params == {}:
                passed = True
                for key in params:
                    if not key in attr['params'] \
                        or not params[key] == attr['params'][key]:
                        passed = False
                        break
                if not passed:
                    continue

            sorted_list[attr['sort_id']] = node

        # filter empty nodes
        filtered_list = []
        for node in sorted_list:
            if node:
                filtered_list.append(node)

        return filtered_list

    # 
    def node_labels(self, **params):
        list = []
        for node in self.nodes(**params):
            list.append(self.graph.node[node]['label'])
        
        return list
    
    def getNodeLabels(self, list):
        labels = []
        for node in list:#
            if not node in self.graph.node:
                return None
            
            labels.append(self.graph.node[node]['label'])
            
        return labels
    
    def getNodeGroups(self, type = None):
        
        # get groups of specific node type 
        if type:
            if not type in self.cfg:
                nemoa.log("warning", "unknown node type '" + str(type) + "'!")
                return None
            
            groups = {}
            for group in self.cfg[type]:
                groups[group] = self.node_labels(type = group)
            return groups
        
        # get all groups
        allGroups = {}
        for type in ['visible', 'hidden']:
            groups = {}
            for group in self.cfg[type]:
                groups[group] = self.node_labels(type = group)
            allGroups[type] = groups
        return allGroups

    #
    # accessing layers
    #

    def layer(self, layer):
        """Return dictionary containing information about a layer."""
        nodes = self.nodes(type = layer)
        if not nodes:
            return None
        fistNode = self.node(nodes[0])['params']
        return {
            'id': fistNode['type_id'],
            'label': fistNode['type'],
            'visible': fistNode['visible'],
            'nodes': nodes}

    def layers(self, **kwargs):
        """Return ordered list of layers by label."""
        layerDict = {self.node(node)['params']['type_id']: \
            {'label': self.node(node)['params']['type']} \
            for node in self.nodes()}
        layerList = [layerDict[layer]['label'] for layer in range(0, len(layerDict))]
        return layerList

    #
    # accessing edges
    #
    
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
                if not passed:
                    continue
                
            # force order (visible, hidden)
            src_type = src.split(':')[0]
            tgt_type = tgt.split(':')[0]
            
            if src_type in self.cfg['visible'] and tgt_type in self.cfg['hidden']:
                sorted_list[attr['sort_id']] = (src, tgt)
            elif src_type in self.cfg['hidden'] and tgt_type in self.cfg['visible']:
                sorted_list[attr['sort_id']] = (tgt, src)
                
        # filter empty nodes
        filtered_list = []
        for edge in sorted_list:
            if edge:
                filtered_list.append(edge)

        return filtered_list
    
    def edge_labels(self, **kwargs):
        list = []
        for src, tgt in self.edges(**kwargs):
            src_label = self.graph.node[src]['label']
            tgt_label = self.graph.node[tgt]['label']
            list.append((src_label, tgt_label))
        return list
    
    #
    # get / set
    #
    
    def _get(self, sec = None):
        dict = {
            'cfg': copy.deepcopy(self.cfg),
            'graph': copy.deepcopy(self.graph)
        }

        if not sec:
            return dict
        if sec in dict:
            return dict[sec]

        return None
    
    def _set(self, **dict):
        if 'cfg' in dict:
            self.cfg = copy.deepcopy(dict['cfg'])
        if 'graph' in dict:
            self.graph = copy.deepcopy(dict['graph'])

        return True

    def save_graph(self, file = None, format = 'gml'):
        if file == None:
            nemoa.log("critical", "no save path was given")
            
        # create path if not available
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        # everythink seems to be fine
        # nemoa.log("info", "saving graph to %s" % (file))
        
        if format == 'gml':
            G = self.graph.copy()
            networkx.write_gml(G, file)
    
