# -*- coding: utf-8 -*-
"""IPython interactive shell."""

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

from nemoa.core import ui

def run(banner: str = '', clear: bool = True) -> None:
    """Start IPython interactive shell in embedded mode."""
    # Bypass IPython excepthook to local 'exepthook', to allow logging of
    # uncaught exceptions
    IShell = IPython.core.interactiveshell.InteractiveShell
    func = IShell.showtraceback
    hook = ui.hook_exception
    IShell.showtraceback = ui.bypass_exceptions(func, hook)

    # Clear screen
    if clear:
        ui.clear()

    # Prepare arguments
    kwds = {}
    if banner:
        kwds['banner1'] = banner + '\n'

    # Start IPython interactive shell in embedded mode.
    IPython.embed(**kwds)
