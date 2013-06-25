# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """
    return new network instance
    """
    import metapath.network.base
    return metapath.network.base.network(*args, **kwargs)

def empty():
    """
    return empty network instance
    """
    import metapath.network.base
    return metapath.network.base.network()
