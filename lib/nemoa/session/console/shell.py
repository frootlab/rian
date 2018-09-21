#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def main():

    import nemoa

    try:
        import IPython
    except ImportError as err:
        raise ImportError(
            "requires package ipython: "
            "https://ipython.org/") from err

    from IPython.core import interactiveshell

    def _change(func):
        from functools import wraps
        import sys

        @wraps(func)
        def showtraceback(*args, **kwargs):

            # extract exception type, value and traceback
            etype, value, trace = sys.exc_info()

            # run the original python hook
            if issubclass(etype, Exception):
                return sys.__excepthook__(etype, value, trace)

            # otherwise run the original hook
            return func(*args, **kwargs)

        return showtraceback

    interactiveshell.InteractiveShell.showtraceback \
        = _change(interactiveshell.InteractiveShell.showtraceback)

    def about(*args, **kwargs) -> None:
        """Get meta information."""
        nemoa.log('note', nemoa.about(*args, **kwargs))

    def close() -> None:
        """Close current workspace instance."""
        nemoa.close()

    def get(*args, **kwargs) -> None:
        """Wrap function to nemoa.get()."""
        nemoa.log('note', nemoa.get(*args, **kwargs))

    def list(*args, **kwargs) -> None:
        """Wrap function to nemoa.list()."""
        retval = nemoa.list(*args, **kwargs)
        if isinstance(retval, dict):
            for key, val in retval.items():
                if not val:
                    continue
                if hasattr(val, '__iter__'):
                    nemoa.log('note', '%s: %s' % (key, ', '.join(val)))
                else:
                    nemoa.log('note', '%s: %s' % (key, val))
        elif hasattr(retval, '__iter__'):
            nemoa.log('note', ', '.join(retval))

    def open(*args, **kwargs):
        """Open object in current session."""
        return nemoa.open(*args, **kwargs)

    def optimize(*args, **kwargs) -> None:
        """Optimize model."""
        return nemoa.model.morphisms.optimize(*args, **kwargs)

    def path(*args, **kwargs) -> None:
        """Wrap function to nemoa.path()."""
        nemoa.log('note', nemoa.path(*args, **kwargs))

    def run(*args, **kwargs) -> None:
        """Wrap function to nemoa.run()."""
        nemoa.run(*args, **kwargs)

    def show(*args, **kwargs) -> None:
        """ """
        open(*args, **kwargs).show()

    def set(*args, **kwargs) -> None:
        """Wrap function to nemoa.set()."""
        nemoa.set(*args, **kwargs)

    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    nemoa.set('mode', 'shell')

    from nemoa.common import napp
    name = napp.getvar('name')
    version = napp.getvar('version')

    return IPython.embed(banner1=f"{name} {version}\n")

if __name__ == '__main__':
    main()
