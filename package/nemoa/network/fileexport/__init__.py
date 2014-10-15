# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa
import os

def save(network, path = None, filetype = None, workspace = None,
    **kwargs):
    """Export network to file.

    Args:
        network (object): nemoa network instance
        path (str, optional): path of export file
        filetype (str, optional): filetype export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.is_network(network):
        return nemoa.log('error', """could not save network to file:
            network is not valid.""")

    # get file path from network source file if path not given
    if path == None:
        source = network.get('config', 'source')
        path = source['file']
        if not filetype == None:
            file_path = nemoa.common.get_file_directory(path)
            file_basename = nemoa.common.get_file_basename(path)
            path = '%s/%s.%s' % (file_path, file_basename, filetype)

    # get file path from workspace/path if workspace is given
    elif isinstance('workspace', str):

        # import workspace if workspace differs from current
        current_workspace = nemoa.workspace.name()
        if not workspace == current_workspace:
            if not nemoa.workspace.load(workspace):
                nemoa.log('error', """could not export network:
                    workspace '%s' does not exist"""
                    % (workspace))
                return  {}

        # get network path from workspace
        path = nemoa.workspace.path('networks') + path

        # import previous workspace if workspace differs from current
        if not workspace == current_workspace:
            if not current_workspace == None:
                nemoa.workspace.load(current_workspace)

    # get file export module name from filetype
    if filetype:
        module_name = 'nemoa.network.fileexport.%s' % (filetype)
    else:
        module_name = 'nemoa.network.fileexport.%s' % (
            nemoa.common.get_file_extension(path).lower())

    # import network file export module
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, 'save'):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not export network '%s':
            filetype '%s' is not supported.""" %
            (network.get('name'), filetype))

    # export network
    return module.save(network, path, **kwargs)
