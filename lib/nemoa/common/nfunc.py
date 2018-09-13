# -*- coding: utf-8 -*-
"""Collection of functions for function handling."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Callable, Optional

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
    if not func.__doc__: return ''

    return func.__doc__.split('\n', 1)[0].strip(' .')

def func(name: str) -> Optional[Callable]:
    """Function instance for a given fully qualified function name.

    Args:
        name: fully qualified function name

    Returns:


    Examples:
        >>> func("nemoa.common.nfunc.func")

    """

    from nemoa.common import nmodule

    minst = nmodule.objectify('.'.join(name.split('.')[:-1]))

    if minst is None: return None
    func = getattr(minst, name.split('.')[-1])

    return func

def kwargs(func: Callable, default: Optional[dict] = None) -> dict:
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
        raise TypeError(f"argument 'default' requires types "
            f"'None' or 'dict', not '{type(default)}'")

    import inspect

    df = inspect.signature(func).parameters
    kd = {}
    for k, v in df.items():
        if '=' not in str(v): continue
        if default is None: kd[k] = v.default
        elif k in default: kd[k] = default[k]

    return kd
