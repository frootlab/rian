# -*- coding: utf-8 -*-
"""Nemoa deep data-analysis and visualization.

Nemoa is a python package to uncover complex dependency structures within
natural data. For this purpose the package connects ``probabilistic graphical
modeling``_ with ``structured data-analysis``_ and data visualization.

.. _probabilistic graphical modeling:
    https://en.wikipedia.org/wiki/Graphical_model
.. _structured data-analysis:
    https://en.wikipedia.org/wiki/Structured_data_analysis_(statistics)

"""
__version__ = '0.5.233'
__status__ = 'Development'
__description__ = 'Network-based Modeling and Data Analysis'
__url__ = 'https://frootlab.github.io/nemoa'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013-2018, Patrick Michl'
__organization__ = 'frootlab'
__author__ = 'frootlab'
__email__ = 'frootlab@gmail.com'
__maintainer__ = 'Patrick Michl'
__authors__ = ['Patrick Michl <patrick.michl@gmail.com>']
__credits__ = ['Willi Jäger', 'Rainer König']

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
