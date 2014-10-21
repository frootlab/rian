# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.imports.archive
import nemoa.network.imports.graph
import nemoa.network.imports.text
import os

def filetypes(filetype = None):
    """Get supported network import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.network.imports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported graph description filetypes
    graph_types = nemoa.network.imports.graph.filetypes()
    for key, val in graph_types.items():
        type_dict[key] = ('graph', val)

    # get supported text filetypes
    text_types = nemoa.network.imports.text.filetypes()
    for key, val in text_types.items():
        type_dict[key] = ('text', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwargs):
    """Import network from file."""

    # get path
    if os.path.isfile(path):
        pass
    elif 'workspace' in kwargs:
        # import workspace and get path and filetype from workspace
        if not kwargs['workspace'] == nemoa.workspace.name():
            if not nemoa.workspace.load(kwargs['workspace']):
                nemoa.log('error', """could not import network:
                    workspace '%s' does not exist"""
                    % (kwargs['workspace']))
                return  {}
        name = '.'.join([kwargs['workspace'], path])
        config = nemoa.workspace.get('network', name = name)
        if not isinstance(config, dict):
            nemoa.log('error', """could not import network:
                workspace '%s' does not contain network '%s'."""
                % (kwargs['workspace'], path))
            return  {}
        path = config['path']
    else:
        nemoa.log('error', """could not import network:
            file '%s' does not exist.""" % (path))
        return {}

    # if filetype is not given get filtype from file extension
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not import network:
            filetype '%s' is not supported.""" % (filetype))

    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        network_dict = nemoa.network.imports.archive.load(
            path, **kwargs)
    elif module_name == 'graph':
        network_dict = nemoa.network.imports.graph.load(
            path, **kwargs)
    elif module_name == 'text':
        network_dict = nemoa.network.imports.text.load(
            path, **kwargs)
    else:
        return False

    # update source
    if not 'source' in network_dict['config']:
        network_dict['config']['source'] = {}
    network_dict['config']['source']['file'] = path
    network_dict['config']['source']['filetype'] = filetype

    return network_dict

