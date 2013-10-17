# -*- coding: utf-8 -*-

def new():
    """
    Return new workspace instance.
    """
    import metapath.workspace.workspace as workspace
    return workspace.workspace()

def open(project, quiet = False):
    """
    Return workspace instance from file(s).
    """
    import metapath.workspace.workspace as workspace
    return workspace.workspace(project)
