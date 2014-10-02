# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def get_empty_file(file):
    """return file path for new file."""
    fDir = get_file_path(file)

    # create directory if not available
    if not os.path.exists(fDir):
        nemoa.log('creating directory \'%s\'' % (fDir))
        os.makedirs(fDir)

    # search unused filename
    fName = get_file_name(file)
    fBaseName, fExt = os.path.splitext(fName)
    fBase = '%s/%s' % (fDir, fBaseName)
    file = fBase + fExt
    fID  = 1
    while os.path.exists(file):
        fID += 1
        file = '%s (%s)%s' % (fBase, fID, fExt)

    return file

def get_file_name(file):
    """return file name from given file path as string."""
    return os.path.basename(file)

def get_file_ext(file):
    """return file extension from given file path as string."""
    fileName = os.path.basename(file)
    fileExt  = os.path.splitext(fileName)[1].lstrip('.')
    return fileExt

def get_file_path(file):
    """return normalized filepath from given file path as string."""
    filePath = os.path.expanduser(file)
    filePath = os.path.expandvars(filePath)
    filePath = os.path.abspath(filePath)
    filePath = os.path.normpath(filePath)
    return os.path.dirname(filePath)

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

def get_subdir_from_hash(basepath, str):

    # create path if not available
    if not os.path.exists(basepath): os.makedirs(basepath)

    # create new subfolder
    subDir = '%s%s/' % (basepath, str_to_hash(str))
    if not os.path.exists(subDir): os.makedirs(subDir)
    return os.path.abspath(subDir) + '/'
