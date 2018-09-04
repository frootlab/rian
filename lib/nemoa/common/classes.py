# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Optional

def hasbase(obj: object, base: str) -> bool:
    """Return true if the class instance has the given base.

    Args:
        obj: Class instance
        base: Class name of base class

    Returns:
        True if the given object has the named base as base

    """

    if not hasattr(obj, '__class__'):
        raise TypeError("obj is required to be a class instance")

    bases = [o.__name__ for o in obj.__class__.__mro__]
    return base in bases

def methods(obj: object, attribute: Optional[str] = None,
    grouping: Optional[str] = None, prefix: str = '', removeprefix: bool = True,
    renamekey: Optional[str] = None) -> dict:
    """Get methods from a given class instance.

    Args:
        obj: Class instance
        prefix: only methods with given prefix are returned.
        removeprefix: remove prefix in dictionary keys if True.
        renamekey:
        attribute:
        grouping:

    Returns:
        Dictionary containing all methods of a given class instance, that
        pass the given filter.

    """

    import inspect

    # get references from module inspection and filter prefix
    methods = dict(inspect.getmembers(obj, inspect.ismethod))
    if prefix:
        for name in list(methods.keys()):
            if not name.startswith(prefix) or name == prefix:
                del methods[name]
                continue
            if removeprefix:
                methods[name[len(prefix):]] = methods.pop(name)
    if not grouping and not renamekey and attribute == 'reference':
        return methods

    # get attributes from decorators
    methoddict = {}
    for name, method in methods.items():
        methoddict[name] = { 'reference': method, 'about': '' }

        # copy method attributes and docstring to dictionary
        for attr in method.__dict__:
            methoddict[name][attr] = method.__dict__[attr]
        if isinstance(method.__doc__, str):
            methoddict[name]['about'] = \
                method.__doc__.split('\n', 1)[0].strip(' .')

        # filter methods by required attributes
        if renamekey and not renamekey in methoddict[name]:
            del methoddict[name]
        elif attribute and not attribute in methoddict[name]:
            del methoddict[name]
        elif grouping and not grouping in methoddict[name]:
            del methoddict[name]
    methods = methoddict

    # (optional) group methods, rename key and reduce to attribute
    if grouping:
        groups = {}
        for ukey, udata in methods.items():
            group = udata[grouping]
            key = udata[renamekey] if renamekey else ukey
            if group not in groups: groups[group] = {}
            if key in groups[group]: continue
            if attribute: groups[group][key] = udata[attribute]
            else: groups[group][key] = udata
        methods = groups
    elif renamekey:
        renamend = {}
        for ukey, udata in methods.items():
            key = udata[renamekey]
            if key in renamend: continue
            if attribute: renamend[key] = udata[attribute]
            else: renamend[key] = udata
        methods = renamend

    return methods
