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
        logger_null = logging.getLogger(__name__ + '.null')
        for h in logger_null.handlers: logger_null.removeHandler(h)
        if hasattr(logging, 'NullHandler'):
            null_handler = logging.NullHandler()
            logger_null.addHandler(null_handler)

        # initialize console logger, remove all previous handlers
        # and set up console handler
        logger_console = logging.getLogger(__name__ + '.tty')
        logger_console.setLevel(logging.INFO)
        for h in logger_console.handlers: logger_console.removeHandler(h)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt = '%(message)s'))
        logger_console.addHandler(console_handler)

        # initialize file logger, remove all previous handlers
        # and set up file handler
        if not 'logfile' in kwargs.keys(): return True
        logfile = kwargs['logfile']

        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        logger_file = logging.getLogger(__name__ + '.file')
        logger_file.setLevel(logging.INFO)
        for h in logger_file.handlers: logger_file.removeHandler(h)
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(logging.Formatter(
            fmt = '%(asctime)s %(levelname)s %(message)s',
            datefmt = '%m/%d/%Y %H:%M:%S'))
        logger_file.addHandler(file_handler)
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
    mode = __shared['mode']

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
    tty_log = logging.getLogger(__name__ + '.tty') \
        if __name__ + '.tty' in loggers \
        else logging.getLogger(__name__ + '.null')
    file_log = logging.getLogger(__name__ + '.file') \
        if __name__ + '.file' in loggers \
        else logging.getLogger(__name__ + '.null')

    # format message
    msg = msg.strip().replace('\n', '')
    while '  ' in msg: msg = msg.replace('  ', ' ')

    if mode == 'shell':
        pre = color['blue'] + '> ' + color['default']
        tty_msg = msg
    else:
        pre = ''
        tty_msg = '  ' * indent + msg

    # create file message
    clrStack  = inspect.stack()[1]
    clrMethod = clrStack[3]
    clrModule = inspect.getmodule(clrStack[0]).__name__
    clrName   = clrModule + '.' + clrMethod
    file_msg   = clrName + ' -> ' + msg.strip()

    # create logging records (depending on loglevels)
    if cmd == 'info':
        if mode == 'debug': file_log.info(file_msg)
        if mode == 'silent': return True
        if mode == 'shell':
            if toplevel: tty_log.info(pre + tty_msg)
        else:
            if toplevel: tty_log.info(
                color['blue'] + tty_msg + color['default'])
            else: tty_log.info(tty_msg)
        return True

    if cmd == 'note':
        if mode == 'debug': file_log.info(file_msg)
        if mode == 'silent': return True
        if not toplevel or mode == 'shell': tty_log.info(pre + tty_msg)
        else: tty_log.info(color['blue'] + tty_msg + color['default'])
        return True

    if cmd == 'header':
        if mode == 'debug': file_log.info(file_msg)
        if mode == 'silent': return True
        if mode == 'shell' and not toplevel: return True
        tty_log.info(color['green'] + tty_msg + color['default'])
        return True

    if cmd == 'warning':
        if not mode == 'silent':
            tty_log.warning(pre + color['yellow'] + tty_msg + color['default'])
        file_log.warning(file_msg)
        return False

    if cmd == 'error':
        tty_log.error(pre + color['yellow'] + tty_msg
            + ' (see logfile for debug info)' + color['default'])
        file_log.error(file_msg)
        for line in traceback.format_stack():
            msg = line.strip().replace('\n', '-> ').replace('  ', ' ').strip()
            file_log.error(msg)
        return False

    if cmd == 'critical':
        tty_log.critical(pre + color['yellow'] + tty_msg + color['default'])
        file_log.critical(file_msg)
        return False

    if cmd == 'debuginfo':
        if mode == 'debug': file_log.error(file_msg)
        return False

    if cmd == 'console':
        tty_log.info(pre + tty_msg)
        return True

    if cmd == 'logfile':
        file_log.info(file_msg)
        return True

    return log('warning', "unknown logging command '%s'!" % (cmd))
