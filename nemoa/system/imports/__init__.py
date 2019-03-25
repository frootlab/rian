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

import nemoa.system.imports.archive
import nemoa.system.imports.text

def filetypes(filetype = None):
    """Get supported system import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.system.imports.archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported text filetypes
    text_types = nemoa.system.imports.text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwds):
    """Import system dictionary from file or workspace."""

    import os
    from flib.base import env

    # get path (if necessary)
    if 'workspace' in kwds or not os.path.isfile(path):
        name = path
        pathkwds = {}
        if 'workspace' in kwds:
            pathkwds['workspace'] = kwds.pop('workspace')
        if 'base' in kwds:
            pathkwds['base'] = kwds.pop('base')
        path = nemoa.path('system', name, **pathkwds)
        if not path:
            raise Warning("""could not import system:
                invalid system name.""") or {}
        if not os.path.isfile(path):
            raise Warning("""could not import system:
                file '%s' does not exist.""" % path) or {}

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype:
        filetype = env.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError("""could not import system:
            filetype '%s' is not supported.""" % filetype)

    # import and check dictionary
    mname = filetypes(filetype)[0]
    if mname == 'archive':
        system = nemoa.system.imports.archive.load(path, **kwds)
    elif mname == 'text':
        system = nemoa.system.imports.text.load(path, **kwds)
    else:
        system = None
    if not system:
        raise ValueError("""could not import system:
            file '%s' is not valid.""" % path) or {}

    # update path
    system['config']['path'] = path

    return system
