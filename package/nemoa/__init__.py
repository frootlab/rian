# -*- coding: utf-8 -*-
"""nemoa data analysis and visualization.

Nemoa is a python package for designing and building complex systems of
stacked artificial neural networks. The key goal of this project is to
provide an intuitive framework for designing data transformations which
implement given requirements and also respect local and global
restrictions of the underlying data structure.
"""

__version__ = '0.4.103'
__status__  = 'Development'
__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__credits__ = ['Rainer König']
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013-2014, Patrick Michl'
__maintainer__ = 'Patrick Michl'

from nemoa.common.log import *
import nemoa.common.type as type
import nemoa.workspace
import nemoa.plot
import nemoa.dataset
import nemoa.system
import nemoa.network
import nemoa.model

initLogger()

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

def workspaces():
    """Return list of workspaces."""
    return nemoa.workspace.__config(update = False).list('workspace')
