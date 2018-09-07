#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def main():

    import nemoa

    try:
        import IPython
    except ImportError as e:
        raise ImportError("IPython is required: https://ipython.org/") from e

    from IPython.core.interactiveshell import InteractiveShell

    def __change(func):
        from functools import wraps
        import sys

        @wraps(func)
        def showtraceback(*args, **kwargs):

            # extract exception type, value and traceback
            typ, val, tb = sys.exc_info()

            # run the original python hook
            if issubclass(typ, Exception):
                return sys.__excepthook__(typ, val, tb)
            else:
                # otherwise run the original hook
                return func(*args, **kwargs)

        return showtraceback

    InteractiveShell.showtraceback = __change(InteractiveShell.showtraceback)

    def about(*args, **kwargs):
        """Get meta information."""
        nemoa.log('note', nemoa.about(*args, **kwargs))
        return None

    def close(*args, **kwargs):
        """Close current workspace instance."""
        nemoa.close()
        return None

    def create(*args, **kwargs):
        """Create object instance from building script."""
        return nemoa.create(*args, **kwargs)

    def get(*args, **kwargs):
        """Wrapping function to nemoa.get()."""
        nemoa.log('note', nemoa.get(*args, **kwargs))
        return None

    def list(*args, **kwargs):
        """Wrapping function to nemoa.list()."""
        retval = nemoa.list(*args, **kwargs)
        if isinstance(retval, dict):
            for key, val in retval.items():
                if not val: continue
                if hasattr(val, '__iter__'):
                    nemoa.log('note', '%s: %s' % (key, ', '.join(val)))
                else:
                    nemoa.log('note', '%s: %s' % (key, val))
        elif hasattr(retval, '__iter__'):
            nemoa.log('note', ', '.join(retval))
        return None

    def open(*args, **kwargs):
        """Open object in current session."""
        return nemoa.open(*args, **kwargs)

    def optimize(*args, **kwargs):
        """Optimize model."""
        return nemoa.model.morphisms.optimize(*args, **kwargs)

    def path(*args, **kwargs):
        """Wrapping function to nemoa.path()."""
        nemoa.log('note', nemoa.path(*args, **kwargs))
        return None

    def run(*args, **kwargs):
        """Wrapping function to nemoa.run()."""
        nemoa.run(*args, **kwargs)
        return None

    def show(*args, **kwargs):
        """ """
        open(*args, **kwargs).show()
        return None

    def set(*args, **kwargs):
        """Wrapping function to nemoa.set()."""
        nemoa.set(*args, **kwargs)
        return None

    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    nemoa.set('mode', 'shell')

    from nemoa.common import appinfo
    name = appinfo.get('name')
    version = appinfo.get('version')

    return IPython.embed(banner1 = f"{name} {version}\n")

if __name__ == '__main__':
    main()
