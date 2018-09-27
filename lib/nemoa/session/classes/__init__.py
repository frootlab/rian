# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def new(*args, **kwargs):
    """Create new session instance."""
    # validate configuration
    if not kwargs:
        kwargs = {'config': {'type': 'base.Session'}}
    elif len(kwargs.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid")

    mname, cname = tuple(kwargs['config']['type'].split('.'))

    from nemoa.common import nmodule

    module = nmodule.getsubmodule(mname)
    if not hasattr(module, cname):
        raise NameError(f"class '{mname}.{cname}' is not known")
    cinst = getattr(module, cname)(**kwargs)

    return cinst
