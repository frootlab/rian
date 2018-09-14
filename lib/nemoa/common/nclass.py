# -*- coding: utf-8 -*-
"""Generic handling of classes and methods."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.common.ntype import Any, Callable, Object, OptStr

def hasbase(obj: Object, base: str) -> bool:
    """Return true if the class instance has the given base.

    Args:
        obj: Class instance
        base: Class name of base class

    Returns:
        True if the given object has the named base as base

    """

    if not hasattr(obj, '__class__'):
        raise TypeError("argument 'obj' is required to be a class instance")

    return base in [o.__name__ for o in obj.__class__.__mro__]

def methods(
        obj: Object, filter: OptStr = None, groupby: OptStr = None,
        key: OptStr = None, val: OptStr = None
    ) -> dict:
    """Get methods from a given class instance.

    Args:
        obj: Class instance
        filter: Only methods, which names satisfy the wildcard patterns given
            by 'filter' are returned. The format of the wildcard pattern
            is described in the standard library module 'fnmatch' [1]
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

    References:
        [1] https://docs.python.org/3/library/fnmatch.html

    """

    import inspect
    from nemoa.common import ndict

    # get references from object inspection
    md = dict(inspect.getmembers(obj, inspect.ismethod))

    # filter dictionary to methods that match given pattern
    if filter:
        md = ndict.filter(md, filter)

    # create dictionary with method attributes
    mc = {}
    for k, v in md.items():
        a = v.__dict__

        # ignore method if any required attribute is not available
        if key and key not in a:
            continue
        if val and val not in a:
            continue
        if groupby and groupby not in a:
            continue

        mc[k] = a
        mc[k]['reference'] = v
        if isinstance(v.__doc__, str):
            mc[k]['about'] = v.__doc__.split('\n', 1)[0].strip(' .')
        else:
            mc[k]['about'] = ''
    md = mc

    # set key for returned dictionary
    if key:
        nd = {}
        for k, v in md.items():
            kr = v[key]
            if kr in nd: continue
            nd[kr] = v
        md = nd

    # group results
    if groupby:
        md = ndict.groupby(md, key=groupby)

    # set value for returned dictionary
    if val:
        if groupby:
            for k1, v1 in md.items():
                for k2, v2 in v1.items():
                    v2 = v2[val]
        else:
            for k, v in md.items():
                v = v[val]

    return md

def attributes(**attr: Any) -> Callable:
    """Generic attribute decorator for class methods.

    Args:
        **attr: Arbitrary attributes

    Returns:
        Wrapper function with additional attributes

    """

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.items():
            setattr(wrapped, key, val)

        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper
