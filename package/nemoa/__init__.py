#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.log import *
import nemoa.common.type as type
import nemoa.workspace, nemoa.plot, nemoa.dataset.annotation

__version = ('0.4.91', 'noGPU-20140914')
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
    config = nemoa.workspace.__config(importShared = False)
    return config.list('workspace')
