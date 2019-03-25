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

from flib.base import env
from flib.io import ini

def filetypes():
    """Get supported text filetypes for workspace import."""
    return {
        'ini': 'Nemoa Workspace Description' }

def load(path, **kwds):
    """Import workspace from text file."""

    # extract filetype from path
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError("""could not import graph:
            filetype '%s' is not supported.""" % filetype)

    if filetype == 'ini':
        return Ini(**kwds).load(path)

    return False

class Ini:
    """Import workspace configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """Return workspace configuration as dictionary.

        Args:
            path: configuration file used to generate workspace
                configuration dictionary.

        """
        scheme = {
            'workspace': {
                'description': str,
                'maintainer': str,
                'email': str,
                'startup_script': str},
            'folders': {
                'datasets': str,
                'networks': str,
                'systems': str,
                'models': str,
                'scripts': str}}

        config = ini.load(path, scheme=scheme)
        config['type'] = 'base.Workspace'

        return {'config': config}
