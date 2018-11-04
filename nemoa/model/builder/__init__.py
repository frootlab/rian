# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.builder.base

def types(type = None):
    """Get supported model types of model builders."""

    type_dict = {}

    # get supported base models
    types = nemoa.model.builder.base.types()
    for key, val in list(types.items()): type_dict[key] = ('base', val)

    if type is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if type in type_dict: return type_dict[type]

    return {}

def build(type = 'model', *args, **kwds):
    """Build model from parameters, datasets, etc. ."""

    # test if type is supported
    if type not in types():
        return ValueError(f"type '{type}' is not supported")

    module_name = types(type)[0]

    if module_name == 'base':
         model = nemoa.model.builder.base.build(type, *args, **kwds)

    return model or {}
