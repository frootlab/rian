# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Logging.

This module implements process global logging as a singleton object, using the
standard library module :py:mod:`logging`.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import contextlib
import importlib
import logging
import warnings
from pathlib import Path
from flab.base import attrib, env, abc
from flab.errors import ExistsError, NotExistsError
from flab.base.types import void, Any, AnyOp, ClassVar, PathLike, StrList
from flab.base.types import StrOrInt, OptPath, Void

#
# Logger Class
#

class Logger(attrib.Group, abc.Singleton):
    """Singleton class for logging.

    Args:
        name: String identifier of Logger, given as a period-separated
            hierarchical value like 'foo.bar.baz'. The name of a Logger also
            identifies respective parents and children by the name hierachy,
            which equals the Python package hierarchy.
        file: String or :term:`path-like object` that identifies a valid
            filename in the directory structure of the operating system. If they
            do not exist, the parent directories of the file are created. If no
            file is given, a default logfile within the applications
            *user-log-dir* is created. If the logfile can not be created a
            temporary logfile in the systems *temp* folder is created as a
            fallback.
        level: Integer value or string, which describes the minimum required
            severity of events, to be logged. Ordered by ascending severity, the
            allowed level names are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and
            'CRITICAL'. The respectively corresponding level numbers are 10, 20,
            30, 40 and 50. The default level is 'INFO'.

    """

    #
    # Protected Class Variables
    #

    _level_names: ClassVar[StrList] = [
        'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    _default_name: ClassVar[str] = env.get_var('name') or __name__
    _default_file: ClassVar[Path] = Path(
        env.get_dir('user_log_dir'), _default_name + '.log')
    _default_level: ClassVar[StrOrInt] = logging.INFO

    #
    # Public Attributes
    #

    logger: property = attrib.Virtual(
        '_get_logger', '_set_logger', dtype=logging.Logger)

    name: property = attrib.Virtual('_get_name', '_set_name', dtype=str)
    name.__doc__ = """
    String identifier of Logger, given as a period-separated hierarchical value
    like 'foo.bar.baz'. The name of a Logger also identifies respective parents
    and children by the name hierachy, which equals the Python package
    hierarchy.
    """

    file: property = attrib.Virtual('_get_file', '_set_file', dtype=(str, Path))
    file.__doc__ = """
    String or :term:`path-like object` that identifies a valid filename in the
    directory structure of the operating system. If they do not exist, the
    parent directories of the file are created. If no file is given, a default
    logfile within the applications *user-log-dir* is created. If the logfile
    can not be created a temporary logfile in the systems *temp* folder is
    created as a fallback.
    """

    level: property = attrib.Virtual(
        '_get_level', '_set_level', dtype=(str, int))
    level.__doc__ = """
    Integer value or string, which describes the minimum required severity of
    events, to be logged. Ordered by ascending severity, the allowed level names
    are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. The respectively
    corresponding level numbers are 10, 20, 30, 40 and 50. The default level is
    'INFO'.
    """

    #
    # Protected Attributes
    #

    _logger: property = attrib.Temporary(dtype=logging.Logger)

    #
    # Special Methods
    #

    def __init__(
            self, name: str = _default_name, file: PathLike = _default_file,
            level: StrOrInt = _default_level) -> None:
        super().__init__() # Initialize Attribute Container
        self._start_logging(name=name, file=file, level=level) # Start logging

    def __del__(self) -> None:
        self._stop_logging() # Stop logging

    def __str__(self) -> str:
        return str(self.logger)

    #
    # Public Methods
    #

    def log(self, level: StrOrInt, msg: str, *args: Any, **kwds: Any) -> None:
        """Log event.

        Args:
            level: Integer value or string, which describes the severity of the
                event. In the order of ascending severity, the accepted level
                names are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'.
                The respectively corresponding level numbers are 10, 20, 30, 40
                and 50.
            msg: Message :ref:`format string <formatstrings>`, containing
                literal text or braces delimited replacement fields. Each
                replacement field contains either the numeric index of a
                positional argument, given by *args, or the name of a keyword
                argument, given by the keyword *extra*.
            *args: Arguments, which can be used by the message format string.
            **kwds: Additional Keywords, used by :meth:`logging.Logger.log`.

        """
        if isinstance(level, str):
            level = self._get_level_number(level)
        self.logger.log(level, msg, *args, **kwds)

    #
    # Protected Methods
    #

    def _start_logging(
            self, name: str = _default_name, file: PathLike = _default_file,
            level: StrOrInt = _default_level) -> bool:
        logger = logging.getLogger(name) # Create new Logger instance
        self._set_logger(logger) # Bind Logger instance to global variable
        self._set_level(level) # Set log level
        self._set_file(file) # Add file handler for logfile
        if not self.file.is_file(): # Stop logging if an error occured
            self._stop_logging()
            return False
        return True

    def _stop_logging(self) -> None:
        for handler in self.logger.handlers: # Close file handlers
            with contextlib.suppress(AttributeError):
                handler.close()
        self._logger = None

    def _get_logger(self, auto_start: bool = True) -> logging.Logger:
        if not self._logger:
            if auto_start:
                self._start_logging()
            else:
                raise NotExistsError("logging has not been started")
        return self._logger

    def _set_logger(
            self, logger: logging.Logger, auto_stop: bool = True) -> None:
        if self._logger:
            if auto_stop:
                self._stop_logging()
            else:
                raise ExistsError("logging has already been started")
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

    def _set_file(self, filepath: PathLike = _default_file) -> None:
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
        names = self._level_names
        return names[int(max(min(level, 50), 0) / 10)]

    def _get_level_number(self, name: str) -> int:
        name = name.upper()
        names = self._level_names
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
            self, filepath: PathLike = _default_file) -> OptPath:
        # Get valid logfile from filepath
        if isinstance(filepath, (str, Path)):
            logfile = env.expand(filepath)
            if env.touch(logfile):
                return logfile

        # Get temporary logfile
        logfile = env.get_temp_file(suffix='log')
        if env.touch(logfile):
            warnings.warn(
                f"logfile '{filepath}' is not valid: "
                f"using temporary logfile '{logfile}'")
            return logfile
        return None

#
# Singleton Accessor Functions
#

def _get_lazy_method(name: str) -> AnyOp:
    def wrapper(*args: Any, **kwds: Any) -> Any:
        return getattr(Logger(), name, void)(*args, **kwds)
    return wrapper

debug: Void = _get_lazy_method('debug')
"""Call :meth:`~logging.Logger.debug` of current Logger instance."""

info: Void = _get_lazy_method('info')
"""Call :meth:`~logging.Logger.info` of current Logger instance."""

warning: Void = _get_lazy_method('warning')
"""Call :meth:`~logging.Logger.warning` of current Logger instance."""

error: Void = _get_lazy_method('error')
"""Call :meth:`~logging.Logger.error` of current Logger instance."""

critical: Void = _get_lazy_method('critical')
"""Call :meth:`~logging.Logger.critical` of current Logger instance."""

exception: Void = _get_lazy_method('exception')
"""Call :meth:`~logging.Logger.exceptions` of current Logger instance."""
