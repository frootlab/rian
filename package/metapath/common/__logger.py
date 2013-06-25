# -*- coding: utf-8 -*-
import os
import logging
import inspect

def initLogger(logfile = None):
    """
    initialize loggers ('null', 'tty' and 'file')
    """

    # initialize null logger
    loggerNull = logging.getLogger(__name__ + '.null')
    #loggerNull.setLevel(logging.INFO)

    # remove all previous handlers and set up null handler
    for h in loggerNull.handlers:
        loggerNull.removeHandler(h)
    
    if hasattr(logging, 'NullHandler'):
        nullHandler = logging.NullHandler()
        loggerNull.addHandler(nullHandler)
    #else:
    #    print 'oh oh -> old python! You need at least python 2.7 - this could result in some errors ...'

    # initialize console logger
    loggerConsole = logging.getLogger(__name__ + '.tty')
    loggerConsole.setLevel(logging.INFO)

    # remove all previous handlers and set up console handler
    for h in loggerConsole.handlers:
        loggerConsole.removeHandler(h)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(fmt = '%(message)s'))
    loggerConsole.addHandler(consoleHandler)

    # initialize file logger
    if not logfile:
        return True
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    loggerFile = logging.getLogger(__name__ + '.file')
    loggerFile.setLevel(logging.INFO)
    #logging.basicConfig()

    # remove all previous handlers and set up file handler
    for h in loggerFile.handlers:
        loggerFile.removeHandler(h)
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logging.Formatter(
        fmt = '%(asctime)s %(levelname)s %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S'))
    loggerFile.addHandler(fileHandler)
    return True

def log(type, msg, quiet = False):

    clrStack = inspect.stack()[1]
    clrMethod = clrStack[3]
    clrModule = inspect.getmodule(clrStack[0]).__name__
    clrName = clrModule + '.' + clrMethod

    # define colors
    color = {
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'green': '\033[92m',
        'default': '\033[0m'}

    # get loggers
    loggers = logging.Logger.manager.loggerDict.keys()
    ttyLog = logging.getLogger(__name__ + '.tty') \
        if __name__ + '.tty' in loggers \
        else logging.getLogger(__name__ + '.null')
    fileLog = logging.getLogger(__name__ + '.file') \
        if __name__ + '.file' in loggers \
        else logging.getLogger(__name__ + '.null')

    # format message
    msg = msg.strip().replace('\n','')
    while '  ' in msg:
        msg = msg.replace('  ', ' ')

    # create logging records (depending on loglevels)
    if type == 'info':
        if not quiet:
            ttyLog.info(msg)
        fileLog.info(clrName + ' -> ' + msg.strip())
        return True
    if type == 'header':
        ttyLog.info(color['green'] + msg + color['default'])
        fileLog.info(clrName + ' -> ' + msg.strip())
        return True
    if type == 'warning':
        if not quiet:
            ttyLog.warning(
                color['yellow'] + msg + color['default'])
        fileLog.warning(clrName + ' -> ' + msg.strip())
        return True
    if type == 'error':
        ttyLog.error(color['yellow'] + msg + color['default'])
        fileLog.error(clrName + ' -> ' + msg.strip())
        return True
    if type == 'critical':
        ttyLog.critical(color['yellow'] + msg + color['default'])
        fileLog.critical(clrName + ' -> ' + msg.strip())
        return True

    # create logging records (depending on logger)
    if type == 'console':
        ttyLog.info(msg)
        return True
    if type == 'logfile':
        fileLog.info(clrName + ' -> ' + msg.strip())
        return True

    log('warning', 'unknown logging type \'%s\'!' % (type))
    return False
