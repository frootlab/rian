# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import nemoa
import os

def save(dataset, path, file_format = None, **kwargs):
    """Export dataset to file."""

    if not nemoa.common.type.is_dataset(dataset):
        return nemoa.log('error', """could not save dataset:
            dataset is not valid.""")

    # if format is not given get format from file extension
    if not file_format:
        file_name = os.path.basename(path)
        file_ext = os.path.splitext(file_name)[1]
        file_format = file_ext.lstrip('.').strip().lower()

    # get network file exporter
    module_name = 'nemoa.dataset.fileexport.%s' % (file_format)
    class_name = file_format.title()
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        exporter = getattr(module, class_name)(**kwargs)
    except ImportError:
        return nemoa.log('error', """could not export dataset '%s':
            file format '%s' not supported.""" %
            (dataset.get('name'), file_format))

    # export network file
    return exporter.save(dataset, path)
