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
    base = 'user', **kwargs):
    """Export model to file.

    Args:
        model (object): nemoa model instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.ismodel(model):
        return nemoa.log('error', """could not export model to file:
            model is not valid.""")

    # get directory, filename and fileextension
    if isinstance(workspace, basestring) and not workspace == 'None':
        directory = nemoa.workspace.path('models',
            workspace = workspace, base = base)
    elif isinstance(path, basestring):
        directory = nemoa.common.ospath.directory(path)
    else:
        directory = nemoa.common.ospath.directory(model.path)
    if isinstance(path, basestring):
        name = nemoa.common.ospath.basename(path)
    else:
        name = model.fullname
    if isinstance(filetype, basestring):
        fileext = filetype
    elif isinstance(path, basestring):
        fileext = nemoa.common.ospath.fileext(path)
        if not fileext:
            fileext = nemoa.common.ospath.fileext(model.path)
    else:
        fileext = nemoa.common.ospath.fileext(model.path)
    path = nemoa.common.ospath.joinpath(directory, name, fileext)

    # get filetype from file extension if not given
    # and test if filetype is supported
    if not filetype: filetype = fileext.lower()
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not export model:
            filetype '%s' is not supported.""" % (filetype))

    # export to file
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
