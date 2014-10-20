# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.fileexport.archive
import nemoa.system.fileexport.image

def filetypes(filetype = None):
    """Get supported system export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.system.fileexport.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported image filetypes
    image_types = nemoa.system.fileexport.image.filetypes()
    for key, val in image_types.items():
        type_dict[key] = ('image', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def save(system, path = None, filetype = None, workspace = None,
    **kwargs):
    """Export system to file.

    Args:
        system (object): nemoa system instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.is_system(system):
        return nemoa.log('error', """could not save system to file:
            system is not valid.""")

    # display output
    if 'output' in kwargs and kwargs['output'] == 'display':
        return nemoa.system.fileexport.image.save(
            system, **kwargs)

    # get file path from system source file if path is not given
    if path == None:
        source = system.get('config', 'source')
        source_path = source['file']
        file_directory = nemoa.common.get_file_directory(source_path)
        file_basename = system.get('fullname')
        if filetype == None:
            file_extension \
                = nemoa.common.get_file_extension(source_path)
        else:
            file_extension = filetype
        path = '%s/%s.%s' % (file_directory, file_basename,
            file_extension)

    # get file path from workspace/path if workspace is given
    elif isinstance(workspace, str) and not workspace == 'None':

        # import workspace if workspace differs from current
        current_workspace = nemoa.workspace.name()
        if not workspace == current_workspace:
            if not nemoa.workspace.load(workspace):
                nemoa.log('error', """could not export system:
                    workspace '%s' does not exist""" % (workspace))
                return  {}

        # get system path from workspace
        path = nemoa.workspace.path('systems') + path

        # import previous workspace if workspace differs from current
        if not workspace == current_workspace:
            if not current_workspace == None:
                nemoa.workspace.load(current_workspace)

    # get filetype from file extension if not given
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not export system:
            filetype '%s' is not supported.""" % (filetype))

    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        return nemoa.system.fileexport.archive.save(
            system, path, filetype, **kwargs)
    if module_name == 'image':
        return nemoa.system.fileexport.image.save(
            system, path, filetype, **kwargs)

    return False
