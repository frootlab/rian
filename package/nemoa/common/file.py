# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def get_file_directory(path):
    """Get directory path of file.

    Args:
        path (string): path to file

    Returns:
        String containing normalized directory path of file.

    """

    file_path = os.path.expanduser(path)
    file_path = os.path.expandvars(file_path)
    file_path = os.path.abspath(file_path)
    file_path = os.path.normpath(file_path)
    file_directory = os.path.dirname(file_path)
    return file_directory

def get_file_name(path):
    """Get name of file.

    Args:
        path (string): path to file

    Returns:
        String containing name of file.

    """

    return os.path.basename(path)

def get_file_basename(path):
    """Get basename of file.

    Args:
        path (string): path to file

    Returns:
        String containing basename of file.

    """

    file_name = os.path.basename(path)
    file_basename = os.path.splitext(file_name)[0].rstrip('.')
    return file_basename

def get_file_extension(path):
    """Get extension of file.

    Args:
        path (string): path to file

    Returns:
        String containing extension of file.

    """

    file_name = os.path.basename(path)
    file_ext = os.path.splitext(file_name)[1].lstrip('.')
    return file_ext

def get_current_directory():
    """Get path of current working derctory.

    Returns:
        String containing path of current working directory.

    """
    return os.getcwd() + os.sep

def get_unused_file_path(path):
    """Get unused file path for given file path.

    Args:
        path (string): path to file

    Returns:
        String containing new file path.

    """

    # get basepath and create directory if not available
    file_basepath = get_file_directory(path)
    if not os.path.exists(file_basepath):
        nemoa.log("creating directory '%s'." % (file_basepath))
        os.makedirs(file_basepath)

    # search for unused filename
    file_directory = get_file_directory(path)
    file_basename = get_file_basename(path)
    file_extension = get_file_extension(path)
    file_base = os.path.join(file_directory, file_basename)
    path = '%s.%s' % (file_base, file_extension)
    file_id = 1
    while os.path.exists(path):
        file_id += 1
        path = '%s (%s).%s' % (file_base, file_id, file_extension)

    return path
