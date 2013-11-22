#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.log import *
import nemoa.common.type as type
import nemoa.workspace.config
import nemoa.plot

def new(**kwargs):
    """Return workspace instance."""
    log('header', 'nemoa %s' % (version()))
    return nemoa.workspace.new(**kwargs)

def open(project, **kwargs):
    """Return workspace instance."""
    log('header', 'nemoa %s' % (version()))
    return nemoa.workspace.open(project, **kwargs)

def version():
    """Return version as string."""
    return '0.4.60noGPU-20131122'

def listProjects():
    """Return list of projects."""
    return nemoa.workspace.config.config().listProjects()

initLogger()
