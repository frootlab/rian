#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, nemoa

def getEmptyFile(file):
    """Return file path for new file."""
    fDir = getFilePath(file)

    # create directory if not available
    if not os.path.exists(fDir):
        nemoa.log('info', 'creating directory \'%s\'' % (fDir))
        os.makedirs(fDir)

    # search unused filename
    fName = getFileName(file)
    fBaseName, fExt = os.path.splitext(fName)
    fBase = '%s/%s' % (fDir, fBaseName)
    file = fBase + fExt
    fID  = 1
    while os.path.exists(file):
        fID += 1
        file = '%s (%s)%s' % (fBase, fID, fExt)

    return file

def getFileName(file):
    """Return file name from given file path as string."""
    return os.path.basename(file)

def getFileExt(file):
    """Return file extension from given file path as string."""
    fileName = os.path.basename(file)
    fileExt  = os.path.splitext(fileName)[1].lstrip('.')
    return fileExt

def getFilePath(file):
    """Return normalized filepath from given file path as string."""
    filePath = os.path.expanduser(file)
    filePath = os.path.expandvars(filePath)
    filePath = os.path.abspath(filePath)
    filePath = os.path.normpath(filePath)
    return os.path.dirname(filePath)

def getEmptySubdir(basepath, subdir = None):

    # create path if not available
    if not os.path.exists(basepath): os.makedirs(basepath)

    #
    if folder: pre = basepath + folder + '_'
    else: pre = basepath

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
    if not os.path.exists(basepath): os.makedirs(basepath)

    # create new subfolder
    subDir = '%s%s/' % (basepath, strToHash(str))
    if not os.path.exists(subDir): os.makedirs(subDir)
    return os.path.abspath(subDir) + '/'
