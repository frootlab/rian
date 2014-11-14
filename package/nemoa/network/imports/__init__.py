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

def load(path, filetype = None, workspace = None, **kwargs):
    """Import network dictionary from file or workspace."""

    # try if path exists or import given workspace and get path from
    # workspace or get path from current workspace
    if not os.path.isfile(path) and workspace:
        current_workspace = nemoa.workspace.name()
        if not workspace == current_workspace:
            if not nemoa.workspace.load(workspace):
                nemoa.log('error', """could not import network:
                    workspace '%s' does not exist""" % (workspace))
                return  {}
        config = nemoa.workspace.get('network', path)
        if not workspace == current_workspace and current_workspace:
            nemoa.workspace.load(current_workspace)
        if not isinstance(config, dict):
            nemoa.log('error', """could not import network:
                workspace '%s' does not contain a network '%s'."""
                % (workspace, path))
            return  {}
        if not 'path' in config:
            return {'config': config}
        path = config['path']
    if not os.path.isfile(path):
        config = nemoa.workspace.get('network', path)
        if not isinstance(config, dict):
            current_workspace = nemoa.workspace.name()
            if current_workspace:
                nemoa.log('error', """could not import network:
                    current workspace '%s' does not contain a network
                    '%s'.""" % (current_workspace, path))
            else:
                nemoa.log('error', """could not import network:
                    file '%s' does not exist.""" % (path))
            return  {}
        if not 'path' in config: return {'config': config}
        path = config['path']
    if not os.path.isfile(path):
        nemoa.log('error', """could not import network:
            file '%s' does not exist.""" % (path))
        return {}

    # if filetype is not given get filtype from file extension
    # and test if filetype is supported
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not import network:
            filetype '%s' is not supported.""" % (filetype))

    # import, check and update dictionary
    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        network = nemoa.network.imports.archive.load(path, **kwargs)
    elif module_name == 'graph':
        network = nemoa.network.imports.graph.load(path, **kwargs)
    elif module_name == 'text':
        network = nemoa.network.imports.text.load(path, **kwargs)
    if not network:
        nemoa.log('error', """could not import network: file '%s' is
            not valid.""" % (path))
        return {}
    network['config']['path'] = path
    network['config']['workspace'] = nemoa.workspace.name()

    return network

