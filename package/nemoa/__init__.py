# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for deep data analysis and visualization.
By utilizing deep artificial neural networks, combinatorial and
statistical methods are used to uncover hidden dependency structures
in complex data as graphical presentations or statistical values.

"""

__version__    = '0.4.259'
__status__     = 'Development'
__author__     = 'Patrick Michl'
__email__      = 'patrick.michl@gmail.com'
__license__    = 'GPLv3'
__copyright__  = 'Copyright 2013-2014, Patrick Michl'
__maintainer__ = 'Patrick Michl'
__credits__    = ['Rainer Koenig', 'Marcus Oswald', 'Anna Dieckmann',
                  'Tobias Bauer', 'Alexandra Poos', 'Rebecca Krauss',
                  'Sebastian Michl']

import nemoa.common
import nemoa.dataset
import nemoa.model
import nemoa.network
import nemoa.system
import nemoa.workspace

def log(*args, **kwargs):
    """Log errors, warnings, notes etc. to console and logfiles."""
    return nemoa.common.log.log(*args, **kwargs)

def new(**kwargs):
    """Return new workspace instance."""
    return nemoa.workspace.new(**kwargs)

def open(workspace, **kwargs):
    """Open and return workspace instance."""
    return nemoa.workspace.open(workspace, **kwargs)

def version():
    """Return version as string."""
    return __version__

def welcome():
    """Print welcome message to standard output."""
    return log('header', 'nemoa ' + __version__)

def list():
    """Return list of workspaces."""
    return nemoa.workspace.list('workspace')
