# -*- coding: utf-8 -*-
"""Current module accessor functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from nemoa.base import assess, check
from nemoa.types import Any, Module, OptModule

def get_caller_module() -> Module:
    """Get reference to callers module."""
    return inspect.getmodule(inspect.stack()[2][0])

def get_caller_name(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of the caller.

    """
    # Check type of 'frame'
    check.has_type("argument 'frame'", frame, int)

    # Check value of 'frame'
    if frame > 0:
        raise ValueError(
            "'frame' is required to be a negative number or zero")

    # Get name of caller using inspect
    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fbase = stack[3]
    return '.'.join([mname, fbase])

def get_module_name(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of module.

    """
    # Check type of 'frame'
    check.has_type("argument 'frame'", frame, int)

    # Check value of 'frame'
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

def get_module() -> Module:
    """Get reference to current module."""
    return inspect.getmodule(inspect.stack()[1][0])

def get_submodule(name: str) -> OptModule:
    """Get instance from the name of a submodule of the current module.

    Args:
        name: Name of submodule of given module.
        ref: Optional module reference. By default the current callers module
            is used.

    Returns:
        Module reference of submodule or None, if the current module does not
        contain the given module name.

    """
    # Check type of 'name'
    check.has_type("argument 'name'", name, str)

    # Get module of caller
    ref = get_caller_module()

    # Get instance of submodule
    return assess.get_module(ref.__name__ + '.' + name)

def get_parent() -> Module:
    """Get parent module.

    Returns:
        Module reference to the parent module of the callers module.

    """
    # Get name of the parent module
    name = get_caller_module().__name__.rsplit('.', 1)[0]

    # Get reference to the parent module
    ref = assess.get_module(name)
    if not isinstance(ref, Module):
        raise ModuleNotFoundError(f"module '{name}' does not exist")
    return ref

def get_attr(name: str, default: Any = None) -> Any:
    """Get attribute of a module.

    Args:
        name: Name of attribute.
        default: Default value, which is returned, if the attribute does not
            exist.

    Returns:
        Value of attribute.

    """
    return getattr(get_caller_module(), name, default)
