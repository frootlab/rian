# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab Developers
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://github.com/frootlab/nemoa
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
"""Global session management using singleton design pattern."""

__copyright__ = '2019 Frootlab Developers'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'frootlab@gmail.com'
__authors__ = ['Patrick Michl <patrick.michl@gmail.com>']

from typing import Any
from nemoa.session import classes

def cur():
    """Get current session instance."""
    if '_cur' not in globals():
        globals()['_cur'] = new()
    return globals()['_cur']

def get(*args: Any, **kwds: Any) -> Any:
    """Get meta information and content from current session."""
    return cur().get(*args, **kwds)

def log(*args, **kwds):
    """Log message in current session."""
    return cur().log(*args, **kwds)

def new(*args, **kwds):
    """Create session instance from session dictionary."""
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Open object in current session."""
    return cur().open(*args, **kwds)

def path(*args: Any, **kwds: Any) -> str:
    """Get path for given object in current session."""
    return cur().path(*args, **kwds)

def run(*args, **kwds):
    """Run script in current session."""
    return cur().run(*args, **kwds)

def set(*args, **kwds):
    """Set configuration parameter and env var in current session."""
    return cur().set(*args, **kwds)
