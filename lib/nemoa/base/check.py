# -*- coding: utf-8 -*-
"""Collection of frequently functions for multitreading."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.types import Any, ClassInfo, StrOrInt

def argtype(name: StrOrInt, value: Any, classinfo: ClassInfo) -> None:
    """Check type of argument."""
    if isinstance(value, classinfo):
        return None
    if isinstance(classinfo, type):
        typeinfo = classinfo.__name__
    elif isinstance(classinfo, tuple):
        names = [getattr(each, '__name__', '?') for each in classinfo]
        typeinfo = "' or '".join(names)
    else:
        return argtype('classinfo', classinfo, (type, tuple))
    if isinstance(name, str):
        argument = f"Argument '{name}'"
    elif name == 0:
        argument = "First argument"
    elif name == 1:
        argument = "Second argument"
    else:
        argument = f"Argument [{name}]"
    valtype = type(value).__name__
    raise TypeError(
        f"{argument} requires type '{typeinfo}' not '{valtype}'")
