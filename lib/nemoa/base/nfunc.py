# -*- coding: utf-8 -*-
"""Extended handling of function type objects."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

__all__ = ['get_summary', 'get_instance', 'get_kwds']

import inspect

from nemoa.base import bare, check, nmodule
from nemoa.types import AnyFunc, StrDict, Function, OptFunction, OptDict

def get_summary(func: AnyFunc) -> str:
    """Get summary line of a function.

    Args:
        func: Function instance

    Returns:
        Summary line of the docstring of a function.

    """
    return bare.get_summary(func)

def get_instance(name: str) -> OptFunction:
    """Get function instance for a given function name.

    Args:
        name: fully qualified function name

    Returns:
        Function instance or None, if the function could not be found.

    Examples:
        >>> get_instance("nemoa.base.nfunc.get_instance")

    """
    mname, fname = name.rsplit('.', 1)
    minst = nmodule.get_instance(mname)

    if not minst:
        return None

    func = getattr(minst, fname)
    if not isinstance(func, Function):
        return None

    return func

def get_kwds(func: AnyFunc, default: OptDict = None) -> StrDict:
    """Get keyword arguments of a function.

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
        >>> get_kwds(get_kwds)
        {'default': None}
        >>> get_kwds(get_kwds, default = {'default': 'not None'})
        {'default': 'not None'}

    """
    # Check Arguments
    check.has_type("first argument 'key'", func, Function)
    check.has_opt_type("argument 'default'", default, dict)

    # Get keywords from inspect
    kwds: StrDict = {}
    struct = inspect.signature(func).parameters
    for key, val in struct.items():
        if '=' not in str(val):
            continue
        if default is None:
            kwds[key] = val.default
        elif key in default:
            kwds[key] = default[key]

    return kwds
