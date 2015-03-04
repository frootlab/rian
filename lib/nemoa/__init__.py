# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for network model based deep data analysis
and visualization. By utilizing deep artificial neural networks,
combinatorial and statistical methods are used to uncover hidden
dependency structures in complex data as graphical presentations
or statistical values.

"""

__version__     = '0.4.281'
__status__      = 'Development'
__description__ = 'Deep data analysis and visualization'
__url__         = 'https://github.com/fishroot/nemoa'
__license__     = 'GPLv3'
__copyright__   = 'Copyright 2013-2015, Patrick Michl'
__author__      = 'Patrick Michl'
__email__       = 'patrick.michl@gmail.com'
__maintainer__  = 'Patrick Michl'
__credits__     = ['Rainer Koenig', 'Marcus Oswald', 'Anna Dieckmann',
                   'Tobias Bauer', 'Alexandra Poos', 'Rebecca Krauss',
                   'Michael Scherer', 'Sebastian Michl']

import nemoa.common
import nemoa.dataset
import nemoa.model
import nemoa.network
import nemoa.session
import nemoa.system
import nemoa.workspace

__session__ = {}

def about(*args, **kwargs):
    """Get meta information."""
    return get('about', *args, **kwargs)

def get(*args, **kwargs):
    """Get value from configuration instance."""
    return config().get(*args, **kwargs)

def list(*args, **kwargs):
    """Return list of given objects."""
    return get('list', *args, **kwargs)

def log(*args, **kwargs):
    """Log errors, warnings, notes etc. to console and logfiles."""
    return config().log(*args, **kwargs)

def open(*args, **kwargs):
    """Open workspace instance from file in search path."""
    return set('workspace', *args, **kwargs)

def path(*args, **kwargs):
    """Return path to given object type or object."""
    return get('path', *args, **kwargs)

def run(*args, **kwargs):
    """Run python script in nemoa."""
    return config().run(*args, **kwargs)

def config():
    """Return session instance."""
    if not 'manager' in __session__:
        __session__['manager'] = nemoa.session.new()
    return __session__['manager']

def set(*args, **kwargs):
    """Set value in configuration instance."""
    return config().set(*args, **kwargs)
