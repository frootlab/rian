# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """
    Return new model instance
    """
    import metapath.model.base
    return metapath.model.base.model(*args, **kwargs)

def empty(*args, **kwargs):
    """
    Return empty model instance
    """
    import metapath.model.base
    return metapath.model.base.empty(*args, **kwargs)
