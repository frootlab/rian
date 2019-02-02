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
"""Call stack helper functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from nemoa.base import check, pkg
from nemoa.types import Module

def get_caller_module() -> Module:
    """Get reference to callers module."""
    name = get_caller_module_name(-2)
    if name:
        module = pkg.get_module(name)
        if isinstance(module, Module):
            return module
    raise ModuleNotFoundError("could not detect module of caller")

def get_caller_module_name(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of module.

    """
    # Check types
    check.has_type("'frame'", frame, int)

    # Check values
    if frame > 0:
        raise ValueError(
            "'frame' is required to be a negative number or zero")

    # Traceback frames using inspect
    mname: str = ''
    cframe = inspect.currentframe()
    for _ in range(abs(frame) + 1):
        if cframe is None:
            break
        cframe = cframe.f_back
    if cframe is not None:
        mname = cframe.f_globals['__name__']

    return mname

def get_caller_name(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of the caller.

    """
    # Check types
    check.has_type("'frame'", frame, int)

    # Check value of 'frame'
    if frame > 0:
        raise ValueError(
            "'frame' is required to be a negative number or zero")

    # Get name of caller using inspect
    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fbase = stack[3]
    return '.'.join([mname, fbase])
