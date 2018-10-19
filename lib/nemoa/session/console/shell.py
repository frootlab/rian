#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
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
        def showtraceback(*args, **kwds):

            # extract exception type, value and traceback
            etype, value, trace = sys.exc_info()

            # run the original python hook
            if issubclass(etype, Exception):
                return sys.__excepthook__(etype, value, trace)

            # otherwise run the original hook
            return func(*args, **kwds)

        return showtraceback

    interactiveshell.InteractiveShell.showtraceback \
        = _change(interactiveshell.InteractiveShell.showtraceback)

    # def about(*args, **kwds) -> None:
    #     """Get meta information."""
    #     nemoa.log('note', nemoa.about(*args, **kwds))
    #
    # def close() -> None:
    #     """Close current workspace instance."""
    #     nemoa.close()
    #
    # def get(*args, **kwds) -> None:
    #     """Wrap function to nemoa.get()."""
    #     nemoa.log('note', nemoa.get(*args, **kwds))
    #
    # def list(*args, **kwds) -> None:
    #     """Wrap function to nemoa.list()."""
    #     retval = nemoa.list(*args, **kwds)
    #     if isinstance(retval, dict):
    #         for key, val in retval.items():
    #             if not val:
    #                 continue
    #             if hasattr(val, '__iter__'):
    #                 nemoa.log('note', '%s: %s' % (key, ', '.join(val)))
    #             else:
    #                 nemoa.log('note', '%s: %s' % (key, val))
    #     elif hasattr(retval, '__iter__'):
    #         nemoa.log('note', ', '.join(retval))
    #
    # def open(*args, **kwds):
    #     """Open object in current session."""
    #     return nemoa.open(*args, **kwds)
    #
    # def optimize(*args, **kwds) -> None:
    #     """Optimize model."""
    #     return nemoa.model.morphisms.optimize(*args, **kwds)
    #
    # def path(*args, **kwds) -> None:
    #     """Wrap function to nemoa.path()."""
    #     nemoa.log('note', nemoa.path(*args, **kwds))
    #
    # def run(*args, **kwds) -> None:
    #     """Wrap function to nemoa.run()."""
    #     nemoa.run(*args, **kwds)
    #
    # def show(*args, **kwds) -> None:
    #     """ """
    #     open(*args, **kwds).show()
    #
    # def set(*args, **kwds) -> None:
    #     """Wrap function to nemoa.set()."""
    #     nemoa.set(*args, **kwds)

    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    nemoa.set('mode', 'shell')

    from nemoa.core import napp
    name = napp.get_var('name')
    version = napp.get_var('version')

    return IPython.embed(banner1=f"{name} {version}\n")

if __name__ == '__main__':
    main()
