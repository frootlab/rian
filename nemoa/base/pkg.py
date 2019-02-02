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
"""Package tree helper functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import importlib
import pkgutil
from nemoa.base import check, otree, mapping, stack
from nemoa.types import Any, OptStr, StrList, OptDictOfKeyOps, ClassInfo
from nemoa.types import Optional, Module, Function

OptModule = Optional[Module]

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
    return otree.call_attr(stack.get_caller_module(), name, *args, **kwds)

def crop_functions(prefix: str, module: OptModule = None) -> list:
    """Get list of cropped function names that satisfy a given prefix.

    Args:
        prefix: String conatining the initial prefix of the returned functions
        module: Module reference. By default the current callers module is used.

    Returns:
        List of functions, that match a given prefix.

    """
    # Set default values
    module = module or stack.get_caller_module()

    # Get functions of current callers module
    pattern = prefix + '*'
    funcs = otree.get_members_dict(module, classinfo=Function, pattern=pattern)

    # Create list of cropped function names
    offset = len(prefix)
    return [each['name'][offset:] for each in funcs.values()]

def get_module(name: OptStr = None, errors: bool = True) -> OptModule:
    """Get reference to a module instance.

    Args:
        name: Optional name of module- If provided, the name is required to be
            a fully qualified name. By default a refrence to the module of the
            current caller is returned.
        errors: Boolean value which determines if an error is raised, if the
            module could not be found. By default errors are raised.

    Returns:
        Module reference or None, if the name does not point to a valid module.

    """
    # Set default values
    name = name or stack.get_caller_module_name(-1)

    # Try to import a module with importlib
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        if errors:
            raise
        return None
    except ImportError:
        if errors:
            raise
        return None

def get_submodule(name: str, parent: OptModule = None) -> OptModule:
    """Get instance from the name of a submodule of the current module.

    Args:
        name: Name of submodule of given module.
        parent: Optional reference to module, which has to be searched for
            submodules. By default the current callers module is used.

    Returns:
        Module reference of submodule or None, if the current module does not
        contain the given module name.

    """
    # Set default values
    parent = parent or stack.get_caller_module()

    # Get reference to submodule
    return get_module(parent.__name__ + '.' + name)

def get_submodules(
        parent: OptModule = None, recursive: bool = False) -> StrList:
    """Get list with submodule names.

    Args:
        parent: Optional reference to module, which has to be searched for
            submodules. By default the current callers module is used.
        recursive: Boolean value which determines, if the search is performed
            recursively within all submodules. By default the returned list only
            comprises immediate submodules.

    Returns:
        List with fully qualified names of submodules.

    """
    # Set default values
    parent = parent or stack.get_caller_module()

    # Check if given module is a package by the existence of a path attribute.
    # Otherwise the module does not contain any submodules and an empty list is
    # returned.
    if not hasattr(parent, '__path__'):
        return []

    # Iterate submodules within package by using pkgutil
    children: StrList = []
    path = parent.__path__ # type: ignore
    for finder, basename, ispkg in pkgutil.iter_modules(path):
        name = '.'.join([parent.__name__, basename])
        children.append(name)
        if ispkg and recursive:
            child = get_module(name)
            if isinstance(child, Module):
                children += get_submodules(parent=child, recursive=True)

    return children

def get_parent(module: OptModule = None) -> Module:
    """Get parent module.

    Args:
        module: Optional reference to module. By default the current callers
            module is used.

    Returns:
        Module reference to the parent module of the current callers module.

    """
    # Set default values
    module = module or stack.get_caller_module()

    # Get name of the parent module
    name = module.__name__.rsplit('.', 1)[0]

    # Get reference to the parent module
    parent = get_module(name)
    if not isinstance(parent, Module):
        raise ModuleNotFoundError(f"module '{name}' does not exist")
    return parent

def get_root(module: OptModule = None) -> Module:
    """Get top level module.

    Args:
        module: Optional reference to module. By default the current callers
            module is used.

    Returns:
        Module reference to the top level module of the current callers module.

    """
    # Set default values
    module = module or stack.get_caller_module()

    # Get name of the root module
    name = module.__name__.split('.', 1)[0]

    # Get reference to the root module
    root = get_module(name)
    if not isinstance(root, Module):
        raise ModuleNotFoundError(f"module '{name}' does not exist")
    return root

def get_attr(name: str, default: Any = None, module: OptModule = None) -> Any:
    """Get an attribute of current module.

    Args:
        name: Name of attribute.
        default: Default value, which is returned, if the attribute does not
            exist.
        module: Optional reference to module, which is used to search for the
            given attribute. By default the current callers module is used.

    Returns:
        Value of attribute.

    """
    # Set default values
    module = module or stack.get_caller_module()

    # Get attribute
    return getattr(module, name, default)

def has_attr(name: str, module: OptModule = None) -> bool:
    """Determine if a module has an attribute of given name.

    Args:
        name: Name of attribute
        module: Optional reference to module, which is used to search for the
            given attribute. By default the current callers module is used.

    Returns:
        Result of call.

    """
    # Set default values
    module = module or stack.get_caller_module()

    # Check Arguments
    check.has_type("'name'", name, str)
    check.has_type("'module'", module, Module)

    return hasattr(module, name)

def search(
        module: OptModule = None, pattern: OptStr = None,
        classinfo: ClassInfo = Function, key: OptStr = None, val: OptStr = None,
        groupby: OptStr = None, recursive: bool = True,
        rules: OptDictOfKeyOps = None, errors: bool = False,
        **kwds: Any) -> dict:
    """Recursively search for objects within submodules.

    Args:
        module: Optional reference to module, which is used to search objects.
            By default the current callers module is used.
        pattern: Only objects which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module :py:mod:`fnmatch`. If
            pattern is None, then all objects are returned. Default: None
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
        errors: Boolean value which determines if an error is raised, if the
            module could not be found. By default errors are not raised.
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
    # Set default values
    module = module or stack.get_caller_module()

    # Check argument types
    check.has_type("'module'", module, Module)
    check.has_opt_type("'pattern'", pattern, str)

    # Get list with module names, including the given and the submodules
    submodules = get_submodules(parent=module, recursive=recursive)
    mnames = [module.__name__] + submodules

    # Create dictionary with member attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        minst = get_module(mname, errors=errors)
        if minst is None:
            continue
        d = otree.get_members_dict(
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
        fd = mapping.groupby(fd, key=groupby)

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
