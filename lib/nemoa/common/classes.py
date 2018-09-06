# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Optional

def hasbase(obj: object, base: str) -> bool:
    """Return true if the class instance has the given base.

    Args:
        obj: Class instance
        base: Class name of base class

    Returns:
        True if the given object has the named base as base

    """

    if not hasattr(obj, '__class__'):
        raise TypeError("obj is required to be a class instance")

    bases = [o.__name__ for o in obj.__class__.__mro__]
    return base in bases

def methods(obj: object, prefix: str = '',
    key: Optional[str] = None, val: Optional[str] = None,
    groupby: Optional[str] = None) -> dict:
    """Get methods from a given class instance.

    Args:
        obj: Class instance
        prefix: Only methods, which names have the given prefix are returned.
        key: Name of attribute which is used as key for the returned dictionary.
            If key is None, then the (trimmed) method names are used as key.
            Default: None
        val: Name of attribute name which is used as value for the returned
            dictionary. If val is None, then all attributes of the respective
            methods are returned. Default: None
        groupby: Name of attribute which value is used to group the results.
            If groupby is None, then the results are not grouped.
            Default: None

    Returns:
        Dictionary containing all methods of a given class instance, that
        pass the given filter.

    """

    import inspect

    # get references from module inspection and filter prefix
    md = dict(inspect.getmembers(obj, inspect.ismethod))

    # reduce dictionary to methods with given prefix
    from nemoa.common import ndict
    md = ndict.reduce(md, s = prefix, trim = False)

    # get method attributes
    mc = {}
    for k, v in md.items():
        a = v.__dict__

        # ignore method if some required attribute is not available
        if key and not key in a or val and not val in a \
            or groupby and not groupby in a: continue

        mc[k] = a
        mc[k]['reference'] = v
        if isinstance(v.__doc__, str):
            mc[k]['about'] = v.__doc__.split('\n', 1)[0].strip(' .')
        else: mc[k]['about'] = ''
    md = mc

    # set key for returned dictionary
    if key:
        nd = {}
        for k, v in md.items():
            kr = v[key]
            if kr in nd: continue
            nd[kr] = v
        md = nd

    # group methods, rename key and reduce to attribute
    if groupby: md = ndict.groupby(md, key = groupby)

    # set value for returned dictionary
    if val:
        if groupby:
            for k1, v1 in md.items():
                for k2, v2 in v1.items(): v2 = v2[val]
        else:
            for k, v in md.items(): v = v[val]

    return md

def attributes(**attr):
    """Generic attribute decorator for class methods."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for k, v in attr.items():
            setattr(wrapped, k, v)

        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper
