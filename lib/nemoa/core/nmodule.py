# -*- coding: utf-8 -*-
"""Collection of functions for module handling.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import importlib
import inspect
import pkgutil

from nemoa.core import ndict, nobject
from nemoa.types import (
    Any, Function, Module, OptStr, OptModule, OptStrDictOfTestFuncs, StrList)

def curname(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of module.

    """
    # Check type of 'frame'
    if not isinstance(frame, int):
        raise TypeError(
            "'frame' is required to be of type 'int'"
            f", not '{type(frame).__name__}'")

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

def caller(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of the caller.

    """
    # Check type of 'frame'
    if not isinstance(frame, int):
        raise TypeError(
            "'frame' is required to be of type 'int'"
            f", not '{type(frame).__name__}'")

    # Check value of 'frame'
    if frame > 0:
        raise ValueError(
            "'frame' is required to be a negative number or zero")

    # Get name of caller using inspect
    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fbase = stack[3]
    return '.'.join([mname, fbase])

def root(module: OptModule = None) -> Module:
    """Get top level module.

    Args:
        module: Module reference. By default a reference to the module of the
            caller is used.

    Returns:
        Module reference to the top level module of a given module reference or
        the current callers module.

    """
    # Set default value of 'module' to current module
    module = module or inst(curname(-1))

    # Check type of 'module'
    if not isinstance(module, Module):
        raise TypeError(
            "'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module).__name__}'")

    # Get name of top level module
    name = module.__name__.split('.')[0]

    # Get reference to top level module
    return importlib.import_module(name)

def submodules(module: OptModule = None, recursive: bool = False) -> StrList:
    """Get list with submodule names.

    Args:
        module: Module reference to search for submodules. By default the
            module of the caller function is used.
        recursive: Boolean value which determines, if the search is performed
            recursively within the submodules. Default: False

    Returns:
        List with submodule names.

    """
    # Set default value of 'module' to current module
    module = module or inst(curname(-1))

    # Check type of 'module'
    if not isinstance(module, Module):
        raise TypeError(
            "'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module).__name__}'")

    # Check if given module is not a package:
    # Since only packages contain submodules, any module without an path
    # attribute does not contain any submodules and an empy list is returned.
    subs: StrList = []
    if not hasattr(module, '__path__'):
        return subs

    # Iterate submodules within package by using 'pkgutil'
    prefix = getattr(module, '__name__') + '.'
    path = getattr(module, '__path__')
    for finder, name, ispkg in pkgutil.iter_modules(path):
        mname = prefix + name
        subs.append(mname)
        if ispkg and recursive:
            subs += submodules(inst(mname), recursive=True)

    return subs

def get_submodule(name: str) -> OptModule:
    """Get instance from the name of a submodule of the current module.

    Args:
        name: Name of submodule of current module.

    Returns:
        Module reference of submodule or None, if the current module does not
        contain the given module name.

    """
    # Check type of 'name'
    if not isinstance(name, str):
        raise TypeError(
            "first argument 'name' is required to be of type 'str'"
            f", not '{type(name).__name__}'")

    # Get fully qualified module name
    prefix = curname(-1) + '.'
    mname = prefix + name

    return inst(mname)

def inst(name: str) -> OptModule:
    """Get reference to module instance from a fully qualified module name.

    Args:
        name: Fully qualified name of module

    Returns:
        Module reference of the given module name or None, if the name does not
        point to a valid module.

    """
    # Check type of 'name'
    if not isinstance(name, str):
        raise TypeError(
            "first argument 'name' is required to be of type 'str'"
            f", not '{type(name).__name__}'")

    # Try to import module using importlib
    module: OptModule = None
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return module

    return module

def get_functions(
        module: OptModule = None, pattern: OptStr = None,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Get dictionary with functions and their attributes.

    Args:
        module: Module reference in which functions are searched. If 'module' is
            None, then the module of the caller function is used. Default: None
        pattern: Only functions which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. If pattern is
            None, then all functions are returned. Default: None
        rules: Dictionary with individual filter rules, used by the attribute
            filter. The form is {<attribute>: <lambda>, ...}, where: <attribute>
            is a string with the attribute name and <lambda> is a boolean valued
            lambda function, which specifies the comparison of the attribute
            value against the argument value. Example: {'tags': lambda arg,
            attr: set(arg) <= set(attr)}. By default any attribute, which is not
            in the filter rules is compared to the argument value by equality.
        **kwds: Keyword arguments, that define the attribute filter for the
            returned dictionary. For example if the argument "tags = ['test']"
            is given, then only functions are returned, which have the attribute
            'tags' and the value of the attribute equals ['test']. If, however,
            the filter rule of the above example is given, then any function,
            with attribute 'tags' and a corresponding tag list, that comprises
            'test' is returned.

    Returns:
        Dictionary with fully qualified function names as keys and attribute
        dictinaries as values.

    """
    # Set default value of 'module' to current module
    module = module or inst(curname(-1))

    # Check type of 'module'
    if not isinstance(module, Module):
        raise TypeError(
            "'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module).__name__}'")

    return nobject.members(
        module, base=Function, pattern=pattern, rules=rules, **kwds)

def search(
        module: OptModule = None, pattern: OptStr = None, base: type = Function,
        key: OptStr = None, val: OptStr = None, groupby: OptStr = None,
        recursive: bool = True, rules: OptStrDictOfTestFuncs = None,
        **kwds: Any) -> dict:
    """Recursively search for functions within submodules.

    Args:
        module: Module reference in which functions are searched. If 'module' is
            None, then the module of the caller function is used. Default: None
        pattern: Only functions which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. If pattern is
            None, then all functions are returned. Default: None
        key: Name of function attribute which is used as the key for the
            returned dictionary. If 'key' is None, then the fully qualified
            function names are used as keys. Default: None
        val: Name of function attribute which is used as the value for the
            returned dictionary. If 'val' is None, then all attributes of the
            respective functions are returned. Default: None
        groupby: Name of function attribute which is used to group the results.
            If 'groupby' is None, then the results are not grouped. Default:
            None
        recursive: Boolean value which determines if the search is performed
            recursively within all submodules. Default: True
        rules: Dictionary with individual filter rules, used by the attribute
            filter. The form is {<attribute>: <lambda>, ...}, where: <attribute>
            is a string with the attribute name and <lambda> is a boolean valued
            lambda function, which specifies the comparison of the attribute
            value against the argument value. Example: {'tags': lambda arg,
            attr: set(arg) <= set(attr)} By default any attribute, which is not
            in the filter rules is compared to the argument value by equality.
        **kwds: Keyword arguments, that define the attribute filter for the
            returned dictionary. For example if the argument "tags = ['test']"
            is given, then only functions are returned, which have the attribute
            'tags' and the value of the attribute equals ['test']. If, however,
            the filter rule of the above example is given, then any function,
            with attribute 'tags' and a corresponding tag list, that comprises
            'test' is returned.

    Returns:
        Dictionary with function information as specified in the arguments
        'key' and 'val'.

    """
    # Set default value of 'module' to current module
    module = module or inst(curname(-1))

    # Check type of 'module'
    if not isinstance(module, Module):
        raise TypeError(
            "'module' is required to be of type 'ModuleType' or None"
            f", not '{type(module).__name__}'")

    # Get list with submodules
    mnames = [module.__name__] + submodules(module, recursive=recursive)

    # Create dictionary with function attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        m = inst(mname)
        if m is None:
            continue
        #d = get_functions(m, pattern=pattern, rules=rules, **kwds)
        d = nobject.members(
            m, base=base, pattern=pattern, rules=rules, **kwds)

        # Ignore functions if any required attribute is not available
        for name, attr in d.items():
            if key and not key in attr:
                continue
            if val and not val in attr:
                continue
            fd[name] = attr

    # Rename key for returned dictionary
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

    # Group results
    if groupby:
        fd = ndict.groupby(fd, key=groupby)

    # Set value for returned dictionary
    if val:
        if groupby:
            for gn, group in fd.items():
                for name, attr in group.items():
                    fd[name] = attr[val]
        else:
            for name, attr in fd.items():
                fd[name] = attr[val]

    return fd
