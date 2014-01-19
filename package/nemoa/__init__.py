#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common.log import *
import nemoa.common.type as type
import nemoa.workspace.config
import nemoa.plot
import nemoa.annotation

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
    return '0.4.66noGPU-20140119'

def listProjects():
    """Return list of projects."""
    return nemoa.workspace.config.config().listProjects()

initLogger()
