# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import os

def directory(path):
    """Get directory path of file.

    Args:
        path (string): path to file

    Returns:
        String containing normalized directory path of file.

    """

    filepath = os.path.expanduser(path)
    filepath = os.path.expandvars(filepath)
    filepath = os.path.abspath(filepath)
    filepath = os.path.normpath(filepath)

    return os.path.dirname(filepath)

def joinpath(directory, name, extension):
    """Get path of file.

    Args:
        directory (string): file directory
        name (string): file basename
        extension (string): file extension

    Returns:
        String containing path of file.

    """

    path = '%s%s%s.%s' % (directory, os.sep, name, extension)
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)

    return path

def basename(path):
    """Get basename of file.

    Args:
        path (string): path to file

    Returns:
        String containing basename of file.

    """

    filename = os.path.basename(path)
    filebasename = os.path.splitext(filename)[0].rstrip('.')

    return filebasename

def fileext(path):
    """Get extension of file.

    Args:
        path (string): path to file

    Returns:
        String containing extension of file.

    """

    filename = os.path.basename(path)
    file_ext = os.path.splitext(filename)[1].lstrip('.')

    return file_ext

def cwd():
    """Get path of current working derctory.

    Returns:
        String containing path of current working directory.

    """
    return os.getcwd() + os.sep
