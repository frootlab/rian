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
    """Create dataset dictionary from building script."""
    from nemoa.dataset import builder
    return builder.build(*args, **kwds)

def copy(dataset, *args, **kwds):
    """Create copy of dataset instance."""
    return new(**dataset.get('copy'))

def create(*args, **kwds):
    """Create dataset instance from building script."""
    return new(**build(*args, **kwds))

def load(*args, **kwds):
    """Import dataset dictionary from file."""
    from nemoa.dataset import imports
    return imports.load(*args, **kwds)

def new(*args, **kwds):
    """Create dataset instance from dataset dictionary."""
    from nemoa.dataset import classes
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Import dataset instance from file."""
    return new(**load(*args, **kwds))

def save(*args, **kwds):
    """Export dataset instance to file."""
    from nemoa.dataset import exports
    return exports.save(*args, **kwds)

def show(*args, **kwds):
    """Show dataset as image."""
    from nemoa.dataset import exports
    return exports.show(*args, **kwds)
