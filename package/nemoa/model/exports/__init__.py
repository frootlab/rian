# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.exports.archive
import nemoa.model.exports.image

def filetypes(filetype = None):
    """Get supported model export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.model.exports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported image filetypes
    image_types = nemoa.model.exports.image.filetypes()
    for key, val in image_types.items():
        type_dict[key] = ('image', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def save(model, path = None, filetype = None, workspace = None,
    **kwargs):
    """Export model to file.

    Args:
        model (object): nemoa model instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.is_model(model):
        return nemoa.log('error', """could not export model to file:
            model is not valid.""")

    # get file path from model source file if path is not given
    if path == None:
        path = model.get('config', 'path')
        filedir = nemoa.common.get_file_directory(path)
        filename = model.get('fullname')
        if filetype: fileext = filetype
        else: fileext = nemoa.common.get_file_extension(path)
        path = '%s/%s.%s' % (filedir, filename, fileext)

    # get file path from workspace/path if workspace is given
    elif isinstance(workspace, str) and not workspace == 'None':

        # import workspace if workspace differs from current
        current_workspace = nemoa.workspace.name()
        if not workspace == current_workspace:
            if not nemoa.workspace.load(workspace):
                nemoa.log('error', """could not export model:
                    workspace '%s' does not exist""" % (workspace))
                return  {}

        # get model path from workspace
        path = nemoa.workspace.path('models') + path

        # import previous workspace if workspace differs from current
        if not workspace == current_workspace:
            if not current_workspace == None:
                nemoa.workspace.load(current_workspace)

    # get filetype from file extension if not given
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not export model:
            filetype '%s' is not supported.""" % (filetype))

    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        return nemoa.model.exports.archive.save(
            model, path, filetype, **kwargs)
    if module_name == 'image':
        return nemoa.model.exports.image.save(
            model, path, filetype, **kwargs)

    return False

def show(model, *args, **kwargs):
    return nemoa.model.exports.image.show(model, *args, **kwargs)
