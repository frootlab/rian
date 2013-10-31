#!/usr/bin/env python
# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """Return new dataset instance."""
    import nemoa.dataset.base
    return nemoa.dataset.base.dataset(*args, **kwargs)

def empty():
    """Return new empty dataset instance."""
    import nemoa.dataset.base
    return nemoa.dataset.base.dataset()
