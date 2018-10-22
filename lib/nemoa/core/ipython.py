# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import IPython
except ImportError as err:
    raise ImportError(
        "requires package ipython: "
        "https://ipython.org/") from err

from nemoa.core import shell
from nemoa.types import OptStr

def bypass_exepthook() -> None:
    """Bypass exceptions from IPython Interactive Shell."""


def start_shell(banner: OptStr = None) -> None:
    """ """
    # Bypass IPython excepthook to allow logging of uncaught exceptions
    IShell = IPython.core.interactiveshell.InteractiveShell
    IShell.showtraceback = shell.bypass_exceptions(IShell.showtraceback)

    # Clear screen
    shell.clear()

    # Prepare arguments
    kwds = {}
    if banner:
        kwds['banner1'] = banner + '\n'
    IPython.embed(**kwds)
