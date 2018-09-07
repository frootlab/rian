# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.imports.archive
import nemoa.system.imports.text

def filetypes(filetype = None):
    """Get supported system import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.system.imports.archive.filetypes()
    for key, val in list(archive_types.items()):
        type_dict[key] = ('archive', val)

    # get supported text filetypes
    text_types = nemoa.system.imports.text.filetypes()
    for key, val in list(text_types.items()):
        type_dict[key] = ('text', val)

    if filetype is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwargs):
    """Import system dictionary from file or workspace."""

    import os
    from nemoa.common import npath

    # get path (if necessary)
    if 'workspace' in kwargs or not os.path.isfile(path):
        name = path
        pathkwargs = {}
        if 'workspace' in kwargs:
            pathkwargs['workspace'] = kwargs.pop('workspace')
        if 'base' in kwargs:
            pathkwargs['base'] = kwargs.pop('base')
        path = nemoa.path('system', name, **pathkwargs)
        if not path:
            raise Warning("""could not import system:
                invalid system name.""") or {}
        if not os.path.isfile(path):
            raise Warning("""could not import system:
                file '%s' does not exist.""" % path) or {}

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype:
        filetype = npath.fileext(path).lower()
    if filetype not in filetypes():
        raise ValueError("""could not import system:
            filetype '%s' is not supported.""" % filetype)

    # import and check dictionary
    mname = filetypes(filetype)[0]
    if mname == 'archive':
        system = nemoa.system.imports.archive.load(path, **kwargs)
    elif mname == 'text':
        system = nemoa.system.imports.text.load(path, **kwargs)
    else:
        system = None
    if not system:
        raise ValueError("""could not import system:
            file '%s' is not valid.""" % path) or {}

    # update path
    system['config']['path'] = path

    return system
