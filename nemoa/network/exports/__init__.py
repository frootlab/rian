# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import otree
import nemoa
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
    base = 'user', **kwds):
    """Export network to file.

    Args:
        network (object): nemoa network instance
        path (str, optional): path of export file
        filetype (str, optional): filetype of export file
        workspace (str, optional): workspace to use for file export

    Returns:
        Boolean value which is True if file export was successful

    """

    from flab.base import env

    if not otree.has_base(network, 'Network'):
        raise ValueError("network is not valid")

    # get directory, filename and fileextension
    if isinstance(workspace, str) and not workspace == 'None':
        directory = nemoa.path('networks', workspace = workspace, base = base)
    elif isinstance(path, str): directory = env.get_dirname(path)
    else: directory = env.get_dirname(network.path)
    if isinstance(path, str): name = env.basename(path)
    else: name = network.fullname
    if isinstance(filetype, str): fileext = filetype
    elif isinstance(path, str):
        fileext = env.fileext(path) or env.fileext(network.path)
    else: fileext = env.fileext(network.path)
    path = str(env.join_path(directory, name + '.' + fileext))

    # get filetype from file extension if not given
    # and test if filetype is supported
    if not filetype: filetype = fileext.lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # export to file
    module_name = filetypes(filetype)[0]
    if module_name == 'graph': return graph.save(
        network, path, filetype, **kwds)
    if module_name == 'archive': return archive.save(
        network, path, filetype, **kwds)
    if module_name == 'image': return image.save(
        network, path, filetype, **kwds)

    return False

def show(network, *args, **kwds):
    """ """
    return image.show(network, *args, **kwds)
