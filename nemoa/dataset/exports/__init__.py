# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import otree
from nemoa.dataset.exports import archive, text, image

def filetypes(filetype = None):
    """Get supported dataset export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported image filetypes
    image_types = image.filetypes()
    for key, val in list(image_types.items()):
        type_dict[key] = ('image', val)

    # get supported text filetypes
    text_types = text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if not filetype:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def save(
        dataset, path = None, filetype = None, workspace = None,
        base = 'user', **kwds):
    """Export dataset to file.

    Args:
        dataset (object): nemoa dataset instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    if not otree.has_base(dataset, 'Dataset'):
        raise TypeError("dataset is not valid")

    from flab.base import env
    import nemoa

    # get directory, filename and fileextension
    if isinstance(workspace, str) and not workspace == 'None':
        dname = nemoa.path('datasets', workspace=workspace, base=base)
    elif isinstance(path, str):
        dname = env.get_dirname(path)
    else:
        dname = env.get_dirname(dataset.path)
    if isinstance(path, str):
        fbase = env.basename(path)
    else:
        fbase = dataset.fullname
    if isinstance(filetype, str):
        fext = filetype
    elif isinstance(path, str):
        fext = env.fileext(path) or env.fileext(dataset.path)
    else:
        fext = env.fileext(dataset.path)
    path = str(env.join_path(dname, fbase + '.' + fext))

    # get filetype from file extension if not given
    # and test if filetype is supported
    if not filetype:
        filetype = fext.lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported.")

    # export to file
    mname = filetypes(filetype)[0]
    if mname == 'text':
        return text.save(dataset, path, filetype, **kwds)
    if mname == 'archive':
        return archive.save(dataset, path, filetype, **kwds)
    if mname == 'image':
        return image.save(dataset, path, filetype, **kwds)

    return False

def show(dataset, *args, **kwds):
    return image.show(dataset, *args, **kwds)
