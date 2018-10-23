# -*- coding: utf-8 -*-
"""Object hierarchy functions.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html
.. _PEP 257: https://www.python.org/dev/peps/pep-0257/

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect

from nemoa.base import ndict
from nemoa.types import Any, ClassInfo, OptStr, OptStrDictOfTestFuncs

def get_summary(obj: object) -> str:
    """Get summary line for an object.

    This function returns the summary line of the documentation string for an
    object as specified in `PEP 257`_. If the documentation string is not
    provided the summary line is retrieved from the inheritance hierarchy.

    Args:
        obj: Arbitrary object

    Returns:
        Summary line for an object.

    """
    text = inspect.getdoc(obj)
    if not isinstance(text, str) or not text:
        return ''
    return text.splitlines()[0].strip('.')

def has_base(obj: object, base: str) -> bool:
    """Return true if the object has the given base.

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

def get_name(obj: object) -> str:
    """Get name of an object.

    This function returns the name of an object. If the object does not have
    a magic name attribute, the name is retrieved from the inheritance
    hierarchy.

    Args:
        obj: Arbitrary object

    Returns:
        Name of an object.

    """
    return getattr(obj, '__name__', None) or getattr(type(obj), '__name__')

def get_members(
        obj: object, pattern: OptStr = None, classinfo: ClassInfo = object,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Get members of an object.

    Args:
        obj: Arbitrary object
        pattern: Only members which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. By default all
            names are allowed.
        classinfo: Classinfo given as a class, a type or a tuple containing
            classes, types or other tuples. Only members, which are ether an
            instance or a subclass of classinfo are returned. By default all
            types are allowed.
        rules: Dictionary with custom test functions, which are used for the
            comparison of the attribute value against the argument value. The
            dictionary items are of the form <*attribute*>: <*test*>, where
            <*attribute*> is the attribute name and <*test*> is a boolean valued
            lambda function, with two arguments <*arg*> and <*attr*>, which
            respectively give the value of the keyword argument and the member
            attribute. A member passes the rules, if all <*test*> functions
            evaluate to True against the given keyword arguments::
                Example: ``{'tags': lambda arg, attr: set(arg) <= set(attr)}``
            By default any attribute, which is not in the filter rules is
            compared to the argument value by equality.
        **kwds: Keyword arguments, that define the attribute filter for the
            returned dictionary. For example if the argument "tags = ['test']"
            is given, then only members are returned, which have the attribute
            'tags' and the value of the attribute equals ['test']. If, however,
            the filter rule of the above example is given, then any member,
            with attribute 'tags' and a corresponding tag list, that comprises
            'test' is returned.

    Returns:
        Dictionary with fully qualified object names as keys and attribute
        dictinaries as values.

    """
    # Get members of object, that satisfy the given base class
    predicate = lambda o: (
        isinstance(o, classinfo) or
        inspect.isclass(o) and issubclass(o, classinfo))
    refs = {k: v for k, v in inspect.getmembers(obj, predicate)}

    # Filter references to members, which names match a given pattern
    if pattern:
        refs = ndict.select(refs, pattern=pattern)

    # Create dictionary with members, which attributes pass all filter rules
    prefix = get_name(obj) + '.'
    rules = rules or {}
    valid = {}
    for name, ref in refs.items():
        if not hasattr(ref, '__dict__'):
            attr: dict = {}
        elif isinstance(ref.__dict__, dict):
            attr = ref.__dict__
        else:
            attr = ref.__dict__.copy()
        attr['name'] = attr.get('name', name)
        attr['about'] = attr.get('about', get_summary(ref))
        attr['reference'] = ref

        # Filter entry by attribute filter
        passed = True
        for key, val in kwds.items():
            if not key in attr:
                passed = False
                break
            # Apply individual attribute filter rules
            if key in rules:
                test = rules[key]
                if test(val, attr[key]):
                    continue
                passed = False
                break
            if val == attr[key]:
                continue
            passed = False
            break
        if not passed:
            continue

        # Add item
        valid[prefix + name] = attr

    return valid
