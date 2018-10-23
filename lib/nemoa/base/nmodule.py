# -*- coding: utf-8 -*-
"""Collection of functions for module handling.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

__all__ = [
    'get_curname', 'get_caller_ref', 'get_caller', 'get_root', 'get_parent',
    'get_attr', 'get_submodule', 'get_submodules', 'get_instance',
    'get_functions', 'crop_functions', 'search']

import importlib
import inspect
import pkgutil

from nemoa.base import check, ndict, dig
from nemoa.types import (
    Any, ClassInfo, Function, Module, OptStr, OptModule, OptStrDictOfTestFuncs,
    StrList)

def get_curname(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of module.

    """
    # Check type of 'frame'
    check.argtype('frame', frame, int)

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

def get_caller_ref() -> Module:
    """Get reference to callers module."""
    return inspect.getmodule(inspect.stack()[2][0])

def get_caller(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack. Default: 0

    Returns:
        String with name of the caller.

    """
    # Check type of 'frame'
    check.argtype('frame', frame, int)

    # Check value of 'frame'
    if frame > 0:
        raise ValueError(
            "'frame' is required to be a negative number or zero")

    # Get name of caller using inspect
    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fbase = stack[3]
    return '.'.join([mname, fbase])

def get_root(ref: OptModule = None) -> Module:
    """Get top level module.

    Args:
        ref: Module reference. By default a reference to the module of the
            caller is used.

    Returns:
        Module reference to the top level module of a given module reference or
        the current callers module.

    """
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Get name of the top level module
    rootname = ref.__name__.split('.', 1)[0]

    # Get reference to the top level module
    return importlib.import_module(rootname)

def get_parent(ref: OptModule = None) -> Module:
    """Get parent module.

    Args:
        ref: Module reference. By default a reference to the module of the
            caller is used.

    Returns:
        Module reference to the parent module of a given module reference or
        the current callers module.

    """
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Get name of the parent module
    name = ref.__name__.rsplit('.', 1)[0]

    # Get reference to the parent module
    return importlib.import_module(name)

def get_attr(name: str, default: Any = None, ref: OptModule = None) -> Any:
    """Get attribute of a module.

    Args:
        name: Name of attribute.
        default: Default value, which is returned, if the attribute does not
            exist.
        ref: Optional module reference. By default the current callers module
            is used.

    Returns:
        Value of attribute.

    """
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    return getattr(ref, name, default)

def get_submodule(name: str, ref: OptModule = None) -> OptModule:
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
    check.argtype('name', name, str)

    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Get instance of submodule
    return get_instance(ref.__name__ + '.' + name)

def get_submodules(
        ref: OptModule = None, recursive: bool = False) -> StrList:
    """Get list with submodule names.

    Args:
        module: Module reference to search for submodules. By default the
            module of the caller function is used.
        recursive: Boolean value which determines, if the search is performed
            recursively within the submodules. Default: False

    Returns:
        List with submodule names.

    """
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Check if given module is a package by the existence of a path attribute.
    # Otherwise the module does not contain any submodules and an empty list is
    # returned.
    subs: StrList = []
    if not hasattr(ref, '__path__'):
        return subs

    # Iterate submodules within package by using pkgutil
    prefix = ref.__name__ + '.'
    path = getattr(ref, '__path__')
    for finder, name, ispkg in pkgutil.iter_modules(path):
        fullname = prefix + name
        subs.append(fullname)
        if ispkg and recursive:
            sref = get_instance(fullname)
            subs += get_submodules(sref, recursive=True)

    return subs

def get_instance(name: str) -> OptModule:
    """Get reference to module instance from a fully qualified module name.

    Args:
        name: Fully qualified name of module

    Returns:
        Module reference of the given module name or None, if the name does not
        point to a valid module.

    """
    # Check type of 'name'
    check.argtype('name', name, str)

    # Try to import module using importlib
    module: OptModule = None
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return module

    return module

def get_functions(
        pattern: OptStr = None, ref: OptModule = None,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Get dictionary with functions and their attributes.

    Args:
        pattern: Only functions which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. If pattern is
            None, then all functions are returned. Default: None
        ref: Module reference in which functions are searched. By default the
            module of the caller function is used.
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
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    return dig.get_members(
        ref, classinfo=Function, pattern=pattern, rules=rules, **kwds)

def crop_functions(prefix: str, ref: OptModule = None) -> list:
    """Get list of cropped function names that satisfy a given prefix.

    Args:
        prefix: String
        ref: Module reference in which functions are searched. By default the
            module of the caller function is used.

    Returns:
        List of functions, that match a given prefix.

    """
    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Get functions dictionary
    funcs = get_functions(pattern=(prefix + '*'), ref=ref)

    # Create list of cropped function names
    i = len(prefix)
    return [each['name'][i:] for each in funcs.values()]

def search(
        pattern: OptStr = None, ref: OptModule = None,
        classinfo: ClassInfo = Function, key: OptStr = None, val: OptStr = None,
        groupby: OptStr = None, recursive: bool = True,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Recursively search for objects within submodules.

    Args:
        pattern: Only objects which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. If pattern is
            None, then all objects are returned. Default: None
        ref: Module reference in which objects are searched. If 'module' is
            None, then the module of the caller function is used. Default: None
        classinfo: Classinfo given as a class, a type or a tuple containing
            classes, types or other tuples. Only members, which are ether an
            instance or a subclass of classinfo are returned. By default all
            types are allowed.
        key: Name of function attribute which is used as the key for the
            returned dictionary. If 'key' is None, then the fully qualified
            function names are used as keys. Default: None
        val: Name of function attribute which is used as the value for the
            returned dictionary. If 'val' is None, then all attributes of the
            respective objects are returned. Default: None
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
            is given, then only objects are returned, which have the attribute
            'tags' and the value of the attribute equals ['test']. If, however,
            the filter rule of the above example is given, then any function,
            with attribute 'tags' and a corresponding tag list, that comprises
            'test' is returned.

    Returns:
        Dictionary with function information as specified in the arguments
        'key' and 'val'.

    """
    # Check type of 'pattern'
    check.argtype('pattern', pattern, (str, type(None)))

    # Set default value of 'ref' to module of caller
    ref = ref or get_caller_ref()

    # Get list with submodules
    mnames = [ref.__name__] + get_submodules(ref, recursive=recursive)

    # Create dictionary with member attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        minst = get_instance(mname)
        if minst is None:
            continue
        d = dig.get_members(
            minst, classinfo=classinfo, pattern=pattern, rules=rules, **kwds)

        # Ignore members if any required attribute is not available
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
