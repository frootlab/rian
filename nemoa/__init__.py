# -*- coding: utf-8 -*-
#
# nemoa --- https://frootlab.github.io/nemoa
# Copyright (C) 2013-2019, Patrick Michl
#
# This file is part of nemoa.
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Nemoa deep data-analysis and visualization.

Nemoa is a Python package for `structured data-analysis`_ and based on
`probabilistic graphical modeling`_.

.. _probabilistic graphical modeling:
    https://en.wikipedia.org/wiki/Graphical_model
.. _structured data-analysis:
    https://en.wikipedia.org/wiki/Structured_data_analysis_(statistics)

"""
__version__ = '0.5.414'
__status__ = 'Development'
__description__ = 'Network-based Modeling and Data Analysis'
__url__ = 'https://frootlab.github.io/nemoa'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013-2019, Patrick Michl'
__organization__ = 'frootlab'
__author__ = 'frootlab'
__email__ = 'frootlab@gmail.com'
__maintainer__ = 'Patrick Michl'
__authors__ = ['Patrick Michl <patrick.michl@gmail.com>']
__credits__ = ['Willi Jäger', 'Rainer König']
__docformat__ = 'google'

import nemoa.dataset
import nemoa.model
import nemoa.network
import nemoa.system
import nemoa.workspace
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
