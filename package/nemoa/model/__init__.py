#!/usr/bin/env python
# -*- coding: utf-8 -*-

def new(*args, **kwargs):
    """Return new model instance."""
    import nemoa.model.base
    return nemoa.model.base.model(*args, **kwargs)

def empty(*args, **kwargs):
    """Return empty model instance."""
    import nemoa.model.base
    return nemoa.model.base.empty(*args, **kwargs)
