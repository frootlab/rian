# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.workspace.imports.text

def filetypes(filetype = None):
    """Get supported workspace import filetypes."""

    type_dict = {}

    # get supported text filetypes
    text_types = nemoa.workspace.imports.text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(arg, base = None, filetype = None, **kwds):
    """Import workspace dictionary from file or workspace."""

    import os
    from flab.base import env

    if os.path.isfile(arg):
        path = arg
        workspace = os.path.basename(os.path.dirname(path))
        base = None # 2Do: get base and workspace from path
    else:
        path = nemoa.path('ini', workspace=arg, base=base)
        if not path:
            return None
        else: workspace = arg

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype: filetype = env.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError("""could not import workspace:
            filetype '%s' is not supported.""" % filetype)

    # import and check dictionary
    mname = filetypes(filetype)[0]
    if mname == 'text':
        config = nemoa.workspace.imports.text.load(path, **kwds)
    else:
        config = None
    if not config:
        raise ValueError("""could not import workspace:
            file '%s' is not valid.""" % path) or {}

    # update path
    config['config']['path'] = path
    config['config']['name'] = workspace
    config['config']['base'] = base

    return config
