# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from nemoa.network.imports import archive, graph, text

def filetypes(filetype = None):
    """Get supported network import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported graph description filetypes
    graph_types = graph.filetypes()
    for key, val in list(graph_types.items()):
        type_dict[key] = ('graph', val)

    # get supported text filetypes
    text_types = text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwds):
    """Import network dictionary from file or workspace."""

    import os
    from flab.base import env
    import nemoa

    # get path (if necessary)
    if 'workspace' in kwds or not os.path.isfile(path):
        name = path
        pathkwds = {}
        if 'workspace' in kwds:
            pathkwds['workspace'] = kwds.pop('workspace')
        if 'base' in kwds:
            pathkwds['base'] = kwds.pop('base')
        path = nemoa.path('network', name, **pathkwds)
        if not path:
            raise Warning("""could not import network:
                invalid network name.""") or {}
        if not os.path.isfile(path):
            raise Warning("""could not import network:
                file '%s' does not exist.""" % path) or {}

    # get filetype (from file extension if not given)
    # and check if filetype is supported
    if not filetype: filetype = env.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # import, check and update dictionary
    mname = filetypes(filetype)[0]
    if mname == 'archive':
        network = archive.load(path, **kwds)
    elif mname == 'graph':
        network = graph.load(path, **kwds)
    elif mname == 'text':
        network = text.load(path, **kwds)
    else:
        network = None
    if not network:
        raise ValueError("""could not import network:
            file '%s' is not valid.""" % path) or {}

    # update path
    network['config']['path'] = path

    return network
