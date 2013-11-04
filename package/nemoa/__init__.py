#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.__logging import *
import nemoa.common.__type as type
import nemoa.workspace.config

def new(**kwargs):
    """Return workspace instance."""
    import nemoa.workspace
    return nemoa.workspace.new(**kwargs)

def open(project, **kwargs):
    """Return workspace instance."""
    import nemoa.workspace
    return nemoa.workspace.open(project, **kwargs)

def version():
    """Return version as string."""
    return '0.4.53noGPU-20131104'

def listProjects():
    """Print list of projects."""
    projects = nemoa.workspace.config.config().listProjects()
    nemoa.log('title', 'scanning for projects')
    nemoa.setLog(indent = '+1')
    for project in projects:
        nemoa.log('info', """
            project: \'%s\'""" % (project))
    nemoa.setLog(indent = '-1')

# initialize logger
initLogger()

# print welcome message
log('header', 'nemoa %s' % (version()))
