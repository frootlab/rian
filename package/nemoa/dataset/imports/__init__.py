# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.imports.archive
import nemoa.dataset.imports.text
import os

def filetypes(filetype = None):
    """Get supported dataset import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.dataset.imports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    # get supported text filetypes
    text_types = nemoa.dataset.imports.text.filetypes()
    for key, val in text_types.items():
        type_dict[key] = ('text', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, **kwargs):
    """Import dataset from file."""

    # get path
    if not os.path.isfile(path) and 'workspace' in kwargs:
        # import workspace and get path and filetype from workspace
        if not kwargs['workspace'] == nemoa.workspace.name():
            if not nemoa.workspace.load(kwargs['workspace']):
                nemoa.log('error', """could not import dataset:
                    workspace '%s' does not exist"""
                    % (kwargs['workspace']))
                return  {}
        name = '.'.join([kwargs['workspace'], path])
        config = nemoa.workspace.get('dataset', name = name)
        if not isinstance(config, dict):
            nemoa.log('error', """could not import dataset:
                workspace '%s' does not contain dataset '%s'."""
                % (kwargs['workspace'], path))
            return  {}
        path = config['path']
    else:
        nemoa.log('error', """could not import dataset:
            file '%s' does not exist.""" % (path))
        return {}

    # if filetype is not given get filtype from file extension
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not import dataset:
            filetype '%s' is not supported.""" % (filetype))

    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        dataset_dict = nemoa.dataset.imports.archive.load(
            path, **kwargs)
    elif module_name == 'text':
        dataset_dict = nemoa.dataset.imports.text.load(
            path, **kwargs)
    else:
        return False

    # test dataset dictionary
    if not dataset_dict:
        nemoa.log('error', """could not import dataset:
            file '%s' is not valid.""" % (path))
        return {}

    # update source
    dataset_dict['config']['path'] = path

    # TODO: old
    if not 'source' in dataset_dict['config']:
        dataset_dict['config']['source'] = {}
    dataset_dict['config']['source']['file'] = path
    dataset_dict['config']['source']['filetype'] = filetype

    return dataset_dict
