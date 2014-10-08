# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import ConfigParser
import nemoa
import os

class Ini:
    """Import network configuration from ini files."""

    _workspace = None

    def __init__(self, workspace = None):
        self._workspace = workspace

    def load(self, path):
        """Return network configuration as dictionary.

        Args:
            file: .ini configuration file used to generate nemoa
                network compatible configuration dictionary.

        """

        netcfg = ConfigParser.ConfigParser()
        netcfg.optionxform = str
        netcfg.read(path)

        name = os.path.splitext(os.path.basename(path))[0]
        #if isinstance(self._workspace, str) and self._workspace:
            #fullname = '.'.join([self._workspace, name])
        #else:
            #fullname = name

        network = {
            #'class': 'network',
            #'name': fullname,
            #'workspace': self._workspace,
            'config': {
                'name': name,
                'type': None,
                'about': None,
                'author': None,
                'email': None,
                'license': None,
                'label_format': 'generic:string',
                'source': {
                    'file': path,
                    'file_format': 'ini' }}}

        # [network]
        if not 'network' in netcfg.sections():
            return nemoa.log('warning', """could not import network
                configuration: file '%s' does not contain section
                'network'!""" % (path))

        # 'name': name of network
        if 'name' in netcfg.options('network'):
            network_name = netcfg.get('network', 'name').strip()
            network['name'] = \
                '.'.join([self._workspace, network_name])
            network['config']['name'] = network_name

        # 'about': short description of the network
        if 'about' in netcfg.options('network'):
            network['config']['about'] = \
                netcfg.get('network', 'about').strip()

        # 'author': author of network
        if 'author' in netcfg.options('network'):
            network['config']['author'] = \
                netcfg.get('network', 'author').strip()

        # 'email': email of author of network
        if 'email' in netcfg.options('network'):
            network['config']['email'] = \
                netcfg.get('network', 'email').strip()

        # 'license': license of network
        if 'license' in netcfg.options('network'):
            network['config']['license'] = \
                netcfg.get('network', 'license').strip()

        # 'type': type of network
        if 'type' in netcfg.options('network'):
            network['config']['type'] = \
                netcfg.get('network', 'type').strip()

        # 'labelformat': annotation of nodes
        if 'labelformat' in netcfg.options('network'):
            network['config']['label_format'] \
                = netcfg.get('network', 'labelformat').strip()

        # depending on type, use different class methods to parse
        # and interpret type specific parameters and sections
        if network['config']['type'] == 'layer.MultiLayer':
            return self._configure_graph(path, netcfg, network)
        if network['config']['type'] == 'layer.Shallow':
            return self._configure_graph(path, netcfg, network)
        if network['config']['type'] == 'layer.Factor':
            return self._configure_graph(path, netcfg, network)

        return nemoa.log('warning', """could not import network
            configuration: file '%s' contains unsupported network
            type '%s'.""" % (path, network['config']['type']))

    def _configure_graph(self, path, netcfg, network):

        config = network['config']

        # 'layers': ordered list of network layers
        if not 'layers' in netcfg.options('network'):
            return nemoa.log('warning', """file '%s' does not
                contain parameter 'layers'.""" % (path))
        else: config['layer'] = nemoa.common.str_to_list(
            netcfg.get('network', 'layers'))

        # init network dictionary
        config['visible'] = []
        config['hidden'] = []
        config['nodes'] = {}
        config['edges'] = {}

        visible_layer_ids = [0, len(config['layer']) - 1]

        # [layer *]
        for layer_id, layer in enumerate(config['layer']):

            layer_section = 'layer ' + layer
            if not layer_section in netcfg.sections():
                return nemoa.log('warning', """could not import layer
                    network: file '%s' does not contain information
                    about layer '%s'.""" % (path, layer))

            # TODO: type in ('gauss', 'sigmoid', 'linear')
            # get type of layer ('type')
            # layer type can be ether 'visible' or 'hidden'
            if layer_id in visible_layer_ids:
                config['visible'].append(layer)
            else:
                config['hidden'].append(layer)

            # get nodes of layer from given list file ('file')
            if 'file' in netcfg.options(layer_section):
                file_str = netcfg.get(layer_section, 'file')
                list_file = nemoa.workspace._expand_path(file_str)
                if not os.path.exists(list_file):
                    return nemoa.log('error', """listfile '%s'
                        does not exists!""" % (list_file))
                with open(list_file, 'r') as list_file:
                    fileLines = list_file.readlines()
                node_list = [node.strip() for node in fileLines]
            # get nodes of layer from given list ('nodes')
            elif 'nodes' in netcfg.options(layer_section):
                node_str = netcfg.get(layer_section, 'nodes')
                node_list = nemoa.common.str_to_list(node_str)
            # get nodes of layer from given layer size ('size')
            elif 'size' in netcfg.options(layer_section):
                layer_size = int(netcfg.get(layer_section, 'size'))
                node_list = []
                for n in xrange(1, layer_size + 1):
                    node_list.append('n%s' % (n))
            else:
                return nemoa.log('warning', """could not import layer
                    network: layer '%s' does not contain valid node
                    information!""" % (layer))

            config['nodes'][layer] = []
            for node in node_list:
                node = node.strip()
                if node == '': continue
                if not node in config['nodes'][layer]:
                    config['nodes'][layer].append(node)

        # parse '[binding *]' sections and add edges to network dict
        for i in xrange(len(config['layer']) - 1):
            src_layer = config['layer'][i]
            tgt_layer = config['layer'][i + 1]

            edge_layer = (src_layer, tgt_layer)
            config['edges'][edge_layer] = []
            edge_section = 'binding %s-%s' % (src_layer, tgt_layer)

            # create full binfing between two layers if not specified
            if not edge_section in netcfg.sections():
                for src_node in config['nodes'][src_layer]:
                    for tgt_node in config['nodes'][tgt_layer]:
                        edge = (src_node, tgt_node)
                        config['edges'][edge_layer].append(edge)
                continue

            # get edges from '[binding *]' section
            for src_node in netcfg.options(edge_section):
                src_node = src_node.strip()
                if src_node == '':
                    continue
                if not src_node in config['nodes'][src_layer]:
                    continue
                for tgt_node in nemoa.common.str_to_list(
                    netcfg.get(edge_section, src_node)):
                    tgt_node = tgt_node.strip()
                    if tgt_node == '':
                        continue
                    if not tgt_node in config['nodes'][tgt_layer]:
                        continue
                    edge = (src_node, tgt_node)
                    if edge in config['edges'][edge_layer]:
                        continue
                    config['edges'][edge_layer].append(edge)

        # check network binding
        for i in xrange(len(config['layer']) - 1):
            src_layer = config['layer'][i]
            tgt_layer = config['layer'][i + 1]

            edge_layer = (src_layer, tgt_layer)
            if config['edges'][edge_layer] == []:
                return nemoa.log('warning', """layer '%s' and
                    layer '%s' are not connected!"""
                    % (src_layer, tgt_layer))

        return network
