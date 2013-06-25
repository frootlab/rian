# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """
    return new dataset instance
    """
    import metapath.dataset.base
    return metapath.dataset.base.dataset(*args, **kwargs)

def empty():
    """
    return new empty dataset instance
    """
    import metapath.dataset.base
    return metapath.dataset.base.dataset()
