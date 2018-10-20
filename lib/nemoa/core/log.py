# -*- coding: utf-8 -*-
"""Logging."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import importlib
import logging
import tempfile
import warnings

from pathlib import Path

from nemoa.core import napp, npath
from nemoa.errors import AlreadyStartedError, NotStartedError
from nemoa.types import void, Any, AnyFunc, StrOrInt, OptPath, OptPathLike

_default_level = logging.INFO

def start(logfile: OptPathLike = None, level: int = _default_level) -> bool:
    """Start logging."""
    # Check if logging has already been started
    if '_logger' in globals():
        raise AlreadyStartedError("logging has already been started")
    name = napp.get_var('name') or __name__
    logger = logging.getLogger(name)
    logger.setLevel(level)
    globals()['_logger'] = logger

    # Add file handler for logfile
    return set_logfile(logfile)

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

def get_logfile() -> Path:
    """Get logfile of current logger."""
    logger = _get_logger()
    first = [h for h in logger.handlers if hasattr(h, 'close')][0]
    return Path(getattr(first, 'baseFilename'))

def set_logfile(filepath: OptPathLike = None) -> bool:
    """Set logfile for current logger."""
    logger = _get_logger()

    # Locate valid logfile
    logfile = _locate_logfile(filepath)
    if not isinstance(logfile, Path):
        warnings.warn("turn logging off: could not determine a valid logfile")
        stop()
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

def get_level() -> int:
    """Get level."""
    return getattr(_get_logger(), 'getEffectiveLevel')()

def set_level(level: StrOrInt) -> None:
    """Set level."""
    logger = _get_logger()
    if isinstance(level, str):
        level = level.upper()
    getattr(logger, 'setLevel')(level)

def _locate_logfile(filepath: OptPathLike = None) -> OptPath:
    warn = False
    if isinstance(filepath, (str, Path)):
        filepath = npath.expand(filepath)
        if npath.touch(filepath):
            return filepath
        warn = True

    # Get default logfile
    dirpath = napp.get_dir('user_log_dir')
    basename = napp.get_var('name') or __name__
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

def _get_logger_method(name: str) -> AnyFunc:
    def wrapper(*args: Any, **kwds: Any) -> Any:
        return getattr(_get_logger(), name, void)(*args, **kwds)
    return wrapper

debug = _get_logger_method('debug')
debug.__doc__ = """Debug."""

info = _get_logger_method('info')
info.__doc__ = """Debug."""

warning = _get_logger_method('warning')
warning.__doc__ = """Debug."""

error = _get_logger_method('error')
error.__doc__ = """Debug."""

critical = _get_logger_method('critical')
critical.__doc__ = """Debug."""

exception = _get_logger_method('exception')
exception.__doc__ = """Debug."""
