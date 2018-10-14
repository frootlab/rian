# -*- coding: utf-8 -*-
"""Extended handling of function type objects."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.types import AnyFunc, StrDict, Function, OptFunction, OptDict

def about(func: AnyFunc) -> str:
    """Summary line of docstring of a function.

    Args:
        func: Function instance

    Returns:
        Summary line of the docstring of a function.

    Examples:
        >>> about(about)
        'Summary line of docstring of a function'

    """
    if not hasattr(func, '__doc__') or not func.__doc__:
        return ''

    return func.__doc__.split('\n', 1)[0].strip(' .')

def inst(name: str) -> OptFunction:
    """Create function instance for a given function name.

    Args:
        name: fully qualified function name

    Returns:
        Function instance or None, if the function could not be found.

    Examples:
        >>> inst("nemoa.core.nfunc.inst")

    """
    from nemoa.core import nmodule

    mname = '.'.join(name.split('.')[:-1])
    fname = name.split('.')[-1]

    module = nmodule.inst(mname)
    if module is None:
        return None

    func = getattr(module, fname)
    if not isinstance(func, Function):
        return None

    return func

def kwds(func: AnyFunc, default: OptDict = None) -> StrDict:
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
        >>> kwds(kwds)
        {'default': None}
        >>> kwds(kwds, default = {'default': 'not None'})
        {'default': 'not None'}

    """
    # Check Arguments
    if not isinstance(func, Function):
        raise TypeError('first argument requires to be a function')
    if not isinstance(default, (dict, type(None))):
        raise TypeError(
            "argument 'default' requires to be of type 'dict' or None"
            f", not '{type(default)}'")

    import inspect

    df = inspect.signature(func).parameters
    dkwds = {}
    for key, val in df.items():
        if '=' not in str(val):
            continue
        if default is None:
            dkwds[key] = val.default
        elif key in default:
            dkwds[key] = default[key]

    return dkwds
