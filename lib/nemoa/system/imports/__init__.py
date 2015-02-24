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
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported text filetypes
    text_types = nemoa.system.imports.text.filetypes()
    for key, val in text_types.items():
        type_dict[key] = ('text', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, workspace = None, base = 'user',
    **kwargs):
    """Import system dictionary from file or workspace."""

    import os

    # get path
    if workspace or not os.path.isfile(path):
        path = nemoa.path('system', path,
            workspace = workspace, base = base)
        if not os.path.isfile(path):
            return nemoa.log('error', """could not import system:
                file '%s' does not exist.""" % path) or {}

    # get filtype from file extension if not given
    # and check if filetype is supported
    if not filetype:
        filetype = nemoa.common.ospath.fileext(path).lower()
    if not filetype in filetypes():
        return nemoa.log('error', """could not import system:
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
        return nemoa.log('error', """could not import system:
            file '%s' is not valid.""" % path) or {}

    # update path
    system['config']['path'] = path

    return system
