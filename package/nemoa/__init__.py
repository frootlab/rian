#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.__logging import *
import nemoa.common.__type as type
import nemoa.workspace.config

def new(**kwargs):
    """Return workspace instance."""
    # print welcome message
    log('header', 'nemoa %s' % (version()))
    import nemoa.workspace
    return nemoa.workspace.new(**kwargs)

def open(project, **kwargs):
    """Return workspace instance."""
    # print welcome message
    log('header', 'nemoa %s' % (version()))
    import nemoa.workspace
    return nemoa.workspace.open(project, **kwargs)

def version():
    """Return version as string."""
    return '0.4.59noGPU-20131118'

def listProjects():
    """Return list of projects."""
    return nemoa.workspace.config.config().listProjects()

# initialize logger
initLogger()
