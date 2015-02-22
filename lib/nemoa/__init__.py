# -*- coding: utf-8 -*-
"""nemoa deep data analysis and visualization.

Nemoa is a python package for network model based deep data analysis
and visualization. By utilizing deep artificial neural networks,
combinatorial and statistical methods are used to uncover hidden
dependency structures in complex data as graphical presentations
or statistical values.

"""

__version__     = '0.4.270'
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
                   'Sebastian Michl']

import nemoa.common
import nemoa.dataset
import nemoa.model
import nemoa.network
import nemoa.system
import nemoa.workspace

_shared = {}

def get(*args, **kwargs):
    """Return information about given object."""
    if not 'config' in _shared:
        _shared['config'] = nemoa.common.classes.Config()
    return _shared['config'].get(*args, **kwargs)

def list(*args, **kwargs):
    """Return list of given objects."""
    if not 'config' in _shared:
        _shared['config'] = nemoa.common.classes.Config()
    return _shared['config'].list(*args, **kwargs)

def load(*args, **kwargs):
    """Import workspace configuration."""
    if not 'config' in _shared:
        _shared['config'] = nemoa.common.classes.Config()
    return _shared['config'].load(*args, **kwargs)

def log(*args, **kwargs):
    """Log errors, warnings, notes etc. to console and logfiles."""
    return nemoa.common.log.log(*args, **kwargs)

def new(**kwargs):
    """Return new workspace instance."""
    return nemoa.workspace.new(**kwargs)

def open(workspace, **kwargs):
    """Open and return workspace instance."""
    return nemoa.workspace.open(workspace, **kwargs)

def path(*args, **kwargs):
    """Return path to given object."""
    if not 'config' in _shared:
        _shared['config'] = nemoa.common.classes.Config()
    return _shared['config'].path(*args, **kwargs)

def version():
    """Return version as string."""
    return __version__

def workspaces():
    """Return list of workspaces."""
    return list(type = 'workspace')
