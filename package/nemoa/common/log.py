#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, logging, inspect, traceback
__shared = {'indent': 0, 'mode': 'exec'}

def initLogger(logfile = None):
    """Initialize loggers and set up handlers."""

    # initialize null logger, remove all previous handlers
    # and set up null handler
    loggerNull = logging.getLogger(__name__ + '.null')
    for h in loggerNull.handlers: loggerNull.removeHandler(h)
    if hasattr(logging, 'NullHandler'):
        nullHandler = logging.NullHandler()
        loggerNull.addHandler(nullHandler)

    # initialize console logger, remove all previous handlers
    # and set up console handler
    loggerConsole = logging.getLogger(__name__ + '.tty')
    loggerConsole.setLevel(logging.INFO)
    for h in loggerConsole.handlers: loggerConsole.removeHandler(h)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(fmt = '%(message)s'))
    loggerConsole.addHandler(consoleHandler)

    # initialize file logger, remove all previous handlers
    # and set up file handler
    if not logfile: return True
    if not os.path.exists(os.path.dirname(logfile)): os.makedirs(
        os.path.dirname(logfile))
    loggerFile = logging.getLogger(__name__ + '.file')
    loggerFile.setLevel(logging.INFO)
    for h in loggerFile.handlers: loggerFile.removeHandler(h)
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logging.Formatter(
        fmt = '%(asctime)s %(levelname)s %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S'))
    loggerFile.addHandler(fileHandler)
    return True

def setLog(**kwargs):
    """Set global logging parameters."""

    if 'mode' in kwargs and kwargs['mode'] in ['exec', 'shell', 'debug', 'silent']:
        __shared['mode'] = kwargs['mode']
    if 'indent' in kwargs:
        if isinstance(kwargs['indent'], int):
            __shared['indent'] = kwargs['indent']
        elif isinstance(kwargs['indent'], str) \
            and kwargs['indent'][0] in ['+', '-']:
            size = int(kwargs['indent'][1:])
            __shared['indent'] += size if kwargs['indent'][0] == '+' else -size
    return True

def getLog():
    """Return global loging parameters."""
    return __shared

def log(*args):
    """Log message."""

    clrStack  = inspect.stack()[1]
    clrMethod = clrStack[3]
    clrModule = inspect.getmodule(clrStack[0]).__name__
    clrName   = clrModule + '.' + clrMethod

    indent = __shared['indent']
    mode   = __shared['mode']

    # get arguments
    if len(args) == 1:
        type = 'info'
        msg  = args[0]
    if len(args) == 2:
        type = args[0]
        msg  = args[1]

    # define colors
    color = {
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'green': '\033[92m',
        'default': '\033[0m'}

    # get loggers
    loggers = logging.Logger.manager.loggerDict.keys()
    ttyLog  = logging.getLogger(__name__ + '.tty') \
        if __name__ + '.tty' in loggers \
        else logging.getLogger(__name__ + '.null')
    fileLog = logging.getLogger(__name__ + '.file') \
        if __name__ + '.file' in loggers \
        else logging.getLogger(__name__ + '.null')

    # format message
    msg = msg.strip().replace('\n', '')
    while '  ' in msg: msg = msg.replace('  ', ' ')
    if mode == 'shell':
        pre = color['blue'] + '> ' + color['default']
        ttyMsg = msg
    else:
        pre = ''
        ttyMsg = '  ' * indent + msg
    fileMsg = clrName + ' -> ' + msg.strip()

    # create logging records (depending on loglevels)
    if type == 'info':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if mode == 'shell':
            if indent > 0: return True
            else: ttyLog.info(pre + ttyMsg)
        else:
             if indent > 0: ttyLog.info(ttyMsg)
             else: ttyLog.info(color['blue'] + ttyMsg + color['default'])
        return True
    if type == 'note':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if indent > 0 or mode == 'shell': ttyLog.info(pre + ttyMsg)
        else: ttyLog.info(color['blue'] + ttyMsg + color['default'])
        return True
    if type == 'header':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if mode == 'shell' and indent > 0: return True
        ttyLog.info(color['green'] + ttyMsg + color['default'])
        return True
    if type == 'warning':
        if not mode == 'silent': ttyLog.warning(pre + color['yellow'] + ttyMsg + color['default'])
        fileLog.warning(fileMsg)
        return False
    if type == 'error':
        ttyLog.error(pre + color['yellow'] + ttyMsg + ' (see logfile for debug info)' + color['default'])
        fileLog.error(fileMsg)
        for line in traceback.format_stack():
            msg = line.strip().replace('\n', '-> ').replace('  ', ' ').strip()
            fileLog.error(msg)
        return False
    if type == 'critical':
        ttyLog.critical(pre + color['yellow'] + ttyMsg + color['default'])
        fileLog.critical(fileMsg)
        return False

    if type == 'debuginfo':
        if mode == 'debug': fileLog.error(fileMsg)
        return False

    # create logging records (depending on logger)
    if type == 'console':
        ttyLog.info(pre + ttyMsg)
        return True
    if type == 'logfile':
        fileLog.info(fileMsg)
        return True

    log('warning', 'unknown logging type \'%s\'!' % (type))
    return False
