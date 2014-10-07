# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa
import os

def open(path, file_format = None, **kwargs):
    """Import dataset configuration from file."""

    if not os.path.isfile(path):
        return nemoa.log('error', """could not import dataset:
            file does not exist '%s'.""" % (path))

    # if format is not given get format from file extension
    if not file_format:
        file_name = os.path.basename(path)
        file_ext = os.path.splitext(file_name)[1]
        file_format = file_ext.lstrip('.').strip().lower()

    # get network file importer
    module_name = 'nemoa.dataset.fileimport.%s' % (file_format)
    class_name = file_format.title()
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        importer = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not import dataset '%s':
            file format '%s' is currently not supported.""" %
            (path, file_format))

    # import dataset file
    return importer.load(path)
