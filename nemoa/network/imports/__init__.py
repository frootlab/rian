# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

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
    from flib.base import env
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
