# -*- coding: utf-8 -*-
"""Current module accessor functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from nemoa.base import entity, check
from nemoa.types import Any, Module, OptModule, Function

def get_caller_module() -> Module:
    """Get reference to callers module."""
    name = get_module_name(-2)
    if name:
        ref = entity.get_module(name)
        if isinstance(ref, Module):
            return ref
    raise ModuleNotFoundError("could not detect module of caller")

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
    name = get_module_name(-1)
    if name:
        ref = entity.get_module(name)
        if isinstance(ref, Module):
            return ref
    raise ModuleNotFoundError("could not detect current module")

def get_submodule(name: str, ref: OptModule = None) -> OptModule:
    """Get instance from the name of a submodule of the current module.

    Args:
        name: Name of submodule of given module.
        ref: Module reference. By default the current callers module is used.

    Returns:
        Module reference of submodule or None, if the current module does not
        contain the given module name.

    """
    # Check type of 'name'
    check.has_type("argument 'name'", name, str)

    # Set default module to callers module
    ref = ref or get_caller_module()

    # Get instance of submodule
    return entity.get_module(ref.__name__ + '.' + name)

def get_parent(ref: OptModule = None) -> Module:
    """Get parent module.

    Args:
        ref: Module reference. By default the current callers module is used.

    Returns:
        Module reference to the parent module of the current callers module.

    """
    # Set default module to callers module
    ref = ref or get_caller_module()

    # Get name of the parent module
    name = ref.__name__.rsplit('.', 1)[0]

    # Get reference to the parent module
    pref = entity.get_module(name)
    if not isinstance(pref, Module):
        raise ModuleNotFoundError(f"module '{name}' does not exist")
    return pref

def get_root(ref: OptModule = None) -> Module:
    """Get top level module.

    Args:
        ref: Module reference. By default the current callers module is used.

    Returns:
        Module reference to the top level module of the current callers module.

    """
    # Set default module to callers module
    ref = ref or get_caller_module()

    # Get name of the top level module
    name = ref.__name__.split('.', 1)[0]

    # Get reference to the top level module
    tlref = entity.get_module(name)
    if not isinstance(tlref, Module):
        raise ModuleNotFoundError(f"module '{name}' does not exist")
    return tlref

def get_attr(name: str, default: Any = None, ref: OptModule = None) -> Any:
    """Get an attribute of current module.

    Args:
        name: Name of attribute.
        default: Default value, which is returned, if the attribute does not
            exist.
        ref: Module reference. By default the current callers module is used.

    Returns:
        Value of attribute.

    """
    # Set default module to callers module
    ref = ref or get_caller_module()

    # Get attribute
    return getattr(ref, name, default)

def has_attr(name: str) -> bool:
    """Determine if current module has an attribute of given name.

    Args:
        name: Name of callable attribute

    Returns:
        Result of call.
    """
    return hasattr(get_caller_module(), name)

def call_attr(name: str, *args: Any, **kwds: Any) -> Any:
    """Call an attribute of current module with given arguments.

    Args:
        name: Name of callable attribute
        *args: Arbitrary arguments, that are passed to the call
        *kwds: Arbitrary keyword arguments, that are passes to the call, if
            supported by the member attribute.

    Returns:
        Result of call.

    """
    return entity.call_attr(get_caller_module(), name, *args, **kwds)

def crop_functions(prefix: str, ref: OptModule = None) -> list:
    """Get list of cropped function names that satisfy a given prefix.

    Args:
        prefix: String
        ref: Module reference. By default the current callers module is used.

    Returns:
        List of functions, that match a given prefix.

    """
    # Set default module to callers module
    ref = ref or get_caller_module()

    # Get functions of current callers module
    funcs = entity.get_members_dict(
        ref, classinfo=Function, pattern=(prefix + '*'))

    # Create list of cropped function names
    i = len(prefix)
    return [each['name'][i:] for each in funcs.values()]
