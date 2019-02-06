# -*- coding: utf-8 -*-
"""Global session management using singleton design pattern."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from typing import Any
from nemoa.session import classes

def cur():
    """Get current session instance."""
    if '_cur' not in globals():
        globals()['_cur'] = new()
    return globals()['_cur']

def get(*args: Any, **kwds: Any) -> Any:
    """Get meta information and content from current session."""
    return cur().get(*args, **kwds)

def log(*args, **kwds):
    """Log message in current session."""
    return cur().log(*args, **kwds)

def new(*args, **kwds):
    """Create session instance from session dictionary."""
    return classes.new(*args, **kwds)

def open(*args, **kwds):
    """Open object in current session."""
    return cur().open(*args, **kwds)

def path(*args: Any, **kwds: Any) -> str:
    """Get path for given object in current session."""
    return cur().path(*args, **kwds)

def run(*args, **kwds):
    """Run script in current session."""
    return cur().run(*args, **kwds)

def set(*args, **kwds):
    """Set configuration parameter and env var in current session."""
    return cur().set(*args, **kwds)
