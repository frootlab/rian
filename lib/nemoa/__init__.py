# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for graphical modeling, deep data analysis
and data visualization. By utilizing deep structured models, statistical
geometrical and topological methods are used to uncover complex dependency
structures within natural data samples.

"""
__version__ = '0.5.178'
__status__ = 'Development'
__description__ = 'Network-based Modeling and Data Analysis'
__url__ = 'https://frootlab.github.io/nemoa'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013-2018, Patrick Michl'
__organization__ = 'frootlab'
__email__ = 'frootlab@gmail.com'
__maintainer__ = 'Patrick Michl'
__author__ = 'Patrick Michl'
__authors__ = [
    'Patrick Michl <patrick.michl@gmail.com>']
__credits__ = [
    'Willi Jäger', 'Rainer König']

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
