# -*- coding: utf-8 -*-
"""Functions to access application variables and directories.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html
.. _PEP 257: https://www.python.org/dev/peps/pep-0257/

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect

from nemoa.core import ndict
from nemoa.types import Any, OptStr, OptStrDictOfTestFuncs

def summary(obj: object) -> str:
    """Get summary line for an object.

    This function returns the summary line of the documentation string for an
    object as specified in `PEP 257`_. If the documentation string is not
    provided the summary line is retrieved from the inheritance hierarchy.

    Args:
        obj: Arbitrary object

    Returns:
        Summary line for an object.

    """
    doc = inspect.getdoc(obj)
    if not isinstance(doc, str) or not doc:
        return ''
    return doc.splitlines()[0].strip('.')

def members(
        obj: object, pattern: OptStr = None, base: type = object,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Get members of an object.

    Args:
        obj: Arbitrary object
        pattern: Only members which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. By default all
            members are returned.
        base: Class info given as a class, a type or a tuple containing classes,
            types or other tuples.
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
    if not hasattr(obj, '__name__'):
        raise TypeError("'obj' is required to have the attribute '__name__'")

    # Get member references of given base class
    predicate = lambda o: (
        isinstance(o, base) or
        inspect.isclass(o) and issubclass(o, base))
    refs = {k: v for k, v in inspect.getmembers(obj, predicate)}

    # Filter references to members, which names match a given pattern
    if pattern:
        refs = ndict.select(refs, pattern=pattern)

    # Create dictionary with members, which attributes pass all filter rules
    prefix = obj.__name__ + '.' # type: ignore
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
        attr['about'] = attr.get('about', summary(ref))
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
