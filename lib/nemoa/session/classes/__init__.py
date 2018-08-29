# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def new(*args, **kwargs):
    """Create new session instance."""

    # validate configuration
    if not kwargs: kwargs = {'config': {'type': 'base.Session'}}
    elif len(kwargs.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid")


    mname, cname = tuple(kwargs['config']['type'].split('.'))
    try:
        from nemoa.common import module
        minst = module.get_submodule(mname)
        if not hasattr(minst, cname): raise ImportError()
        cinst = getattr(minst, cname)(**kwargs)
    except ImportError as e: raise ValueError(
        f"session type '{mname}.{cname}' is not valid") from e

    return cinst
