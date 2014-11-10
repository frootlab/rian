# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

def getfunctions(modulename, prefix = '', removeprefix = True,
    values = 'reference'):
    functions = dict(inspect.getmembers(modulename, inspect.isfunction))
    if prefix:
        for key in functions.keys():
            if key.startswith(prefix) and not key == prefix:
                if removeprefix:
                    functions[key[len(prefix):]] = functions[key]
                    del functions[key]
                    continue
            del functions[key]
    if values == 'reference': return functions
    if values == 'about':
        for key in functions.keys():
            if isinstance(functions[key].__doc__, basestring):
                functions[key] = \
                    functions[key].__doc__.split('\n', 1)[0].strip(' .')
            else:
                functions[key] = ''
        return functions
    return False

def getmethods(classname, prefix = '', removeprefix = True,
    values = 'reference'):
    methods = dict(inspect.getmembers(classname, inspect.ismethod))
    if prefix:
        for key in methods.keys():
            if key.startswith(prefix) and not key == prefix:
                if removeprefix:
                    methods[key[len(prefix):]] = methods[key]
                    del methods[key]
                continue
            del methods[key]
    if values == 'reference': return methods
    if values == 'about':
        for key in methods.keys():
            if isinstance(methods[key].__doc__, basestring):
                methods[key] = \
                    methods[key].__doc__.split('\n', 1)[0].strip(' .')
            else:
                methods[key] = ''
        return methods
    return False
