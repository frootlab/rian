# -*- coding: utf-8 -*-
"""Logging.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _Logger.debug():
    https://docs.python.org/3/library/logging.html#logging.Logger.debug
.. _Logger.info():
    https://docs.python.org/3/library/logging.html#logging.Logger.info
.. _Logger.warning():
    https://docs.python.org/3/library/logging.html#logging.Logger.warning
.. _Logger.error():
    https://docs.python.org/3/library/logging.html#logging.Logger.error
.. _Logger.critical():
    https://docs.python.org/3/library/logging.html#logging.Logger.critical

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import importlib
import logging
import tempfile
import warnings

from pathlib import Path

from nemoa.base import env, npath
from nemoa.errors import AlreadyStartedError, NotStartedError
from nemoa.types import void, Any, AnyFunc, StrOrInt, OptPath, OptPathLike

_logger_name = env.get_var('name') or __name__

def start(logfile: OptPathLike = None, level: StrOrInt = logging.INFO) -> bool:
    """Start logging.

    Args:
        logfile: String or `path-like object`_ that identifies a valid filename
            in the directory structure of the operating system. If they do not
            exist, the parent directories of the file are created. If no file is
            given, or the file can not be created, a default logfile within the
            *user log directory* is created. If even the default logfile can not
            be created a temporary logfile is created as fallback.
        level: Integer value or string, which describes the minimum severity of
            events, that are logged. In the order of ascending severity, the
            level indicators are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and
            'CRITICAL'. These level indicators respectively correspond to the
            integer levels 10, 20, 30, 40 and 50. The default level is 'INFO'.

    Returns:
        True if logging could be initiated with a valid logfile.

    """
    _set_logger(logging.getLogger(_logger_name))

    # Set level
    set_level(level)

    # Add file handler for logfile
    if set_logfile(logfile):
        return True

    # If an error occured stop logging
    stop()
    return False

def stop() -> None:
    """Stop logging."""
    logger = _get_logger()

    # Close and remove all previous file handlers
    if logger.hasHandlers():
        remove = [h for h in logger.handlers if hasattr(h, 'close')]
        for handler in remove:
            handler.close()
            logger.removeHandler(handler)

    del globals()['_logger']

def set_logfile(filepath: OptPathLike = None) -> bool:
    """Set logfile for current logger.

    Args:
        logfile: String or `path-like object`_ that identifies a valid filename
            in the directory structure of the operating system. If they do not
            exist, the parent directories of the file are created. If no file is
            given, or the file can not be created, a default logfile within the
            *user log directory* is created. If even the default logfile can not
            be created a temporary logfile is created as fallback.

    Returns:
        True if the logger could be initiated with a valid logfile.

    """
    logger = _get_logger()

    # Locate valid logfile
    logfile = _locate_logfile(filepath)
    if not isinstance(logfile, Path):
        warnings.warn("could not set logfile")
        return False

    # Close and remove all previous file handlers
    if logger.hasHandlers():
        remove = [h for h in logger.handlers if hasattr(h, 'close')]
        for handler in remove:
            handler.close()
            logger.removeHandler(handler)

    # Add file handler for logfile
    handers = importlib.import_module('logging.handlers')
    handler = getattr(handers, 'TimedRotatingFileHandler')(
        str(logfile), when="d", interval=1, backupCount=5)
    #handler = logging.FileHandler(str(logfile))
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return True

def get_logfile() -> Path:
    """Get logfile of current logger."""
    logger = _get_logger()

    first = [h for h in logger.handlers if hasattr(h, 'close')][0]
    return Path(getattr(first, 'baseFilename'))

def set_level(level: StrOrInt) -> None:
    """Set level.

    Args:
        level: Integer value or string, which describes the minimum severity of
            events, that are logged. In the order of ascending severity, the
            level names are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'.
            These respectively correspond to the level numbers 10, 20, 30, 40
            and 50.

    """
    logger = _get_logger()
    if isinstance(level, str):
        level = level.upper()
    getattr(logger, 'setLevel')(level)

def get_level(as_name: bool = True) -> StrOrInt:
    """Get level.

    Args:
        as_name: Boolean value which determines, if the returned level is given
            as level name or level number.

    Returns:
        Integer value or string, which describes the minimum severity of events,
        that are logged.

    """
    level = getattr(_get_logger(), 'getEffectiveLevel')()
    if not as_name:
        return level
    index = int(max(min(level, 50), 0) / 10)
    return ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'][index]

def _get_logger_method(name: str) -> AnyFunc:
    def wrapper(msg: str, *args: Any, **kwds: Any) -> Any:
        return getattr(_get_logger(), name, void)(*args, **kwds)
    return wrapper

debug = _get_logger_method('debug')
debug.__doc__ = """Wrapper function to `Logger.debug()`_."""

info = _get_logger_method('info')
info.__doc__ = """Wrapper function to `Logger.info()`_."""

warning = _get_logger_method('warning')
warning.__doc__ = """Wrapper function to `Logger.warning()`_."""

error = _get_logger_method('error')
error.__doc__ = """Wrapper function to `Logger.error()`_."""

critical = _get_logger_method('critical')
critical.__doc__ = """Wrapper function to `Logger.critical()`_."""

def _locate_logfile(filepath: OptPathLike = None) -> OptPath:
    warn = False
    if isinstance(filepath, (str, Path)):
        filepath = npath.expand(filepath)
        if npath.touch(filepath):
            return filepath
        warn = True

    # Get default logfile
    dirpath = env.get_dir('user_log_dir')
    basename = env.get_var('name') or __name__
    default_log = Path(dirpath, basename + '.log')
    if npath.touch(default_log):
        if warn:
            warnings.warn(
                f"logfile '{str(filepath)}' is not valid: "
                f"using default logfile '{str(default_log)}'")
        return default_log

    # Get temporary logfile
    temp_log = Path(tempfile.NamedTemporaryFile().name + '.log')
    if npath.touch(temp_log):
        warnings.warn(
            f"default logfile '{str(filepath)}' is not valid: "
            f"using temporary logfile '{str(temp_log)}'")
        return temp_log
    return None

def _get_logger() -> logging.Logger:
    if not '_logger' in globals():
        raise NotStartedError("logging has not been started")
    return globals()['_logger']

def _set_logger(logger: logging.Logger) -> None:
    if '_logger' in globals():
        raise AlreadyStartedError("logging has already been started")
    globals()['_logger'] = logger
