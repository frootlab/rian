# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import types
from typing import Union
Function = types.FunctionType

def kwargs(func: Function, d: dict = None) -> Union[dict, list]:
    """Keyword arguments of a function.

    Args:
        func:
        d:

    Returns:


    """

    if not isinstance(func, Function):
        raise TypeError('first argument is required to be a function')

    import inspect

    df = inspect.signature(func).parameters

    klist = [k for k, v in df.items() if '=' in str(v)]
    if d is None: return klist

    kdict = {k: d.get(k) for k in klist if k in d}
    return kdict
