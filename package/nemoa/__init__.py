#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.log import *
import nemoa.common.type as type
import nemoa.workspace.config, nemoa.plot, nemoa.annotation

__version = ('0.4.81', 'noGPU-20140818')
initLogger()

def new(**kwargs):
    """Return new workspace instance."""
    return nemoa.workspace.new(**kwargs)

def open(workspace, **kwargs):
    """Open and return workspace instance."""
    return nemoa.workspace.open(workspace, **kwargs)

def welcome():
    """Print welcome message to standard output."""
    return log('header', 'nemoa ' + __version[0])

def version():
    """Return version number and identifier string as tuple."""
    return __version

def workspaces():
    """Return list of workspaces."""
    return nemoa.workspace.config.config().listWorkspaces()
