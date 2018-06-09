# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

def getfunctions(modulename, prefix = '', removeprefix = True,
    attribute = 'reference'):
    """ """

    functions = dict(inspect.getmembers(modulename, inspect.isfunction))
    if prefix:
        for key in list(functions.keys()):
            if key.startswith(prefix) and not key == prefix:
                if removeprefix:
                    functions[key[len(prefix):]] = functions[key]
                    del functions[key]
                    continue
            del functions[key]
    if attribute == 'reference': return functions
    if attribute == 'about':
        for key in list(functions.keys()):
            if isinstance(functions[key].__doc__, str):
                functions[key] = \
                    functions[key].__doc__.split('\n', 1)[0].strip(' .')
            else:
                functions[key] = ''
        return functions
    return False

def getmethods(instance, attribute = None, grouping = None,
    prefix = '', removeprefix = True, renamekey = None):
    """Get the methods of an instance.

    Args:
        instance: instance of arbitrary class
        prefix (string): only methods with given prefix are returned.
        removeprefix (bool): remove prefix in dictionary keys if True.
        renamekey (string):
        attribute (string):
        grouping (string):

    Returns:
        Dictionary containing the methods of an instance including
        their attributes.

    """

    # get references from module inspection and filter prefix
    methods = dict(inspect.getmembers(instance, inspect.ismethod))
    if prefix:
        for name in list(methods.keys()):
            if not name.startswith(prefix) or name == prefix:
                del methods[name]
                continue
            if removeprefix:
                methods[name[len(prefix):]] = methods.pop(name)
    if not grouping and not renamekey and attribute == 'reference':
        return methods

    # get attributes from references
    methoddict = {}
    for name, method in methods.items():
        methoddict[name] = { 'reference': method, 'about': '' }

        # copy method attributes and docstring to dictionary
        for attr in method.__dict__:
            methoddict[name][attr] = method.__dict__[attr]
        if isinstance(method.__doc__, str):
            methoddict[name]['about'] = \
                method.__doc__.split('\n', 1)[0].strip(' .')

        # filter methods by necessary attributes
        if renamekey and not renamekey in methoddict[name]:
            del methoddict[name]
        elif attribute and not attribute in methoddict[name]:
            del methoddict[name]
        elif grouping and not grouping in methoddict[name]:
            del methoddict[name]
    methods = methoddict

    # (optional) group methods, rename key and reduce to attribute
    if grouping:
        grouped = {}
        for ukey, udata in methods.items():
            group = udata[grouping]
            key = udata[renamekey] if renamekey else ukey
            if not group in grouped: grouped[group] = {}
            if key in grouped[group]: continue
            if attribute: grouped[group][key] = udata[attribute]
            else: grouped[group][key] = udata
        methods = grouped
    elif renamekey:
        renamend = {}
        for ukey, udata in methods.items():
            key = udata[renamekey]
            if key in renamend: continue
            if attribute: renamend[key] = udata[attribute]
            else: renamend[key] = udata
        methods = renamend

    return methods
