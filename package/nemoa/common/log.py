#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, logging, inspect
__shared = {'quiet': False, 'indent': 0, 'debug': False}

def initLogger(logfile = None):
    """Initialize loggers ('null', 'tty' and 'file')."""

    # initialize null logger
    loggerNull = logging.getLogger(__name__ + '.null')

    # remove all previous handlers and set up null handler
    for h in loggerNull.handlers:
        loggerNull.removeHandler(h)
    
    if hasattr(logging, 'NullHandler'):
        nullHandler = logging.NullHandler()
        loggerNull.addHandler(nullHandler)

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

    # remove all previous handlers and set up file handler
    for h in loggerFile.handlers:
        loggerFile.removeHandler(h)
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logging.Formatter(
        fmt = '%(asctime)s %(levelname)s %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S'))
    loggerFile.addHandler(fileHandler)

    return True

def setLog(**kwargs):
    """Set global logging options."""

    if 'quiet' in kwargs and kwargs['quiet'] in [True, False]:
        __shared['quiet'] = kwargs['quiet']
    if 'debug' in kwargs and kwargs['debug'] in [True, False]:
        __shared['debug'] = kwargs['debug']
    if 'indent' in kwargs:
        if isinstance(kwargs['indent'], int):
            __shared['indent'] = kwargs['indent']
        elif isinstance(kwargs['indent'], str) \
            and kwargs['indent'][0] in ['+', '-']:
            if kwargs['indent'][0] == '+':
                __shared['indent'] += int(kwargs['indent'][1:])
            else:
                __shared['indent'] -= int(kwargs['indent'][1:])
    return True

def log(type, msg, quiet = False):
    """Log message."""

    clrStack = inspect.stack()[1]
    clrMethod = clrStack[3]
    clrModule = inspect.getmodule(clrStack[0]).__name__
    clrName = clrModule + '.' + clrMethod

    quiet  = __shared['quiet']
    debug  = __shared['debug']
    indent = __shared['indent']

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
    if indent:
        ttyMsg = '  ' * indent + msg
    else:
        ttyMsg = msg
    fileMsg = clrName + ' -> ' + msg.strip()

    # create logging records (depending on loglevels)
    if type == 'info':
        if not quiet:
            ttyLog.info(ttyMsg)
        if debug:
            fileLog.info(fileMsg)
        return True
    if type == 'title':
        if not quiet:
            ttyLog.info(color['blue'] + ttyMsg + color['default'])
        if debug:
            fileLog.info(fileMsg)
        return True
    if type == 'header':
        if not quiet:
            ttyLog.info(color['green'] + ttyMsg + color['default'])
        if debug:
            fileLog.info(fileMsg)
        return True
    if type == 'warning':
        if not quiet:
            ttyLog.warning(color['yellow'] + ttyMsg + color['default'])
        fileLog.warning(fileMsg)
        return True
    if type == 'error':
        ttyLog.error(color['yellow'] + ttyMsg + ' (see logfile for debug info)' + color['default'])
        fileLog.error(fileMsg)
        import traceback
        for line in traceback.format_stack():
            msg = line.strip().replace('\n', '-> ').replace('  ', ' ').strip()
            fileLog.error(msg)
        return True
    if type == 'debuginfo':
        if debug:
            fileLog.error(fileMsg)
        return True
    if type == 'critical':
        ttyLog.critical(color['yellow'] + ttyMsg + color['default'])
        fileLog.critical(fileMsg)
        return True

    # create logging records (depending on logger)
    if type == 'console':
        ttyLog.info(ttyMsg)
        return True
    if type == 'logfile':
        fileLog.info(fileMsg)
        return True

    log('warning', 'unknown logging type \'%s\'!' % (type))
    return False
