# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.exports.archive

def filetypes(filetype = None):
    """Get supported system export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.system.exports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

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

    if not nemoa.common.type.issystem(system):
        return nemoa.log('error', """could not export system to file:
            system is not valid.""")

    # get file path from system source file if path is not given
    if path == None:
        path = system.path

        if filetype:
            filename = '%s.%s' % (system.fullname, filetype)
        else:
            fileext = nemoa.common.get_file_extension(path)
            filename = '%s.%s' % (system.fullname, fileext)

        filedir = nemoa.common.get_file_directory(path)
        path = '%s/%s.%s' % (filedir, filename)

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
        return nemoa.system.exports.archive.save(
            system, path, filetype, **kwargs)

    return False
