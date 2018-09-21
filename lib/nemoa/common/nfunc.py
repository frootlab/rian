# -*- coding: utf-8 -*-
"""Collection of functions for function handling."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.types import AnyFunc, StrDict, Function, OptFunction, OptDict

def about(func: AnyFunc) -> str:
    """Summary about a function.

    Args:
        func: Function instance

    Returns:
        Summary line of the docstring of a function.

    Examples:
        >>> about(about)
        'Summary about a function'

    """
    if not hasattr(func, '__doc__') or not func.__doc__:
        return ''

    return func.__doc__.split('\n', 1)[0].strip(' .')

def inst(name: str) -> OptFunction:
    """Create functionion instance for a given function name.

    Args:
        name: fully qualified function name

    Returns:


    Examples:
        >>> inst("nemoa.common.nfunc.inst")

    """
    from nemoa.common import nmodule

    mname = '.'.join(name.split('.')[:-1])
    fname = name.split('.')[-1]

    module = nmodule.inst(mname)
    if module is None:
        return None

    func = getattr(module, fname)
    if not isinstance(func, Function):
        return None

    return func

def kwargs(func: AnyFunc, default: OptDict = None) -> StrDict:
    """Keyword arguments of a function.

    Args:
        func: Function instance
        default: Dictionary containing alternative default values.
            If default is set to None, then all keywords of the function are
            returned with their standard default values.
            If default is a dictionary with string keys, then only
            those keywords are returned, that are found within default,
            and the returned values are taken from default.

    Returns:
        Dictionary of keyword arguments with default values.

    Examples:
        >>> kwargs(kwargs)
        {'default': None}
        >>> kwargs(kwargs, default = {'default': 'not None'})
        {'default': 'not None'}

    """
    # Check arguments
    if not isinstance(func, Function):
        raise TypeError('first argument requires to be a function')
    if not isinstance(default, (dict, type(None))):
        raise TypeError(
            "argument 'default' requires to be of type 'dict' or None"
            f", not '{type(default)}'")

    import inspect

    df = inspect.signature(func).parameters
    dkwargs = {}
    for key, val in df.items():
        if '=' not in str(val):
            continue
        if default is None:
            dkwargs[key] = val.default
        elif key in default:
            dkwargs[key] = default[key]

    return dkwargs
