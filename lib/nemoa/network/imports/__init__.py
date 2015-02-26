# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.network.imports.archive
import nemoa.network.imports.graph
import nemoa.network.imports.text

def filetypes(filetype = None):
    """Get supported network import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.network.imports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported graph description filetypes
    graph_types = nemoa.network.imports.graph.filetypes()
    for key, val in graph_types.items():
        type_dict[key] = ('graph', val)

    # get supported text filetypes
    text_types = nemoa.network.imports.text.filetypes()
    for key, val in text_types.items():
        type_dict[key] = ('text', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwargs):
    """Import network dictionary from file or workspace."""

    import os

    # get path (if necessary)
    if 'workspace' in kwargs or not os.path.isfile(path):
        name = path
        pathkwargs = {}
        if 'workspace' in kwargs:
            pathkwargs['workspace'] = kwargs.pop('workspace')
        if 'base' in kwargs:
            pathkwargs['base'] = kwargs.pop('base')
        path = nemoa.path('network', name, **pathkwargs)
        if not os.path.isfile(path):
            return nemoa.log('error', """could not import network:
                file '%s' does not exist.""" % path) or {}

    # get filetype (from file extension if not given)
    # and check if filetype is supported
    if not filetype:
        filetype = nemoa.common.ospath.fileext(path).lower()
    if not filetype in filetypes():
        return nemoa.log('error', """could not import network:
            filetype '%s' is not supported.""" % filetype)

    # import, check and update dictionary
    mname = filetypes(filetype)[0]
    if mname == 'archive':
        network = nemoa.network.imports.archive.load(path, **kwargs)
    elif mname == 'graph':
        network = nemoa.network.imports.graph.load(path, **kwargs)
    elif mname == 'text':
        network = nemoa.network.imports.text.load(path, **kwargs)
    else:
        network = None
    if not network:
        return nemoa.log('error', """could not import network:
            file '%s' is not valid.""" % path) or {}

    # update path
    network['config']['path'] = path

    return network

