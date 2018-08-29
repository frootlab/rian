# -*- coding: utf-8 -*-
"""Global session management using singleton design pattern."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def create(*args, **kwargs):
    """Create new object instance from building script."""

def get(*args, **kwargs):
    """Get meta information and content from current session."""
    return instance().get(*args, **kwargs)

def instance(*args, **kwargs):
    """Get session instance."""
    if 'default' not in globals(): globals()['default'] = new()
    return globals()['default']

def log(*args, **kwargs):
    """Log message in current session."""
    return instance().log(*args, **kwargs)

def new(*args, **kwargs):
    """Create session instance from session dictionary."""
    from nemoa.session import classes
    return classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Open object in current session."""
    return instance().open(*args, **kwargs)

def run(*args, **kwargs):
    """Run script in current session."""
    return instance().run(*args, **kwargs)

def set(*args, **kwargs):
    """Set configuration parameter and env var in current session."""
    return instance().set(*args, **kwargs)
