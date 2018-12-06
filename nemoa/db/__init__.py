# -*- coding: utf-8 -*-
"""Database I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import this
from nemoa.db import table
from nemoa.errors import ConnectError
from nemoa.types import Any, Module

#
# Constructors
#

def connect(module: str, *args: Any, **kwds: Any) -> table.ProxyBase:
    """Connect Table Proxy

    Args:
        module: Name of module, which is used to connect a Table Proxy.
        *args: Arguments, that are passed to the class 'Table' of the given
            module.
        **kwds: Keyword arguments, that are passed to the class 'Table' of the
            given module.

    """
    mref = this.get_submodule(module)
    if not isinstance(mref, Module):
        raise ConnectError("module '{module}' does not exist")
    if not hasattr(mref, 'Table'):
        raise ConnectError(
            "module '{module}' does not contain a 'TableProxy' class")
    return mref.Table(*args, **kwds) # type: ignore
