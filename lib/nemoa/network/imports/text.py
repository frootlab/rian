# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

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
    filetype = nemoa.common.ospath.fileext(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import graph:
            filetype '%s' is not supported.""" % filetype)

    if filetype in ['ini', 'txt']:
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import network configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def load(self, path):
        """Return network configuration as dictionary.

        Args:
            path: configuration file used to generate network
                configuration dictionary.

        """

        structure = {'network': { 'type': 'str' }}
        network = nemoa.common.inifile.load(path, structure)
        if not network \
            or not 'network' in network \
            or not 'type' in network['network']:
            return nemoa.log('error', """could not import network:
                configuration file '%s' is not valid.""" % path)

        if network['network']['type'] in \
            ['layer.MultiLayer', 'layer.Shallow', 'layer.Factor']:
            return self._parse_layer_network(path)

        return nemoa.log('error', """could not import network
            configuration file '%s' contains unsupported network
            type '%s'.""" % (path, network['network']['type']))

    def _parse_layer_network(self, path):

        structure = {
            'network': {
                'name': 'str',
                'branch': 'str',
                'version': 'str',
                'about': 'str',
                'author': 'str',
                'email': 'str',
                'license': 'str',
                'type': 'str',
                'labelformat': 'str',
                'layers': 'list'},
            'layer [0-9a-zA-Z]*': {
                'function': 'str',
                'distribution': 'str',
                'type': 'str',
                'file': 'str',
                'nodes': 'list',
                'size': 'int' },
            'binding [0-9a-zA-Z]*-[0-9a-zA-Z]*': {
                '[0-9a-zA-Z]*': 'list' }}

        ini_dict = nemoa.common.inifile.load(path,
            structure = structure)
        config = ini_dict['network'].copy()

        # layers
        if not 'layers' in config:
            return nemoa.log('warning', """file '%s' does not
                contain parameter 'layers'.""" % path)
        config['layer'] = config['layers']
        del config['layers']

        # name
        if not 'name' in config:
            config['name'] = nemoa.common.ospath.basename(path)

        # node labelformat
        if not 'labelformat' in config:
            config['labelformat'] = 'generic:string'

        # init network dictionary
        config['nodes'] = {}
        config['edges'] = {}
        config['layers'] = {}

        visible_layer_ids = [0, len(config['layer']) - 1]

        # [layer *]
        for layer_id, layer in enumerate(config['layer']):

            layer_section = 'layer ' + layer
            if not layer_section in ini_dict:
                return nemoa.log('warning', """could not import layer
                    network: file '%s' does not contain information
                    about layer '%s'.""" % (path, layer))

            config['layers'][layer] = {}
            config['layers'][layer]['visible'] = \
                layer_id in visible_layer_ids

            # get type of layer nodes
            if 'type' in ini_dict[layer_section]:
                config['layers'][layer]['type'] = \
                    ini_dict[layer_section]['type']

            # get function of layer nodes
            if 'function' in ini_dict[layer_section]:
                config['layers'][layer]['function'] = \
                    ini_dict[layer_section]['function']

            # get distribution of layer nodes
            if 'distribution' in ini_dict[layer_section]:
                config['layers'][layer]['distribution'] = \
                    ini_dict[layer_section]['distribution']

            # get nodes of layer from given list file ('file')
            if 'file' in ini_dict[layer_section]:
                file_str = ini_dict[layer_section]['file']
                list_file = nemoa.workspace._expand_path(file_str)
                if not os.path.exists(list_file):
                    return nemoa.log('error', """listfile '%s'
                        does not exists!""" % list_file)
                with open(list_file, 'r') as list_file:
                    fileLines = list_file.readlines()
                node_list = [node.strip() for node in fileLines]

            # get nodes of layer from given list ('nodes')
            elif 'nodes' in ini_dict[layer_section]:
                node_list = ini_dict[layer_section]['nodes']

            # get nodes of layer from given layer size ('size')
            elif 'size' in ini_dict[layer_section]:
                layer_size = ini_dict[layer_section]['size']
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
            if not edge_section in ini_dict:
                for src_node in config['nodes'][src_layer]:
                    for tgt_node in config['nodes'][tgt_layer]:
                        edge = (src_node, tgt_node)
                        config['edges'][edge_layer].append(edge)
                continue

            # get edges from '[binding *]' section
            for src_node in ini_dict[edge_section]:
                src_node = src_node.strip()
                if src_node == '':
                    continue
                if not src_node in config['nodes'][src_layer]:
                    continue
                for tgt_node in ini_dict[edge_section][src_node]:
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

        return { 'config': config }
