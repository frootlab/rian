# -*- coding: utf-8 -*-
import os

#
# file operations
#

def getEmptyFile(file):
    file_dirname = os.path.dirname(file) + '/'
    file_name = os.path.basename(file)
    file_base_name, file_ext = os.path.splitext(file_name)
    file_base = file_dirname + file_base_name

    # search unused filename
    if os.path.exists(file):
        file_id = 2
        while os.path.exists('%s (%s)%s' % (file_base, file_id, file_ext)):
            file_id += 1
        file = '%s (%s)%s' % (file_base, file_id, file_ext)

    # create path if not available
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))

    return file

def getFileExt(file):
    fileName = os.path.basename(file)
    fileExt  = os.path.splitext(fileName)[1].lstrip('.')
    return fileExt

def getEmptySubdir(basepath, subdir = None):

    # create path if not available
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    #
    if folder:
        pre = basepath + folder + '_'
    else:
        pre = basepath

    # search for unused subfolder, starting with 1
    i = 1
    while os.path.exists('%s%s/' % (pre, i)):
        i += 1

    # create new subdirectory
    new = '%s%s/' % (pre, i)
    os.makedirs(new)

    return os.path.abspath(new) + '/'

def getSubdirFromHash(basepath, str):

    # create path if not available
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    # create new subfolder
    subDir = '%s%s/' % (basepath, strToHash(str))
    if not os.path.exists(subDir):
        os.makedirs(subDir)

    return os.path.abspath(subDir) + '/'
