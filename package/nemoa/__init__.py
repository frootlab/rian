# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for network model based deep data analysis and
visualization.

"""

__version__ = '0.4.226'
__status__  = 'Development'
__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__credits__ = ['Rainer Koenig', 'Rebecca Krauss', 'Sebastian Michl']
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013-2014, Patrick Michl'
__maintainer__ = 'Patrick Michl'

from nemoa.common.log import *
import nemoa.common.type as type
import nemoa.workspace
import nemoa.model
import nemoa.dataset
import nemoa.network
import nemoa.system

log('init')

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
    return nemoa.workspace.list('workspace')
