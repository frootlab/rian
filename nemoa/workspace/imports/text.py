# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import env
from flab.io import ini

def filetypes():
    """Get supported text filetypes for workspace import."""
    return {
        'ini': 'Nemoa Workspace Description' }

def load(path, **kwds):
    """Import workspace from text file."""

    # extract filetype from path
    filetype = env.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError("""could not import graph:
            filetype '%s' is not supported.""" % filetype)

    if filetype == 'ini':
        return Ini(**kwds).load(path)

    return False

class Ini:
    """Import workspace configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def load(self, path):
        """Return workspace configuration as dictionary.

        Args:
            path: configuration file used to generate workspace
                configuration dictionary.

        """
        scheme = {
            'workspace': {
                'description': str,
                'maintainer': str,
                'email': str,
                'startup_script': str},
            'folders': {
                'datasets': str,
                'networks': str,
                'systems': str,
                'models': str,
                'scripts': str}}

        config = ini.load(path, scheme=scheme)
        config['type'] = 'base.Workspace'

        return {'config': config}
