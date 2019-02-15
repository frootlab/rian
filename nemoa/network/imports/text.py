# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for network import."""
    return {
        'ini': 'Nemoa Network Description',
        'txt': 'Nemoa Network Description'}

def load(path, **kwds):
    """Import network from text file."""

    from flab.base import env

    # extract filetype from path
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    if filetype in ['ini', 'txt']:
        return Ini(**kwds).load(path)

    return False

class Ini:
    """Import network configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """Return network configuration as dictionary.

        Args:
            path: configuration file used to generate network
                configuration dictionary.

        """
        from flab.io import ini

        scheme = {
            'network': {
                'type': str}}
        network = ini.load(path, scheme=scheme)
        if not network \
            or not 'network' in network \
            or not 'type' in network['network']:
            raise ValueError("could not import network: "
                "configuration file '%s' is not valid." % path)

        if network['network']['type'] in \
            ['layer.MultiLayer', 'layer.Shallow', 'layer.Factor']:
            return self._parse_layer_network(path)

        raise ValueError("could not import network "
            "configuration file '%s' contains unsupported network "
            "type '%s'." % (path, network['network']['type']))

    def _parse_layer_network(self, path):
        from flab.base import env
        from flab.io import ini

        scheme = {
            'network': {
                'name': str,
                'description': str,
                'branch': str,
                'version': str,
                'about': str,
                'author': str,
                'email': str,
                'license': str,
                'type': str,
                'layers': list,
                'directed': bool,
                'labelformat': str},
            'layer [0-9a-zA-Z]*': {
                'name': str,
                'function': str,
                'distribution': str,
                'type': str,
                'visible': bool,
                'file': str,
                'nodes': list,
                'size': int},
            'binding [0-9a-zA-Z]*-[0-9a-zA-Z]*': {
                '[0-9a-zA-Z]*': list}}

        ini_dict = ini.load(path, scheme=scheme)
        config = ini_dict['network'].copy()

        # layers
        if 'layers' not in config:
            raise Warning("""file '%s' does not
                contain parameter 'layers'.""" % path)
        config['layer'] = config['layers']
        del config['layers']

        # name
        if 'name' not in config:
            config['name'] = env.basename(path)

        # directed
        if 'directed' not in config:
            config['directed'] = True

        # node labelformat
        if 'labelformat' not in config:
            config['labelformat'] = 'generic:string'

        # init network dictionary
        config['nodes'] = {}
        config['edges'] = {}
        config['layers'] = {}

        visible_layer_ids = [0, len(config['layer']) - 1]

        # [layer *]
        for layer_id, layer in enumerate(config['layer']):

            layer_section = 'layer ' + layer
            if layer_section not in ini_dict:
                raise Warning("""could not import layer
                    network: file '%s' does not contain information
                    about layer '%s'.""" % (path, layer))

            sec_data = ini_dict[layer_section]
            config['layers'][layer] = {}
            lay_data = config['layers'][layer]

            # get name of layer
            lay_data['name'] = sec_data.get('name')

            # get visibility (observable, latent) of nodes in layer
            if 'visible' in sec_data:
                lay_data['visible'] = sec_data['visible']
            else:
                lay_data['visible'] = layer_id in visible_layer_ids

            # get type of layer nodes
            if 'type' in sec_data:
                lay_data['type'] = sec_data.get('type')

            # get function of layer nodes
            if 'function' in sec_data:
                lay_data['function'] = sec_data.get('function')

            # get distribution of layer nodes
            if 'distribution' in sec_data:
                lay_data['distribution'] = sec_data.get('distribution')

            # get nodes of layer from given list file ('file')
            # or from list ('nodes') or from given layer size ('size')
            if 'file' in sec_data:
                file_str = sec_data['file']
                list_file = nemoa.workspace._expand_path(file_str)
                if not os.path.exists(list_file):
                    raise ValueError("""listfile '%s'
                        does not exists!""" % list_file)
                with open(list_file, 'r') as list_file:
                    fileLines = list_file.readlines()
                node_list = [node.strip() for node in fileLines]
            elif 'nodes' in sec_data:
                node_list = sec_data['nodes']
            elif 'size' in sec_data:
                node_list = ['n%s' % (n) \
                    for n in range(1, sec_data['size'] + 1)]
            else:
                raise Warning("""could not import layer
                    network: layer '%s' does not contain valid node
                    information!""" % (layer))

            config['nodes'][layer] = []
            for node in node_list:
                node = node.strip()
                if node == '':
                    continue
                if node not in config['nodes'][layer]:
                    config['nodes'][layer].append(node)

        # parse '[binding *]' sections and add edges to network dict
        for i in range(len(config['layer']) - 1):
            src_layer = config['layer'][i]
            tgt_layer = config['layer'][i + 1]

            edge_layer = (src_layer, tgt_layer)
            config['edges'][edge_layer] = []
            edge_section = 'binding %s-%s' % (src_layer, tgt_layer)

            # create full binding between two layers if not specified
            if edge_section not in ini_dict:
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
                if src_node not in config['nodes'][src_layer]:
                    continue
                for tgt_node in ini_dict[edge_section][src_node]:
                    tgt_node = tgt_node.strip()
                    if tgt_node == '':
                        continue
                    if tgt_node not in config['nodes'][tgt_layer]:
                        continue
                    edge = (src_node, tgt_node)
                    if edge in config['edges'][edge_layer]:
                        continue
                    config['edges'][edge_layer].append(edge)

        # check network binding
        for i in range(len(config['layer']) - 1):
            src_layer = config['layer'][i]
            tgt_layer = config['layer'][i + 1]

            edge_layer = (src_layer, tgt_layer)
            if config['edges'][edge_layer] == []:
                raise Warning("""layer '%s' and
                    layer '%s' are not connected!"""
                    % (src_layer, tgt_layer))

        return {'config': config}
