# -*- coding: utf-8 -*-
"""Handling of classes and methods.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect

from nemoa.core import ndict
from nemoa.types import (
    Any, RecDict, DictOfRecDicts, NestRecDict, FuncWrapper, OptStr)

def hasbase(obj: object, base: str) -> bool:
    """Return true if the class instance has the given base.

    Args:
        obj: Class
        base: Class name of base class

    Returns:
        True if the given object has the named base as base

    """
    if not hasattr(obj, '__class__'):
        raise TypeError(
            "argument 'obj' requires to be a class instance"
            f", not '{type(obj).__name__}'")

    return base in [o.__name__ for o in obj.__class__.__mro__]

def methods(
        obj: object, pattern: OptStr = None, groupby: OptStr = None,
        key: OptStr = None, val: OptStr = None) -> NestRecDict:
    """Get methods from a given class instance.

    Args:
        obj: Class
        pattern: Only methods, which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern
            is described in the standard library module `fnmatch`_.
        groupby: Name of attribute which value is used to group the results.
            If groupby is None, then the results are not grouped.
            Default: None
        key: Name of the attribute which is used as the key for the returned
            dictionary. If key is None, then the method names are used as key.
            Default: None
        val: Name of attribute which is used as the value for the returned
            dictionary. If val is None, then all attributes of the respective
            methods are returned. Default: None

    Returns:
        Dictionary containing all methods of a given class instance, which
        names satisfy a given filter pattern.

    """
    # Declare and initialize return values
    mdict: RecDict = {}
    gdict: DictOfRecDicts = {}

    # Get references from object inspection
    ref = dict(inspect.getmembers(obj, inspect.ismethod))

    # Filter dictionary to methods that match given pattern
    if pattern:
        ref = ndict.select(ref, pattern)

    # Create dictionary with method attributes
    for k, v in ref.items():
        attr = v.__dict__

        # Ignore method if any required attribute is not available
        if key and key not in attr:
            continue
        if val and val not in attr:
            continue
        if groupby and groupby not in attr:
            continue

        doc = v.__doc__ or ''
        about = doc.split('\n', 1)[0].strip(' .')
        attr['reference'] = v
        attr['about'] = attr.get('about', about)

        # change dictionary key, if argument 'key' is given
        if key:
            k = str(attr[key])
            if k in mdict:
                continue

        mdict[k] = attr

    # Group results
    if groupby:
        gdict = ndict.groupby(mdict, key=groupby)

        # Set value for returned dictionary
        if val:
            for v in gdict.values():
                for w in v.values():
                    w = w[val]
        return gdict

    # Set value for returned dictionary
    if val:
        for v in mdict.values():
            v = v[val]

    return mdict

def attributes(**attr: Any) -> FuncWrapper:
    """Decorate methods with attributes.

    Args:
        **attr: Arbitrary attributes

    Returns:
        Wrapper function with additional attributes

    """
    def wrapper(method): # type: ignore
        def wrapped(self, *args, **kwds): # type: ignore
            return method(self, *args, **kwds)

        for key, val in attr.items():
            setattr(wrapped, key, val)

        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper
