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

import nemoa.workspace.imports.text

def filetypes(filetype = None):
    """Get supported workspace import filetypes."""

    type_dict = {}

    # get supported text filetypes
    text_types = nemoa.workspace.imports.text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(arg, base = None, filetype = None, **kwds):
    """Import workspace dictionary from file or workspace."""

    import os
    from flib.base import env

    if os.path.isfile(arg):
        path = arg
        workspace = os.path.basename(os.path.dirname(path))
        base = None # 2Do: get base and workspace from path
    else:
        path = nemoa.path('ini', workspace=arg, base=base)
        if not path:
            return None
        else: workspace = arg

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype: filetype = env.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError("""could not import workspace:
            filetype '%s' is not supported.""" % filetype)

    # import and check dictionary
    mname = filetypes(filetype)[0]
    if mname == 'text':
        config = nemoa.workspace.imports.text.load(path, **kwds)
    else:
        config = None
    if not config:
        raise ValueError("""could not import workspace:
            file '%s' is not valid.""" % path) or {}

    # update path
    config['config']['path'] = path
    config['config']['name'] = workspace
    config['config']['base'] = base

    return config
