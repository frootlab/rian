# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Frootlab Developers
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Nemoa data analysis.

Nemoa is a data analysis framework for collaborative data science and enterprise
application. Nemoa is open source and based on the Python programming language.
Nemoa utilizes methods from probabilistic graphical modeling [PGM]_, machine
learning [ML]_ and structured data-analysis [SDA]_.

"""
__version__ = '0.5.578'
__status__ = 'Development'
__description__ = 'enterprise data analysis'
__url__ = 'https://frootlab.github.io/nemoa'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (c) 2013-2019 Frootlab Developers'
__organization__ = 'frootlab'
__author__ = 'frootlab'
__email__ = 'frootlab@gmail.com'
__maintainer__ = 'Patrick Michl'
__authors__ = ['Patrick Michl <patrick.michl@gmail.com>']
__credits__ = ['Willi Jäger']
__docformat__ = 'google'

from nemoa import session

def about(*args, **kwds):
    """Get meta information about current instance."""
    return get('about', *args, **kwds)

def close():
    """Close current workspace instance."""
    return set('workspace', None)

def get(*args, **kwds):
    """Get value from configuration instance."""
    return session.get(*args, **kwds)

def list(*args, **kwds):
    """Return list of given objects."""
    return get('list', *args, **kwds)

def log(*args, **kwds):
    """Log errors, warnings, notes etc. to console and logfiles."""
    return session.log(*args, **kwds)

def open(*args, **kwds):
    """Open object instance in current session."""
    return session.open(*args, **kwds)

def path(*args, **kwds):
    """Get path to given object type or object."""
    return session.path(*args, **kwds)

def run(*args, **kwds):
    """Run nemoa python script in current session."""
    return session.run(*args, **kwds)

def set(*args, **kwds):
    """Set value in configuration instance."""
    return session.set(*args, **kwds)
