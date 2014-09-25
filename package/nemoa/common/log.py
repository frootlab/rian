# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import os
import logging
import inspect
import traceback

__shared = {'indent': 0, 'mode': 'exec'}

def log(*args, **kwargs):
    """Log message."""

    if not args: return True

    cmd = args[0].lower()

    if cmd == 'init':
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
        if not 'logfile' in kwargs.keys(): return True
        logfile = kwargs['logfile']

        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        loggerFile = logging.getLogger(__name__ + '.file')
        loggerFile.setLevel(logging.INFO)
        for h in loggerFile.handlers: loggerFile.removeHandler(h)
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setFormatter(logging.Formatter(
            fmt = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%m/%d/%Y %H:%M:%S'))
        loggerFile.addHandler(fileHandler)
        return True

    elif cmd == 'set':
        # set logging mode
        if 'mode' in kwargs and kwargs['mode'] \
            in ['exec', 'shell', 'debug', 'silent']:
            __shared['mode'] = kwargs['mode']
        # set indent
        if 'indent' in kwargs:
            if isinstance(kwargs['indent'], int):
                __shared['indent'] = kwargs['indent']
            elif isinstance(kwargs['indent'], str) \
                and kwargs['indent'][0] in ['+', '-']:
                size = int(kwargs['indent'][1:])
                __shared['indent'] += size \
                    if kwargs['indent'][0] == '+' else -size
        return True

    elif cmd == 'get':
        # return global logging parameters.
        if len(args) == 1:
            return __shared
        if len(args) == 2 and args[1] in __shared.keys():
            return __shared[args[1]]
        return False

    indent = __shared['indent']
    toplevel = indent == 0
    mode   = __shared['mode']

    # get arguments
    if len(args) == 1:
        cmd = 'info'
        msg = args[0]
    if len(args) == 2:
        msg = args[1]

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

    # create file message
    clrStack  = inspect.stack()[1]
    clrMethod = clrStack[3]
    clrModule = inspect.getmodule(clrStack[0]).__name__
    clrName   = clrModule + '.' + clrMethod
    fileMsg   = clrName + ' -> ' + msg.strip()

    # create logging records (depending on loglevels)
    if cmd == 'info':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if mode == 'shell':
            if toplevel: ttyLog.info(pre + ttyMsg)
        else:
            if toplevel: ttyLog.info(
                color['blue'] + ttyMsg + color['default'])
            else: ttyLog.info(ttyMsg)
        return True

    if cmd == 'note':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if not toplevel or mode == 'shell': ttyLog.info(pre + ttyMsg)
        else: ttyLog.info(color['blue'] + ttyMsg + color['default'])
        return True

    if cmd == 'header':
        if mode == 'debug': fileLog.info(fileMsg)
        if mode == 'silent': return True
        if mode == 'shell' and not toplevel: return True
        ttyLog.info(color['green'] + ttyMsg + color['default'])
        return True

    if cmd == 'warning':
        if not mode == 'silent':
            ttyLog.warning(pre + color['yellow'] + ttyMsg + color['default'])
        fileLog.warning(fileMsg)
        return False

    if cmd == 'error':
        ttyLog.error(pre + color['yellow'] + ttyMsg
            + ' (see logfile for debug info)' + color['default'])
        fileLog.error(fileMsg)
        for line in traceback.format_stack():
            msg = line.strip().replace('\n', '-> ').replace('  ', ' ').strip()
            fileLog.error(msg)
        return False

    if cmd == 'critical':
        ttyLog.critical(pre + color['yellow'] + ttyMsg + color['default'])
        fileLog.critical(fileMsg)
        return False

    if cmd == 'debuginfo':
        if mode == 'debug': fileLog.error(fileMsg)
        return False

    if cmd == 'console':
        ttyLog.info(pre + ttyMsg)
        return True

    if cmd == 'logfile':
        fileLog.info(fileMsg)
        return True

    return log('warning', "unknown logging command '%s'!" % (cmd))
