# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

def getfunctions(modulename, prefix = '', removeprefix = True,
    attribute = 'reference'):
    functions = dict(inspect.getmembers(modulename, inspect.isfunction))
    if prefix:
        for key in functions.keys():
            if key.startswith(prefix) and not key == prefix:
                if removeprefix:
                    functions[key[len(prefix):]] = functions[key]
                    del functions[key]
                    continue
            del functions[key]
    if attribute == 'reference': return functions
    if attribute == 'about':
        for key in functions.keys():
            if isinstance(functions[key].__doc__, basestring):
                functions[key] = \
                    functions[key].__doc__.split('\n', 1)[0].strip(' .')
            else:
                functions[key] = ''
        return functions
    return False

def getmethods(classname, prefix = '', removeprefix = True,
    attribute = None):

    # create dictionary with references
    methods = dict(inspect.getmembers(classname, inspect.ismethod))
    if prefix:
        for name in methods.keys():
            if name.startswith(prefix) and not name == prefix:
                if removeprefix:
                    methods[name[len(prefix):]] = methods[name]
                    del methods[name]
                continue
            del methods[name]
    if attribute == 'reference': return methods

    # create dictionary with all attributes and references
    methoddict = {}
    for name in methods.keys():
        methoddict[name] = { 'reference': methods[name], 'about': '' }

        # copy method attributes to dictionary
        for attr in methods[name].__dict__:
            methoddict[name][attr] = methods[name].__dict__[attr]

        # copy first line of docstring to dictionary
        if isinstance(methods[name].__doc__, basestring):
            methoddict[name]['about'] = \
                methods[name].__doc__.split('\n', 1)[0].strip(' .')
    if attribute == None: return methoddict

    # create dictionary only with given attribute
    methoddictattrib = {}
    for name in methoddict.keys():
        if not attribute in methoddict[name]: continue
        if not name in methoddictattrib.keys():
            methoddictattrib[name] = methoddict[name][attribute]
            continue
        if not isinstance(methoddictattrib[name], list):
            methoddictattrib[name] = [methoddictattrib[name]]
        methoddictattrib[name].append(methoddict[name][attribute])
    return methoddictattrib
