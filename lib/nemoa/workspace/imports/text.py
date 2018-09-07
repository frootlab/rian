# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for workspace import."""
    return {
        'ini': 'Nemoa Workspace Description' }

def load(path, **kwargs):
    """Import workspace from text file."""

    from nemoa.common import npath

    # extract filetype from path
    filetype = npath.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError("""could not import graph:
            filetype '%s' is not supported.""" % filetype)

    if filetype == 'ini':
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import workspace configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwargs):
        from nemoa.common import ndict
        self.settings = ndict.merge(kwargs, self.default)

    def load(self, path):
        """Return workspace configuration as dictionary.

        Args:
            path: configuration file used to generate workspace
                configuration dictionary.

        """

        from nemoa.common import nini

        structure = {
            'workspace': {
                'description': 'str',
                'maintainer': 'str',
                'email': 'str',
                'startup_script': 'str' },
            'folders': {
                'datasets': 'str',
                'networks': 'str',
                'systems': 'str',
                'models': 'str',
                'scripts': 'str' }}

        config = nini.load(path, structure)
        config['type'] = 'base.Workspace'

        return { 'config': config }
