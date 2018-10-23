# -*- coding: utf-8 -*-
"""Logging.

This module implements application global logging by a singleton design class
and module level wrappers to convenience functions of the ``logging``_ module
from standard library.

.. References:
.. _logging:
    https://docs.python.org/3/library/logging.html
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _Format String:
    https://docs.python.org/3/library/string.html#format-string-syntax
.. _Logger.log():
    https://docs.python.org/3/library/logging.html#logging.Logger.log
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
.. _Logger.exception():
    https://docs.python.org/3/library/logging.html#logging.Logger.exception

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

__all__ = ['get_instance', 'debug', 'info', 'warning', 'error', 'critical',
           'exception']

import contextlib
import importlib
import logging
import tempfile
import warnings

from pathlib import Path

from nemoa.base import env, npath
from nemoa.classes import ReadWriteAttr
from nemoa.errors import AlreadyStartedError, NotStartedError
from nemoa.types import (
    void, Any, AnyFunc, ClassVar, PathLike, StrList, StrOrInt, OptPath,
    VoidFunc)

#
# Logger Class
#

class Logger:
    """Logger class.

    Args:
        name: String identifier of Logger, given as a period-separated
            hierarchical value like 'foo.bar.baz'. The name of a Logger also
            identifies respective parents and children by the name hierachy,
            which equals the Python package hierarchy.
        file: String or `path-like object`_ that identifies a valid filename in
            the directory structure of the operating system. If they do not
            exist, the parent directories of the file are created. If no file is
            given, a default logfile within the applications *user-log-dir* is
            created. If the logfile can not be created a temporary logfile in
            the systems *temp* folder is created as a fallback.
        level: Integer value or string, which describes the minimum required
            severity of events, to be logged. Ordered by ascending severity, the
            allowed level names are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and
            'CRITICAL'. The respectively corresponding level numbers are 10, 20,
            30, 40 and 50. The default level is 'INFO'.

    """

    #
    # Private Class Variables
    #

    _LEVEL_NAMES: ClassVar[StrList] = [
        'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    _DEFAULT_NAME: ClassVar[str] = env.get_var('name') or __name__
    _DEFAULT_FILE: ClassVar[Path] = Path(
        env.get_dir('user_log_dir'), _DEFAULT_NAME + '.log')
    _DEFAULT_LEVEL: ClassVar[StrOrInt] = logging.INFO

    #
    # Private Instance Variables
    #

    _logger: logging.Logger

    #
    # Public Instance Properties
    #

    logger: property = ReadWriteAttr(
        logging.Logger, getter='_get_logger', setter='_set_logger')

    name: property = ReadWriteAttr(
        str, getter='_get_name', setter='_set_name', default=_DEFAULT_NAME)
    name.__doc__ = """Name of logger.

    String identifier of Logger, given as a period-separated hierarchical value
    like 'foo.bar.baz'. The name of a Logger also identifies respective parents
    and children by the name hierachy, which equals the Python package
    hierarchy.
    """

    file: property = ReadWriteAttr(
        (str, Path), getter='_get_file', setter='_set_file',
        default=_DEFAULT_FILE)
    file.__doc__ = """Log file.

    String or `path-like object`_ that identifies a valid filename in the
    directory structure of the operating system. If they do not exist, the
    parent directories of the file are created. If no file is given, a default
    logfile within the applications *user-log-dir* is created. If the logfile
    can not be created a temporary logfile in the systems *temp* folder is
    created as a fallback.
    """

    level: property = ReadWriteAttr(
        (str, int), getter='_get_level', setter='_set_level',
        default=_DEFAULT_LEVEL)
    level.__doc__ = """Log level.

    Integer value or string, which describes the minimum required severity of
    events, to be logged. Ordered by ascending severity, the allowed level names
    are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. The respectively
    corresponding level numbers are 10, 20, 30, 40 and 50. The default level is
    'INFO'.
    """

    #
    # Magic
    #

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize instance."""
        self._start_logging(*args, **kwds)

    def __del__(self) -> None:
        """Run destructor for instance."""
        self._stop_logging()

    def __str__(self) -> str:
        """Represent instance as string."""
        return str(self.logger)

    #
    # Public Instance Methods
    #

    def log(self, level: StrOrInt, msg: str, *args: Any, **kwds: Any) -> None:
        """Log event.

        Args:
            level: Integer value or string, which describes the severity of the
                event. In the order of ascending severity, the accepted level
                names are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'.
                The respectively corresponding level numbers are 10, 20, 30, 40
                and 50.
            msg: Message ``format string``_, which may can contain literal text
                or replacement fields delimited by braces. Each replacement
                field contains either the numeric index of a positional
                argument, given by *args, or the name of a keyword argument,
                given by the keyword *extra*.
            *args: Arguments, which can be used by the message format string.
            **kwds: Additional Keywords, used by the function by
                `Logger.log()`_.

        """
        if isinstance(level, str):
            level = self._get_level_number(level)
        self.logger.log(level, msg, *args, **kwds)

    #
    # Private Instance Methods
    #

    def _start_logging(
            self, name: str = _DEFAULT_NAME, file: PathLike = _DEFAULT_FILE,
            level: StrOrInt = _DEFAULT_LEVEL) -> bool:
        logger = logging.getLogger(name) # Create new logger instance
        self._set_logger(logger) # Bind new logger instance to global variable
        self._set_level(level) # Set log level
        self._set_file(file) # Add file handler for logfile
        if not self.file.is_file(): # If an error occured stop logging
            self._stop_logging()
            return False
        return True

    def _stop_logging(self) -> None:
        for handler in self.logger.handlers: # Close file handlers
            with contextlib.suppress(AttributeError):
                handler.close()
        delattr(self, '_logger')

    def _get_logger(self, auto_start: bool = True) -> logging.Logger:
        if not hasattr(self, '_logger'):
            if auto_start:
                self._start_logging()
            else:
                raise NotStartedError("logging has not been started")
        return self._logger

    def _set_logger(
            self, logger: logging.Logger, auto_stop: bool = True) -> None:
        if hasattr(self, '_logger'):
            if auto_stop:
                self._stop_logging()
            else:
                raise AlreadyStartedError("logging has already been started")
        self._logger = logger

    def _get_name(self) -> str:
        return self.logger.name

    def _set_name(self, name: str) -> None:
        self.logger.name = name

    def _get_file(self) -> OptPath:
        for handler in self.logger.handlers:
            with contextlib.suppress(AttributeError):
                return Path(handler.baseFilename)
        return None

    def _set_file(self, filepath: PathLike = _DEFAULT_FILE) -> None:
        # Locate valid logfile
        logfile = self._locate_logfile(filepath)
        if not isinstance(logfile, Path):
            warnings.warn("could not set logfile")
            return None

        # Close and remove all previous file handlers
        if self.logger.hasHandlers():
            remove = [h for h in self.logger.handlers if hasattr(h, 'close')]
            for handler in remove:
                handler.close()
                self.logger.removeHandler(handler)

        # Add file handler for logfile
        handers = importlib.import_module('logging.handlers')
        handler = getattr(handers, 'TimedRotatingFileHandler')(
            str(logfile), when="d", interval=1, backupCount=5)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return None

    def _get_level(self, as_name: bool = True) -> StrOrInt:
        level = getattr(self.logger, 'getEffectiveLevel')()
        if not as_name:
            return level
        return self._get_level_name(level)

    def _get_level_name(self, level: int) -> str:
        names = self._LEVEL_NAMES
        return names[int(max(min(level, 50), 0) / 10)]

    def _get_level_number(self, name: str) -> int:
        name = name.upper()
        names = self._LEVEL_NAMES
        if not name in names:
            allowed = ', '.join(names[1:])
            raise ValueError(
                f"{name} is not a valid level name, "
                f"allowed values are: {allowed}")
        return names.index(name) * 10

    def _set_level(self, level: StrOrInt) -> None:
        if isinstance(level, str):
            level = level.upper()
        getattr(self.logger, 'setLevel')(level)

    def _locate_logfile(
            self, filepath: PathLike = _DEFAULT_FILE) -> OptPath:
        # Get valid logfile from filepath
        if isinstance(filepath, (str, Path)):
            logfile = npath.expand(filepath)
            if npath.touch(logfile):
                return logfile

        # Get temporary logfile
        logfile = Path(tempfile.NamedTemporaryFile().name + '.log')
        if npath.touch(logfile):
            warnings.warn(
                f"logfile '{filepath}' is not valid: "
                f"using temporary logfile '{logfile}'")
            return logfile
        return None

#
# Singleton Accessor Functions
#

def get_instance() -> Logger:
    """Get logger instance."""
    if not '_logger' in globals():
        globals()['_logger'] = Logger()
    return globals()['_logger']

def get_method(name: str) -> AnyFunc:
    """Get method of logger instance."""
    def wrapper(*args: Any, **kwds: Any) -> Any:
        self = get_instance()
        method = getattr(self.logger, name, void)
        return method(*args, **kwds)
    return wrapper

#
# Convenience Functions
#

debug: VoidFunc = get_method('debug')
debug.__doc__ = """Wrapper function to `Logger.debug()`_."""

info: VoidFunc = get_method('info')
info.__doc__ = """Wrapper function to `Logger.info()`_."""

warning: VoidFunc = get_method('warning')
warning.__doc__ = """Wrapper function to `Logger.warning()`_."""

error: VoidFunc = get_method('error')
error.__doc__ = """Wrapper function to `Logger.error()`_."""

critical: VoidFunc = get_method('critical')
critical.__doc__ = """Wrapper function to `Logger.critical()`_."""

exception: VoidFunc = get_method('exception')
exception.__doc__ = """Wrapper function to `Logger.exception()`_."""
