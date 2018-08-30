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
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported image filetypes
    image_types = nemoa.model.exports.image.filetypes()
    for key, val in list(image_types.items()):
        type_dict[key] = ('image', val)

    if not filetype:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict: return type_dict[filetype]

    return {}

def save(model, path = None, filetype = None, workspace = None,
    base = 'user', **kwargs):
    """Export model to file.

    Args:
        model (object): nemoa model instance

    Kwargs:
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Return:
        Boolean value which is True if file export was successful

    """

    if not nemoa.common.type.ismodel(model):
        raise ValueError("""could not export model to file:
            model is not valid.""")

    from nemoa.common import ospath

    # get directory, filename and fileextension
    if isinstance(workspace, str) and not workspace == 'None':
        directory = nemoa.path('models', workspace = workspace, base = base)
    elif isinstance(path, str): directory = ospath.dirname(path)
    else: directory = ospath.dirname(model.path)
    if isinstance(path, str): name = ospath.basename(path)
    else:
        name = model.fullname
    if isinstance(filetype, str):
        fileext = filetype
    elif isinstance(path, str):
        fileext = ospath.fileext(path)
        if not fileext: fileext = ospath.fileext(model.path)
    else:
        fileext = ospath.fileext(model.path)
    path = ospath.join(directory, name + '.' + fileext)

    # get filetype from file extension if not given
    # and test if filetype is supported
    if not filetype: filetype = fileext.lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

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
    """ """
    return nemoa.model.exports.image.show(model, *args, **kwargs)
