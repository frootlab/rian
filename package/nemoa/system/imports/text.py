# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for system import."""
    return {
        'ini': 'Nemoa System Description',
        'txt': 'Nemoa System Description'}

def load(path, **kwargs):
    """Import system from text file."""

    # extract filetype from path
    filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import graph:
            filetype '%s' is not supported.""" % (filetype))

    if filetype in ['ini', 'txt']:
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import system configuration from ini file."""

    settings = {}

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        """Return system configuration as dictionary.

        Args:
            path: configuration file used to generate system
                configuration dictionary.

        """

        structure = {'system': { 'type': 'str' }}
        system = nemoa.common.ini_load(path, structure)
        if not system \
            or not 'system' in system \
            or not 'type' in system['system']:
            return nemoa.log('error', """could not import system:
                configuration: file '%s' is not valid.""" % (path))

        return nemoa.log('error', """could not import network
            configuration: file '%s' contains unsupported network
            type '%s'.""" % (path, network['network']['type']))
