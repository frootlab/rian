# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.builder.base

def types(type = None):
    """Get supported model types of model builders."""

    type_dict = {}

    # get supported base models
    types = nemoa.model.builder.base.types()
    for key, val in types.items():
        type_dict[key] = ('base', val)

    if type == None:
        return {key: val[1] for key, val in type_dict.items()}
    if type in type_dict:
        return type_dict[type]

    return None

def build(type = 'model', *args, **kwargs):
    """Build model from parameters, datasets, etc. ."""

    # test if type is supported
    if not type in types().keys():
        nemoa.log('error', """could not build model:
            type '%s' is not supported.""" % (type))
        return {}

    module_name = types(type)[0]

    if module_name == 'base':
         model = nemoa.model.builder.base.build(type, *args, **kwargs)

    if not model: return {}

    # update path
    basepath = nemoa.path('models')
    if not basepath: basepath = nemoa.common.ospath.getcwd()
    model['config']['path'] = \
        basepath + model['config']['name'] + '.npz'

    return model

