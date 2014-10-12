# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def get_empty_file(path):
    """Get file path for new file."""
    file_path = get_file_path(path)

    # create directory if not available
    if not os.path.exists(file_path):
        nemoa.log("creating directory '%s'" % (file_path))
        os.makedirs(file_path)

    # search unused filename
    file_name = get_file_name(path)
    file_basename, file_ext = os.path.splitext(file_name)
    file_base = '%s/%s' % (file_path, file_basename)
    path = file_base + file_ext
    file_id = 1
    while os.path.exists(path):
        file_id += 1
        path = '%s (%s)%s' % (file_base, file_id, file_ext)

    return path

def get_file_path(path):
    """Get filepath.

    Args:
        path (string): path to file

    Returns:
        String containing normalized file path.

    """

    file_path = os.path.expanduser(path)
    file_path = os.path.expandvars(file_path)
    file_path = os.path.abspath(file_path)
    file_path = os.path.normpath(file_path)
    return os.path.dirname(file_path)

def get_file_name(path):
    """Get filename.

    Args:
        path (string): path to file

    Returns:
        String containing filename.

    """

    return os.path.basename(path)

def get_file_ext(path):
    """Get file extension.

    Args:
        path (string): path to file

    Returns:
        String containing file extension.

    """

    file_name = get_file_name(path)
    file_ext = os.path.splitext(file_name)[-1].lstrip('.')
    return file_ext

def get_file_basename(path):
    """Get file basename.

    Args:
        path (string): path to file

    Returns:
        String containing file basename.

    """

    file_name = get_file_name(path)
    file_ext = get_file_ext(path)
    file_basename_length = len(file_name) - len(file_ext)
    return file_name[:file_basename_length - 1]

def get_empty_subdir(basepath, subdir = None):

    # create path if not available
    if not os.path.exists(basepath): os.makedirs(basepath)

    #
    if folder: pre = basepath + folder + '_'
    else: pre = basepath

    # search for unused subfolder, starting with 1
    i = 1
    while os.path.exists('%s%s/' % (pre, i)): i += 1

    # create new subdirectory
    new = '%s%s/' % (pre, i)
    os.makedirs(new)

    return os.path.abspath(new) + '/'

def get_subdir_from_hash(basepath, string):

    # create path if not available
    if not os.path.exists(basepath): os.makedirs(basepath)

    # create new subfolder
    sub_dir = '%s%s/' % (basepath, str_to_hash(string))
    if not os.path.exists(sub_dir): os.makedirs(sub_dir)
    return os.path.abspath(sub_dir) + '/'
