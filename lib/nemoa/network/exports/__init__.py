# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.network.exports import archive, graph, image

def filetypes(filetype = None):
    """Get supported network export filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported graph description file types
    graph_types = graph.filetypes()
    for key, val in list(graph_types.items()):
        type_dict[key] = ('graph', val)

    # get supported image filetypes
    image_types = image.filetypes()
    for key, val in list(image_types.items()):
        type_dict[key] = ('image', val)

    if not filetype:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def save(network, path = None, filetype = None, workspace = None,
    base = 'user', **kwargs):
    """Export network to file.

    Args:
        network (object): nemoa network instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    from nemoa.common import nclass, npath

    if not nclass.hasbase(network, 'Network'):
        raise ValueError("network is not valid")

    # get directory, filename and fileextension
    if isinstance(workspace, str) and not workspace == 'None':
        directory = nemoa.path('networks', workspace = workspace, base = base)
    elif isinstance(path, str): directory = npath.dirname(path)
    else: directory = npath.dirname(network.path)
    if isinstance(path, str): name = npath.basename(path)
    else: name = network.fullname
    if isinstance(filetype, str): fileext = filetype
    elif isinstance(path, str):
        fileext = npath.fileext(path) or npath.fileext(network.path)
    else: fileext = npath.fileext(network.path)
    path = npath.join(directory, name + '.' + fileext)

    # get filetype from file extension if not given
    # and test if filetype is supported
    if not filetype: filetype = fileext.lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # export to file
    module_name = filetypes(filetype)[0]
    if module_name == 'graph': return graph.save(
        network, path, filetype, **kwargs)
    if module_name == 'archive': return archive.save(
        network, path, filetype, **kwargs)
    if module_name == 'image': return image.save(
        network, path, filetype, **kwargs)

    return False

def show(network, *args, **kwargs):
    """ """
    return image.show(network, *args, **kwargs)
