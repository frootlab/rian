# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.fileexport.archive
import nemoa.network.fileexport.graph
import nemoa.network.fileexport.image

def filetypes(filetype = None):
    """Get supported network export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.network.fileexport.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported graph description file types
    graph_types = nemoa.network.fileexport.graph.filetypes()
    for key, val in graph_types.items():
        type_dict[key] = ('graph', val)

    # get supported image filetypes
    image_types = nemoa.network.fileexport.image.filetypes()
    for key, val in image_types.items():
        type_dict[key] = ('image', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def save(network, path = None, filetype = None, workspace = None,
    **kwargs):
    """Export network to file.

    Args:
        network (object): nemoa network instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.is_network(network):
        return nemoa.log('error', """could not save network to file:
            network is not valid.""")

    # display output
    if 'output' in kwargs and kwargs['output'] == 'display':
        return nemoa.network.fileexport.image.save(
            network, **kwargs)

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
                    workspace '%s' does not exist""" % (workspace))
                return  {}

        # get network path from workspace
        path = nemoa.workspace.path('networks') + path

        # import previous workspace if workspace differs from current
        if not workspace == current_workspace:
            if not current_workspace == None:
                nemoa.workspace.load(current_workspace)

    # get filetype from file extension if not given
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not export network:
            filetype '%s' is not supported.""" % (filetype))

    module_name = filetypes(filetype)[0]
    if module_name == 'graph':
        return nemoa.network.fileexport.graph.save(
            network, path, filetype, **kwargs)
    if module_name == 'archive':
        return nemoa.network.fileexport.archive.save(
            network, path, filetype, **kwargs)
    if module_name == 'image':
        return nemoa.network.fileexport.image.save(
            network, path, filetype, **kwargs)

    return False
