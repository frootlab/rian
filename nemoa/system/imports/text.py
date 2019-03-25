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

import nemoa
import os

def filetypes():
    """Get supported text filetypes for system import."""
    return {
        'ini': 'Nemoa System Description',
        'txt': 'Nemoa System Description'}

def load(path, **kwds):
    """Import system from text file."""

    from flib.base import env

    # extract filetype from path
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError("""could not import graph:
            filetype '%s' is not supported.""" % (filetype))

    if filetype in ['ini', 'txt']:
        return Ini(**kwds).load(path)

    return False

class Ini:
    """Import system configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """Return system configuration as dictionary.

        Args:
            path: configuration file used to generate system
                configuration dictionary.

        """
        from flib.base import env
        from flib.io import ini

        # import ini file to dictionary, using ini file structure
        # described with regular expressions
        system = ini.load(path, scheme={
            'system': {
                'name': str,
                'type': str},
            'schedule [.0-9a-zA-Z]*': {
                'system [.0-9a-zA-Z]*': dict}})

        if not system \
            or not 'system' in system \
            or not 'type' in system['system']:
            raise ValueError("""could not import system:
                configuration file '%s' is not valid.""" % (path))

        config = system['system'].copy()

        # update / set name
        if 'name' not in config: config['name'] = env.basename(path)

        # update / set optimization schedules
        schedules = {}
        for key in system:
            if key[:8].lower() != 'schedule': continue
            name = key[9:]
            schedules[name] = { 'name': name }
            for syskey in system[key]:
                if syskey[:6].lower() != 'system': continue
                systype = syskey[7:]
                schedules[name][systype] = system[key][syskey].copy()

        config['schedules'] = schedules

        return { 'config': config }
