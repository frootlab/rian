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
"""User Interface."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import functools
import os
import sys
from flab.base import pkg
from nemoa.core import log
from flab.base.types import Any, AnyOp, ErrMeta, ErrType, ErrStack, OptVoid

#
# Module Variables
#

_NOTIFICATION_TYPES = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
_DEFAULT_NOTIFICATION_LEVEL = 1

#
# Notifications
#

def get_notification_level() -> str:
    """Get notification level."""
    level = globals().get('level', _DEFAULT_NOTIFICATION_LEVEL)
    return _NOTIFICATION_TYPES[level]

def set_notification_level(level: str) -> None:
    """Set notification level."""
    level = level.upper()
    if not level in _NOTIFICATION_TYPES:
        raise ValueError(
            f"notification level '{level}' is not valid")
    globals()['level'] = _NOTIFICATION_TYPES.index(level)

def is_above_level(ntype: str) -> bool:
    """Check if notification type is above current level."""
    if not ntype in _NOTIFICATION_TYPES:
        return False
    level = globals().get('level', _DEFAULT_NOTIFICATION_LEVEL)
    return _NOTIFICATION_TYPES.index(ntype) >= level

def get_notification_hook(ntype: str) -> OptVoid:
    """Get hook for given notification type."""
    if not ntype in _NOTIFICATION_TYPES:
        raise ValueError(
            f"notification type '{ntype}' is not valid")
    return pkg.get_attr('hook_' + ntype.lower(), None)

def notify(ntype: str, msg: str, *args: Any, **kwds: Any) -> None:
    """Notify user."""
    # Log message
    ntype = ntype.upper()
    if msg:
        log.Logger().log(ntype, msg)

    # Check if notification type is to be filtered
    if not is_above_level(ntype):
        return None

    # Get hook for given notification type
    func = get_notification_hook(ntype)
    if func:
        func(msg, *args, **kwds)
    else:
        print(msg, *args, **kwds)
    return None

def debug(msg: str, *args: Any, **kwds: Any) -> None:
    """Provide runtime information for debugging."""
    return notify('debug', msg, *args, **kwds)

def hook_debug(msg: str, *args: Any, **kwds: Any) -> None:
    """Print debug notification to stdout."""
    print(msg, *args, **kwds)

def info(msg: str, *args: Any, **kwds: Any) -> None:
    """Inform user about a regular condition."""
    return notify('info', msg, *args, **kwds)

def hook_info(msg: str, *args: Any, **kwds: Any) -> None:
    """Print info notification to stdout."""
    print(msg, *args, **kwds)

def warning(msg: str, *args: Any, **kwds: Any) -> None:
    """Warn user about a condition that might cause a problems."""
    return notify('warning', msg, *args, **kwds)

def hook_warning(msg: str, *args: Any, **kwds: Any) -> None:
    """Print warning notification to stdout."""
    print(msg, *args, **kwds)

def error(msg: str, *args: Any, **kwds: Any) -> None:
    """Notify user about an error."""
    return notify('error', msg, *args, **kwds)

def hook_error(msg: str, *args: Any, **kwds: Any) -> None:
    """Print error notification to stdout."""
    print(msg, *args, **kwds)

def critical(msg: str, *args: Any, **kwds: Any) -> None:
    """Notify user about a critical error."""
    return notify('critical', msg, *args, **kwds)

def hook_critical(msg: str, *args: Any, **kwds: Any) -> None:
    """Print critical error notification to stdout."""
    print(msg, *args, **kwds)

#
#
#

def clear() -> None:
    """Clear screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

#
# Exception Handling
#

def hook_exception(cls: ErrMeta, obj: ErrType, tb: ErrStack) -> None:
    """Alternative exception hook."""
    log.exception(str(obj), exc_info=(cls, obj, tb))

def bypass_exceptions(
        func: AnyOp, hook: AnyOp, interrupt: bool = False) -> AnyOp:
    """Bypass exceptions from given function."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwds: Any) -> Any:
        err = sys.exc_info()[0]
        if err and not issubclass(err, Exception):
            return func(*args, **kwds)
        hook(*sys.exc_info())
        if interrupt:
            return None
        return func(*args, **kwds)
    return wrapper

def bypass_python_exepthook() -> None:
    """Bypass exceptions from sys.excepthook."""
    sys.excepthook = bypass_exceptions(sys.excepthook, hook_exception)
