# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from nemoa.dataset.builder import plain

def types(type = None):
    """Get supported dataset types of dataset builders."""

    alltypes = {}

    # get supported plain datasets
    types = plain.types()
    for key, val in list(types.items()): alltypes[key] = ('plain', val)

    if type is None:
        return {key: val[1] for key, val in list(alltypes.items())}
    if type in alltypes:
        return alltypes[type]

    return None

def build(type, *args, **kwds):
    """Build dataset from building parameters."""

    # test if type is supported
    if type not in types():
        raise ValueError(f"type '{type}' is not supported")

    module_name = types(type)[0]

    if module_name == 'plain':
        dataset = plain.build(type, *args, **kwds)

    return dataset or {}
