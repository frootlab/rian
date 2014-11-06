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

        # import ini file to dictionary, using ini file structure
        # described with regular expressions
        system = nemoa.common.ini_load(path, {
            'system': {
                'name': 'str',
                'type': 'str' },
            'schedule [.0-9a-zA-Z]*': {
                'system [.0-9a-zA-Z]*': 'dict' }})

        if not system \
            or not 'system' in system \
            or not 'type' in system['system']:
            return nemoa.log('error', """could not import system:
                configuration file '%s' is not valid.""" % (path))

        config = system['system'].copy()

        # update / set name
        if not 'name' in config:
            config['name'] = nemoa.common.get_file_basename(path)

        # update / set optimization schedules
        schedules = {}
        for key in system:
            if not key[:8].lower() == 'schedule': continue
            name = key[9:]
            schedules[name] = { 'name': name }
            for syskey in system[key]:
                if not syskey[:6].lower() == 'system': continue
                systype = syskey[7:]
                schedules[name][systype] = system[key][syskey].copy()

        config['schedules'] = schedules

        return { 'config': config }
