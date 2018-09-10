# -*- coding: utf-8 -*-
"""Collection of functions for module handling."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import types
from typing import Any, Dict, Optional

Function = types.FunctionType
Module = types.ModuleType

def curname(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack.
            default: 0

    Returns:
        String with name of module.

    """

    if not isinstance(frame, int):
        raise TypeError(f"frame requires type 'int', not '{type(frame)}'")
    if frame > 0:
        raise ValueError("frame is required to be zero or negative")

    import inspect

    caller = inspect.currentframe()

    for i in range(abs(frame - 1)):
        if caller is None: break
        caller = caller.f_back

    if caller is None: return ''
    mname = caller.f_globals['__name__']

    return mname

def caller(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack.
            default: 0

    Returns:
        String with name of the caller.

    """

    if not isinstance(frame, int):
        raise TypeError(f"frame requires type 'int', not '{type(frame)}'")
    if frame > 0:
        raise ValueError("frame is required to be zero or negative")

    import inspect

    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fname = stack[3]

    return '.'.join([mname, fname])

def submodules(minst: Optional[Module] = None, recursive: bool = False) -> list:
    """Get list with submodule names.

    Args:
        minst: Module instance to search for submodules
            default: Use current module which calls this function
        recursive: Search recursively within submodules
            default: Do not search recursively

    Returns:
        List with submodule names.

    """

    if minst is None: minst = get_module(curname(-1))
    elif not isinstance(minst, Module):
        raise TypeError("argument 'minst' is required to be a module instance")

    # check if module is a package or a file
    if not hasattr(minst, '__path__'): return []

    import pkgutil

    mpref = minst.__name__ + '.'
    mpath = minst.__path__

    mlist = []
    for path, name, ispkg in pkgutil.iter_modules(mpath):
        mlist += [mpref + name]
        if not ispkg or not recursive: continue
        mlist += submodules(get_module(mpref + name), recursive = True)

    return mlist

def get_submodule(s: str) -> Optional[Module]:
    """Get module instance, by name of current submodule."""

    return get_module('.'.join([curname(-1), s]))

def get_module(s: str) -> Optional[Module]:
    """Get module instance for a given qualified module name."""

    import importlib

    try: minst = importlib.import_module(s)
    except ModuleNotFoundError: return None

    return minst

def functions(minst: Optional[Module] = None, filter: Optional[str] = None,
    rules: Optional[Dict[str, Function]] = None, **kwargs: Any) -> dict:
    """Get dictionary with functions and attributes.

    Args:
        minst: Module instance to search for submodules
            default: Use current module, which called this function
        filter: Only functions which names satisfy the wildcard pattern given
            by 'filter' are returned. The format of the wildcard pattern
            is described in the standard library module 'fnmatch' [1]
        rules:
            default: {}
        **kwargs:

    Returns:
        Dictionary with fully qualified function names as keys and attribute
        dictinaries as values.

    References:
        [1] https://docs.python.org/3/library/fnmatch.html

    """

    if minst is None: minst = get_module(curname(-1))
    elif isinstance(minst, Module): pass
    else: raise TypeError("argument 'minst' is requires type 'module', "
        f"not type '{type(minst)}'")

    import inspect
    from nemoa.common import ndict, nfunc

    # get dictionary with function names and references from inspect
    fd = {k: v for k, v in inspect.getmembers(minst, inspect.isfunction)}

    # filter dictionary to functions names, that match given pattern
    if filter: fd = ndict.filter(fd, pattern = filter)

    # create dictionary with function attributes
    fc = {}
    pref = minst.__name__ + '.'
    rules = rules or {}
    for name, ref in fd.items():
        attr = ref.__dict__
        attr['reference'] = ref
        if not 'about' in attr: attr['about'] = nfunc.about(ref)
        if not 'name' in attr: attr['name'] = name

        # filter entry by attributes
        passed = True
        for key, val in kwargs.items():
            if not key in attr:
                passed = False
                break
            if key in rules:
                match = rules[key]
                if match(val, attr[key]): continue
                passed = False
                break
            if val == attr[key]: continue
            passed = False
            break
        if not passed: continue

        # add item
        fc[pref + name] = attr

    return fc

def search(minst: Optional[Module] = None,
    filter: Optional[str] = None, groupby: Optional[str] = None,
    key: Optional[str] = None, val: Optional[str] = None,
    rules: Optional[Dict[str, Function]] = None, recursive: bool = True,
    **kwargs: Any) -> dict:
    """Recursively search for functions within submodules.

    Args:
        minst: Module instance to search for functions
            Default: Use current module, which calles this function
        filter: Only functions which names satisfy the wildcard pattern given
            by 'filter' are returned. The format of the wildcard pattern
            is described in the standard library module 'fnmatch' [1]
        groupby: Name of function attribute which is used to group the results.
            If 'groupby' is None, then the results are not grouped.
            Default: None
        key: Name of function attribute which is used as the key for the
            returned dictionary. If 'key' is None, then the fully qualified
            function names are used as keys. Default: None
        val: Name of function attribute which is used as the value for the
            returned dictionary. If 'val' is None, then all attributes of the
            respective functions are returned. Default: None
        rules: Default: None
        recursive: Boolean value which determines if the search is recursively
            within submodules. Defaut: True
        **kwargs: Attributes, which values are testet by using the filter rules.

    Returns:
        Dictionary with function information as specified in the arguments
        'key' and 'val'.

    References:
        [1] https://docs.python.org/3/library/fnmatch.html

    """

    if minst is None: minst = get_module(curname(-1))
    elif isinstance(minst, Module): pass
    else: raise TypeError("first argument is required to be a module instance")

    from nemoa.common import ndict

    # get list with submodules
    mnames = [minst.__name__] + submodules(minst, recursive = recursive)

    # create dictionary with function attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        m = get_module(mname)
        if m is None: continue
        d = functions(m, filter = filter, rules = rules, **kwargs)

        # ignore functions if any required attribute is not available
        for name, attr in d.items():
            if key and not key in attr: continue
            if val and not val in attr: continue
            fd[name] = attr

    # rename key for returned dictionary
    if key:
        d = {}
        for name, attr in fd.items():
            if key not in attr: continue
            id = attr[key]
            if id in d: continue
            d[id] = attr
        fd = d

    # group results
    if groupby: fd = ndict.groupby(fd, key = groupby)

    # set value for returned dictionary
    if val:
        if groupby:
            for gn, group in fd.items():
                for name, attr in group.items(): fd[name] = attr[val]
        else:
            for name, attr in fd.items(): fd[name] = attr[val]

    return fd
