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

def build(*args, **kwds):
    """Create network dictionary from building script."""
    from nemoa.network import builder
    return builder.build(*args, **kwds)

def copy(network, *args, **kwds):
    """Create copy of network instance."""
    return new(**network.get('copy'))

def create(*args, **kwds):
    """Create network instance from building script."""
    return new(**build(*args, **kwds))

def load(*args, **kwds):
    """Import network dictionary from file."""
    from nemoa.network import imports
    return imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create network instance from network dictionary."""
    from nemoa.network import classes
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import network intance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export network intance to file."""
    from nemoa.network import exports
    return exports.save(*args, **kwds)

def show(*args, **kwds):
    """Show network as image."""
    from nemoa.network import exports
    return exports.show(*args, **kwds)
