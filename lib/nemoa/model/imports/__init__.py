# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.imports.archive

def filetypes(filetype = None):
    """Get supported model import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.model.imports.archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwargs):
    """Import model dictionary from file or workspace."""

    import os
    from nemoa.core import npath

    # get path (if necessary)
    if 'workspace' in kwargs or not os.path.isfile(path):

        name = path
        pathkwargs = {}
        if 'workspace' in kwargs:
            pathkwargs['workspace'] = kwargs.pop('workspace')

        if 'base' in kwargs:
            pathkwargs['base'] = kwargs.pop('base')

        path = nemoa.path('model', name, **pathkwargs)
        #path = nemoa.session.get('path', 'model', name, **pathkwargs)

        if not path:
            raise Warning(f"unknown model '{name}'")
        if not os.path.isfile(path):
            raise IOError(f"file '{path}' does not exist")

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype: filetype = npath.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # import and check dictionary
    mname = filetypes(filetype)[0]
    if mname == 'archive':
        model = nemoa.model.imports.archive.load(path, **kwargs)
    else:
        model = None
    if not model:
        raise ValueError(f"file '{path}' is not valid")

    # update path
    model['config']['path'] = path

    return model
