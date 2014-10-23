# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import ConfigParser
import nemoa
import os

def filetypes():
    """Get supported text filetypes for network import."""
    return {
        'ini': 'Nemoa Network Description',
        'txt': 'Nemoa Network Description'}

def load(path, **kwargs):
    """Import network from text file."""

    # extract filetype from path
    filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import graph:
            filetype '%s' is not supported.""" % (filetype))

    if filetype in ['ini', 'txt']:
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import network configuration from ini file."""

    settings = {}

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        """Return network configuration as dictionary.

        Args:
            path: configuration file used to generate network
                configuration dictionary.

        """

        netcfg = ConfigParser.ConfigParser()
        netcfg.optionxform = str
        netcfg.read(path)

        name = os.path.splitext(os.path.basename(path))[0]

        network = {
            'config': {
                'name': name,
                'branch': None,
                'version': None,
                'about': None,
                'author': None,
                'email': None,
                'license': None,
                'type': None,
                'labelformat': 'generic:string',
                'source': {
                    'file': path,
                    'filetype': 'ini' }}}

        # [network] section
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

        # 'branch': branch of the network
        if 'branch' in netcfg.options('network'):
            network['config']['branch'] = \
                netcfg.get('network', 'branch').strip()

        # 'version': version number of network branch
        if 'version' in netcfg.options('network'):
            network['config']['version'] = \
                int(netcfg.get('network', 'about'))

        # 'about': short description of the network
        if 'about' in netcfg.options('network'):
            network['config']['about'] = \
                netcfg.get('network', 'about').strip()

        # 'author': author of the network
        if 'author' in netcfg.options('network'):
            network['config']['author'] = \
                netcfg.get('network', 'author').strip()

        # 'email': email of the author of the network
        if 'email' in netcfg.options('network'):
            network['config']['email'] = \
                netcfg.get('network', 'email').strip()

        # 'license': license of the network
        if 'license' in netcfg.options('network'):
            network['config']['license'] = \
                netcfg.get('network', 'license').strip()

        # 'type': type of the network
        if 'type' in netcfg.options('network'):
            network['config']['type'] = \
                netcfg.get('network', 'type').strip()

        # 'labelformat': annotation of the nodes
        if 'labelformat' in netcfg.options('network'):
            network['config']['labelformat'] \
                = netcfg.get('network', 'labelformat').strip()

        # depending on type, use different methods to parse and
        # interpret parameters and sections
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
        else:
            config['layer'] = nemoa.common.str_to_list(
                netcfg.get('network', 'layers'))

        # init network dictionary
        config['visible'] = []
        config['hidden'] = []
        config['nodes'] = {}
        config['edges'] = {}
        config['layers'] = {}

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

            config['layers'][layer] = {}
            config['layers'][layer]['visible'] = \
                layer_id in visible_layer_ids

            # get type of layer nodes
            if 'type' in netcfg.options(layer_section):
                config['layers'][layer]['type'] = \
                    netcfg.get(layer_section, 'type')

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

            # create full binding between two layers if not specified
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
