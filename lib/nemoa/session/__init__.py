# -*- coding: utf-8 -*-
"""Global session management using singleton design pattern."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def cur():
    """Get current session instance."""
    if '_cur' not in globals(): globals()['_cur'] = new()
    return globals()['_cur']

def get(*args, **kwargs):
    """Get meta information and content from current session."""
    return cur().get(*args, **kwargs)

def log(*args, **kwargs):
    """Log message in current session."""
    return cur().log(*args, **kwargs)

def new(*args, **kwargs):
    """Create session instance from session dictionary."""
    from nemoa.session import classes
    return classes.new(*args, **kwargs)

def open(*args, **kwargs):
    """Open object in current session."""
    return cur().open(*args, **kwargs)

def path(*args, **kwargs):
    """Get path for given object in current session."""
    return cur().path(*args, **kwargs)

def run(*args, **kwargs):
    """Run script in current session."""
    return cur().run(*args, **kwargs)

def set(*args, **kwargs):
    """Set configuration parameter and env var in current session."""
    return cur().set(*args, **kwargs)
