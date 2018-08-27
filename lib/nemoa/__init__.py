# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for grafical modeling, deep data analysis
and data visualization. By utilizing deep structured probabilistic graphical
models, graphical and statistical methods are used to uncover structures
within complex and natural data samples.

"""

__version__     = '0.5.71'
__status__      = 'Development'
__description__ = 'Network-based Modeling and deep Data Analysis'
__url__         = 'https://fishroot.github.io/nemoa'
__license__     = 'GPLv3'
__copyright__   = 'Copyright 2013-2018, Patrick Michl'
__author__      = 'Patrick Michl'
__email__       = 'patrick.michl@gmail.com'
__maintainer__  = 'Patrick Michl'
__credits__     = ['Willi Jäger', 'Rainer König']

import nemoa.common
import nemoa.dataset
import nemoa.model
import nemoa.network
import nemoa.session
import nemoa.system
import nemoa.workspace

def about(*args, **kwargs):
    """Get meta information about current instance."""
    return get('about', *args, **kwargs)

def close(*args, **kwargs):
    """Close current workspace instance."""
    return set('workspace', None)

def create(*args, **kwargs):
    """Create new object instance from building script."""
    return nemoa.session.create(*args, **kwargs)

def get(*args, **kwargs):
    """Get value from configuration instance."""
    return nemoa.session.get(*args, **kwargs)

def list(*args, **kwargs):
    """Return list of given objects."""
    return get('list', *args, **kwargs)

def log(*args, **kwargs):
    """Log errors, warnings, notes etc. to console and logfiles."""
    return nemoa.session.log(*args, **kwargs)

def open(*args, **kwargs):
    """Open object instance in current session."""
    return nemoa.session.open(*args, **kwargs)

def path(*args, **kwargs):
    """Get path to given object type or object."""
    return get('path', *args, **kwargs)

def run(*args, **kwargs):
    """Run nemoa python script in current session."""
    return nemoa.session.run(*args, **kwargs)

def set(*args, **kwargs):
    """Set value in configuration instance."""
    return nemoa.session.set(*args, **kwargs)
