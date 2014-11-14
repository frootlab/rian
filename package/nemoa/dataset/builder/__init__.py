# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.builder.plain

def types(type = None):
    """Get supported dataset types of dataset builders."""

    alltypes = {}

    # get supported plain datasets
    types = nemoa.dataset.builder.plain.types()
    for key, val in types.items(): alltypes[key] = ('plain', val)

    if type == None:
        return {key: val[1] for key, val in alltypes.items()}
    if type in alltypes:
        return alltypes[type]

    return None

def build(type, *args, **kwargs):
    """Build dataset from building parameters."""

    # test if type is supported
    if not type in types().keys():
        nemoa.log('error', """could not create dataset:
            type '%s' is not supported.""" % (type))
        return {}

    module_name = types(type)[0]

    if module_name == 'plain':
        dataset = nemoa.dataset.builder.plain.build(
            type, *args, **kwargs)

    if not dataset: return {}

    # update path
    basepath = nemoa.workspace.path('datasets')
    if not basepath: basepath = nemoa.common.get_current_directory()
    dataset['config']['path'] = \
        basepath + dataset['config']['name'] + '.csv'

    return dataset
