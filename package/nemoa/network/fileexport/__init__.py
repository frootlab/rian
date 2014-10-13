# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa
import os

def save(network, path = None, file_format = None, workspace = None,
    **kwargs):
    """Export network configuration to file.

    Args:
        network (object): nemoa network instance
        path (str, optional): export file path
        file_format (str, optional): export file format
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
        if not file_format == None:
            file_path = nemoa.common.get_file_path(path)
            file_basename = nemoa.common.get_file_basename(path)
            path = '%s/%s.%s' % (file_path, file_basename, file_format)

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

    # if format is not given get format from file extension
    if not file_format:
        print path
        file_format = nemoa.common.get_file_ext(path).lower()

    # get network file exporter
    module_name = 'nemoa.network.fileexport.%s' % (file_format)
    class_name = file_format.title()
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        exporter = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not export network '%s':
            file format '%s' is not supported.""" %
            (network.get('name'), file_format))

    # export network file
    return exporter.save(network, path)
