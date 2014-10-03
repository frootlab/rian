# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import ConfigParser
import nemoa
import os

def open(path, file_format = None):
    """Import network configuration from file."""

    if not os.path.isfile(path):
        return nemoa.log('error', """could not import network:
            file does not exist '%s'.""" % (path))

    # if format is not given get format from file extension
    if not file_format:
        file_name = os.path.basename(path)
        file_ext = os.path.splitext(file_name)[1]
        file_format = file_ext.lstrip('.').strip().lower()

    # get network configuration from file
    if file_format == 'ini':
        import_class = nemoa.network.importer.Ini()
    else:
        return nemoa.log('error', """could not import network '%s':
            file format '%s' is currently not supported.""" %
            (path, file_format))

    return import_class.load(path)

class Ini:
    """import network configuration from ini files."""

    workspace = None

    def __init__(self):
        self.workspace = nemoa.workspace.name()

    def load(self, file):
        """Return network configuration as dictionary.

        Args:
            file: .ini configuration file used to generate nemoa
                network compatible configuration dictionary.

        """

        netcfg = ConfigParser.ConfigParser()
        netcfg.optionxform = str
        netcfg.read(file)

        name = os.path.splitext(os.path.basename(file))[0]
        if nemoa.workspace.name():
            fullname = '.'.join([nemoa.workspace.name(), name])
        else:
            fullname = name

        network = {
            'class': 'network',
            'name': fullname,
            'workspace': self.workspace,
            'config': {
                'package': 'base',
                'class': 'network',
                'type': None,
                'name': name,
                'source': {
                    'file': file,
                    'file_format': 'ini' }}}

        # validate 'network' section
        if not 'network' in netcfg.sections():
            return nemoa.log('warning', """could not import network
                configuration: file '%s' does not contain section
                'network'!""" % (file))

        # name of network ('name')
        if 'name' in netcfg.options('network'):
            network_name = netcfg.get('network', 'name').strip()
            network['config']['name'] = network_name
            network['name'] = \
                '.'.join([self.workspace, network_name])

        # short description of the network ('description')
        if 'description' in netcfg.options('network'):
            network['config']['description'] = \
                netcfg.get('network', 'description').strip()
        else: network['config']['description'] = ''

        # python module containing the network class ('package')
        if 'package' in netcfg.options('network'):
            network['config']['package'] = \
                netcfg.get('network', 'package').strip()

        # python network class inside module ('class')
        if 'class' in netcfg.options('network'):
            network['config']['class'] = \
                netcfg.get('network', 'class').strip()

        # type of network ('type')
        # currently supported:
        #     'layer': layered feedforward network
        if 'type' in netcfg.options('network'):
            network['config']['type'] = \
                netcfg.get('network', 'type').strip().lower()
        else: network['config']['type'] = 'auto'

        # TODO: make network type specific sections
        # 'labelformat': annotation of nodes, default: 'generic:string'
        if 'labelformat' in netcfg.options('network'):
            network['config']['label_format'] \
                = netcfg.get('network', 'nodes').strip()
        else: network['config']['label_format'] = 'generic:string'

        # depending on type, use different class methods to parse
        # and interpret type specific parameters and sections
        if network['config']['type'] in ['layer', 'auto']:
            return self._parse_layer_network(file, netcfg, network)

        return nemoa.log('warning',
            """could not import network configuration:
            file '%s' contains unsupported network type '%s'.""" %
            (file, network['config']['type']))

    def _parse_layer_network(self, file, netcfg, network):

        config = network['config']

        # 'layers': ordered list of network layers
        if not 'layers' in netcfg.options('network'):
            return nemoa.log('warning', """file '%s' does not
                contain parameter 'layers'.""" % (file))
        else: config['layer'] = nemoa.common.str_to_list(
            netcfg.get('network', 'layers'))

        # init network dictionary
        config['visible'] = []
        config['hidden'] = []
        config['nodes'] = {}
        config['edges'] = {}

        # parse '[layer *]' sections and add nodes
        # and layer types to network dict
        for layer in config['layer']:
            layer_section = 'layer ' + layer
            if not layer_section in netcfg.sections():
                return nemoa.log('warning', """file '%s' does not
                    contain information about layer '%s'."""
                    % (file, layer))

            # TODO: type in ('gauss', 'sigmoid', 'linear')
            # get type of layer ('type')
            # layer type can be ether 'visible' or 'hidden'
            if not 'type' in netcfg.options(layer_section):
                return nemoa.log('warning', """type of layer '%s'
                    has to be specified ('visible', 'hidden')!"""
                    % (layer))
            layer_type = netcfg.get(layer_section, 'type').lower()
            if layer_type == 'visible':
                config['visible'].append(layer)
            elif layer_type == 'hidden':
                config['hidden'].append(layer)
            else:
                return nemoa.log('warning',
                    "unknown type of layer '" + layer + "'!")

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
                return nemoa.log('warning',
                    """layer '%s' does not contain
                    node information!""" % (layer))

            config['nodes'][layer] = []
            for node in node_list:
                node = node.strip()
                if node == '': continue
                if not node in config['nodes'][layer]:
                    config['nodes'][layer].append(node)

        # check network layers
        if config['visible'] == []:
            return nemoa.log('error', """could not parse network:
                file '%s' does not contain visible layers!"""
                % (file))

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
