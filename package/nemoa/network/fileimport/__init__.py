# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa
import os

def load(path, file_format = None, **kwargs):
    """Import network configuration from file."""

    # get path
    if os.path.isfile(path):
        pass
    elif 'workspace' in kwargs:
        # import workspace and get path and file format from workspace
        if not kwargs['workspace'] == nemoa.workspace.name():
            if not nemoa.workspace.load(kwargs['workspace']):
                nemoa.log('error', """could not import network:
                    workspace '%s' does not exist"""
                    % (kwargs['workspace']))
                return  {}
        name = '.'.join([kwargs['workspace'], path])
        config = nemoa.workspace.get('network', name = name)
        if not isinstance(config, dict):
            nemoa.log('error', """could not import network:
                workspace '%s' does not contain network '%s'."""
                % (kwargs['workspace'], path))
            return  {}
        path = config['path']
    else:
        nemoa.log('error', """could not import network:
            file '%s' does not exist.""" % (path))
        return {}

    # if file format is not given get format from file extension
    if not file_format:
        file_name = os.path.basename(path)
        file_ext = os.path.splitext(file_name)[1]
        file_format = file_ext.lstrip('.').strip().lower()

    # get network file importer
    module_name = 'nemoa.network.fileimport.%s' % (file_format)
    class_name = file_format.title()
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        importer = getattr(module, class_name)(**kwargs)
    except ImportError:
        nemoa.log('error', """could not import network '%s':
            file format '%s' is not supported.""" %
            (path, file_format))
        return {}

    # import network file
    return importer.load(path)
