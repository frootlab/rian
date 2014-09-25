# -*- coding: utf-8 -*-
"""nemoa data analysis and visualization.

Nemoa is a python package for designing and building complex systems of
stacked artificial neural networks. This allows the creation,
transformation and analysis of datasets by using or introducing general
structural assumptions like noise models, sparsity or complexity.

"""

__version__ = '0.4.110'
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
    return nemoa.workspace.__config(update = False).list('workspace')
