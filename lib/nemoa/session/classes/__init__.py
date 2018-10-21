# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def new(*args, **kwds):
    """Create new session instance."""
    # validate configuration
    if not kwds:
        kwds = {'config': {'type': 'base.Session'}}
    elif len(kwds.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid")

    mname, cname = tuple(kwds['config']['type'].split('.'))

    from nemoa.base import nmodule

    module = nmodule.get_submodule(mname)
    if not hasattr(module, cname):
        raise NameError(f"class '{mname}.{cname}' is not known")
    cinst = getattr(module, cname)(**kwds)

    return cinst
