# -*- coding: utf-8 -*-
"""Database and Data Warehouse."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import pkg
from nemoa.db import table
from nemoa.errors import ConnectError
from nemoa.types import Any, Module

#
# Constructors
#

def connect(name: str, *args: Any, **kwds: Any) -> table.Proxy:
    """Connect Table Proxy

    Args:
        name: Name of module, which is used to connect a Table Proxy.
        *args: Arguments, that are passed to the class 'Table' of the given
            module.
        **kwds: Keyword arguments, that are passed to the class 'Table' of the
            given module.

    """
    module = pkg.get_submodule(name=name)
    if not isinstance(module, Module):
        raise ConnectError(f"module '{name}' does not exist")
    if not hasattr(module, 'Table'):
        raise ConnectError(f"module '{name}' does not contain a 'Table' class")
    return module.Table(*args, **kwds) # type: ignore
