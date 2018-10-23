# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def new(*args, **kwds):
    """Create new network instance."""

    if not 'config' in kwds \
        or not 'type' in kwds['config'] \
        or not len(kwds['config']['type'].split('.')) == 2:
        raise ValueError("""could not create network:
            configuration is not valid.""")

    import importlib

    type = kwds['config']['type']
    module_name = 'nemoa.network.classes.' + type.split('.', 1)[0]
    class_name = type.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        network = getattr(module, class_name)(**kwds)
    except ImportError:
        raise ValueError("""could not create network:
            unknown network type '%s'.""" % (type))

    return network
