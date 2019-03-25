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

import nemoa.system.classes
import nemoa.system.commons
import nemoa.system.imports
import nemoa.system.exports

def copy(system, *args, **kwds):
    """Create copy of system instance."""
    return new(**system.get('copy'))

def load(*args, **kwds):
    """Import system dictionary from file."""
    return nemoa.system.imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create system instance from system dictionary."""
    return nemoa.system.classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import system instance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export system instance to file."""
    return nemoa.system.exports.save(*args, **kwds)
