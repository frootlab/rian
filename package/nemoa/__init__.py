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
    return '0.4.52noGPU-20131031'

# initialize logger
initLogger()

# print welcome message
log('header', 'nemoa %s' % (version()))
