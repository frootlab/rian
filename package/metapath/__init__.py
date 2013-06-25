# -*- coding: utf-8 -*-
import metapath.common as mp

# initialize logger and print welcome message
mp.initLogger()
mp.log("header", "metapath " + mp.version())

def new():
    """
    Return workspace instance.
    """
    import metapath.workspace
    return metapath.workspace.new()

def open(project):
    """
    Return workspace instance.
    """
    import metapath.workspace
    return metapath.workspace.open(project)
