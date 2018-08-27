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

    # extract filetype from path
    filetype = nemoa.common.ospath.fileext(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import graph:
            filetype '%s' is not supported.""" % filetype)

    if filetype == 'ini':
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import workspace configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

    def load(self, path):
        """Return workspace configuration as dictionary.

        Args:
            path: configuration file used to generate workspace
                configuration dictionary.

        """

        from nemoa.common import ioini

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

        config = ioini.load(path, structure)
        config['type'] = 'base.Workspace'

        return { 'config': config }
