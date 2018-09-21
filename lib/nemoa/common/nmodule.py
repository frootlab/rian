# -*- coding: utf-8 -*-
"""Collection of functions for module handling."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

from nemoa.types import (
    Any, Module, OptStr, OptModule, OptStrDictOfTestFuncs, StrList)

def curname(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of module.

    """
    # Check argument 'frame'
    if not isinstance(frame, int):
        raise TypeError(
            "argument 'frame' is required to be of type 'int'"
            f", not '{type(frame)}'")
    if frame > 0:
        raise ValueError(
            "argument 'frame' is required to be a negative number or zero")

    # Declare and initialize return value
    mname: str = ''

    # Traceback frames using 'inspect'
    cframe = inspect.currentframe()
    for i in range(abs(frame - 1)):
        if cframe is None:
            break
        cframe = cframe.f_back
    if cframe is not None:
        mname = cframe.f_globals['__name__']

    return mname

def caller(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack.
            Default: 0

    Returns:
        String with name of the caller.

    """
    # Check argument 'frame'
    if not isinstance(frame, int):
        raise TypeError(
            "argument 'frame' is required to be of type 'int'"
            f", not '{type(frame)}'")
    if frame > 0:
        raise ValueError(
            "argument 'frame' is required to be a negative number or zero")

    # Declare return value
    name: str

    # Get name of caller using 'inspect'
    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fbase = stack[3]
    name = '.'.join([mname, fbase])

    return name

def submodules(module: OptModule = None, recursive: bool = False) -> StrList:
    """Get list with submodule names.

    Args:
        module: Module instance to search for submodules
            default: Use current module which calls this function
        recursive: Search recursively within submodules
            default: Do not search recursively

    Returns:
        List with submodule names.

    """
    # Check argument 'module'
    module = module or inst(curname(-1))
    if not isinstance(module, Module):
        raise TypeError(
            "argument 'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module)}'")

    # Declare and initialize return value
    subs: StrList = []

    # Check if given module is not a package:
    # Since only packages contain submodules, any module without an path
    # attribute does not contain any submodules and an empy list is returned.
    if not hasattr(module, '__path__'):
        return subs

    # Iterate submodules within package by using 'pkgutil'
    import pkgutil
    prefix = getattr(module, '__name__') + '.'
    path = getattr(module, '__path__')
    for finder, name, ispkg in pkgutil.iter_modules(path):
        mname = prefix + name
        subs.append(mname)
        if ispkg and recursive:
            subs += submodules(inst(mname), recursive=True)

    return subs

def getsubmodule(name: str) -> OptModule:
    """Get instance from the name of a submodule of the current module.

    Args:
        name: Name of submodule of current module

    Returns:
        Module instance of submodule or None, if the current module does not
        contain the given module name.

    """
    # Check argument 'name'
    if not isinstance(name, str):
        raise TypeError(
            "first argument is required to be of type 'str'"
            f", not '{type(name)}'")

    # Get fully qualified module name
    prefix = curname(-1) + '.'
    mname = prefix + name

    return inst(mname)

def inst(name: str) -> OptModule:
    """Get module instance from a fully qualified module name.

    Args:
        name: Fully qualified name of module

    Returns:
        Module instance of the given module name or None, if the name does not
        point to a valid module.

    """
    # Check argument 'name'
    if not isinstance(name, str):
        raise TypeError(
            "first argument is required to be of type 'str'"
            f", not '{type(name)}'")

    # Declare and initialize return value
    module: OptModule = None

    # Try to import module using 'importlib'
    import importlib
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return module

    return module

def functions(
        module: OptModule = None, pattern: OptStr = None,
        rules: OptStrDictOfTestFuncs = None, **kwargs: Any) -> dict:
    """Get dictionary with functions and attributes.

    Args:
        module: Module instance to search for submodules
            default: Use current module, which called this function
        pattern: Only functions which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern
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
    # Check argument 'module'
    module = module or inst(curname(-1))
    if not isinstance(module, Module):
        raise TypeError(
            "argument 'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module)}'")

    from nemoa.common import ndict, nfunc

    # Get dictionary with function references using 'inspect'
    refs = {k: v for k, v in inspect.getmembers(module, inspect.isfunction)}

    # Filter references to functions, that match a given pattern
    if pattern:
        refs = ndict.select(refs, pattern=pattern)

    # Declare and initialize return value
    funcs: dict = {}

    # Add entries dictionary with function attributes
    prefix = module.__name__ + '.'
    rules = rules or {}
    for name, ref in refs.items():
        attr = ref.__dict__
        attr['about'] = attr.get('about', nfunc.about(ref))
        attr['name'] = attr.get('name', name)
        attr['reference'] = ref

        # filter entry by attributes using filter rules
        passed = True
        for key, val in kwargs.items():
            if not key in attr:
                passed = False
                break
            if key in rules:
                match = rules[key]
                if match(val, attr[key]):
                    continue
                passed = False
                break
            if val == attr[key]:
                continue
            passed = False
            break
        if not passed:
            continue

        # add item
        funcs[prefix + name] = attr

    return funcs

def search(
        module: OptModule = None, pattern: OptStr = None,
        groupby: OptStr = None, key: OptStr = None,
        val: OptStr = None, rules: OptStrDictOfTestFuncs = None,
        recursive: bool = True, **kwargs: Any) -> dict:
    """Recursively search for functions within submodules.

    Args:
        module: Module instance to search for functions
            Default: Use current module, which calles this function
        pattern: Only functions which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern
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
    module = module or inst(curname(-1))
    if not isinstance(module, Module):
        raise TypeError(
            "argument 'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module)}'")

    from nemoa.common import ndict

    # get list with submodules
    mnames = [module.__name__] + submodules(module, recursive=recursive)

    # create dictionary with function attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        m = inst(mname)
        if m is None:
            continue
        d = functions(m, pattern=pattern, rules=rules, **kwargs)

        # ignore functions if any required attribute is not available
        for name, attr in d.items():
            if key and not key in attr:
                continue
            if val and not val in attr:
                continue
            fd[name] = attr

    # rename key for returned dictionary
    if key:
        d = {}
        for name, attr in fd.items():
            if key not in attr:
                continue
            kval = attr[key]
            if kval in d:
                continue
            d[kval] = attr
        fd = d

    # group results
    if groupby:
        fd = ndict.groupby(fd, key=groupby)

    # set value for returned dictionary
    if val:
        if groupby:
            for gn, group in fd.items():
                for name, attr in group.items():
                    fd[name] = attr[val]
        else:
            for name, attr in fd.items():
                fd[name] = attr[val]

    return fd
