# -*- coding: utf-8 -*-
"""Collection of functions for function handling."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.common.ntype import Callable, OptCallable, OptDict

def about(func: Callable) -> str:
    """Summary about a function.

    Args:
        func: Function instance

    Returns:
        Summary line of the docstring of a function.

    Examples:
        >>> about(about)
        'Summary about a function'

    """
    if not isinstance(func, Callable):
        raise TypeError('first argument requires to be a function')

    if not func.__doc__:
        return ''

    return func.__doc__.split('\n', 1)[0].strip(' .')

def inst(name: str) -> OptCallable:
    """Create functionion instance for a given function name.

    Args:
        name: fully qualified function name

    Returns:


    Examples:
        >>> inst("nemoa.common.nfunc.inst")

    """
    from nemoa.common import nmodule

    module = nmodule.inst('.'.join(name.split('.')[:-1]))
    if module is None:
        return None

    return getattr(module, name.split('.')[-1])

def kwargs(func: Callable, default: OptDict = None) -> dict:
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
    # check types of arguments
    if not isinstance(func, Callable):
        raise TypeError('first argument requires to be a function')
    if not isinstance(default, (dict, type(None))):
        raise TypeError(
            "argument 'default' requires types "
            f"'None' or 'dict', not '{type(default)}'")

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
