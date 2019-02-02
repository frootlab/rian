# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Object tree helper functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import inspect
from typing import Collection
from nemoa.base import call, check, literal, mapping
from nemoa.types import Any, ClassInfo, OptStr, OptDictOfKeyOps
from nemoa.types import RecDict, Union, StrDict
from nemoa.types import DictOfRecDicts, StrOrType

#
# Structural Types
#

NestRecDict = Union[StrDict, RecDict, DictOfRecDicts]

#
# Functions
#

def call_attr(obj: object, attr: str, *args: Any, **kwds: Any) -> Any:
    """Call an object attribute with given arguments.

    Args:
        obj: Arbitrary object
        attr: Name of callable object attribute
        *args: Arbitrary arguments, that are passed to the call
        *kwds: Arbitrary keyword arguments, that are passes to the call, if
            supported by the member attribute.

    Returns:
        Result of call.

    """
    name = literal.from_str(attr, charset='uax-31')
    check.has_attr(obj, name)
    func = getattr(obj, name)
    check.is_callable(attr, func)
    return call.safe_call(func, *args, **kwds)

def get_members(
        obj: object, pattern: OptStr = None, classinfo: ClassInfo = object,
        rules: OptDictOfKeyOps = None, **kwds: Any) -> list:
    """List members of an object.

    This is a wrapper function to :func:`~nemoa.base.otree.get_members_dict`,
    but only returns the names of the members instead of the respective
    dictionary of attributes.

    """
    dicts = get_members_dict(
        obj, pattern=pattern, classinfo=classinfo, rules=rules, **kwds)
    return [member['name'] for member in dicts.values()]

def get_members_dict(
        obj: object, pattern: OptStr = None, classinfo: ClassInfo = object,
        rules: OptDictOfKeyOps = None, **kwds: Any) -> dict:
    """Get dictionary with an object's members dict attributes.

    Args:
        obj: Arbitrary object
        pattern: Only members which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module :py:mod:`fnmatch`. By
            default all names are allowed.
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
                rules = {'tags': lambda arg, attr: set(arg) <= set(attr)}
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
        refs = mapping.select(refs, pattern=pattern)

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
        if isinstance(attr.get('name'), str):
            attr['name'] = attr.get('name')
        else:
            attr['name'] = name
        attr['about'] = get_summary(ref)
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

def get_name(obj: object) -> str:
    """Get name identifier for an object.

    This function returns the name identifier of an object. If the object does
    not have a name attribute, the name is retrieved from the object class.

    Args:
        obj: Arbitrary object

    Returns:
        Name of an object.

    """
    return getattr(obj, '__name__', obj.__class__.__name__)

def get_lang_repr(obj: object, separator: str = 'and') -> str:
    """Get natural language representation of an object.

    Args:
        seperator: String separator for collection items.

    Returns:
        Natural language representation of object.

    """
    if hasattr(obj, '__name__'):
        return repr(obj.__name__) # type: ignore
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, Collection):
        if isinstance(obj, set):
            item = 'element'
        else:
            item = 'item'
        size = len(obj)
        if size == 0:
            return f'no {item}s'
        if size == 1:
            name = repr(str(obj.__iter__().__next__()))
            return f'{item} {name}'
        if size < 4:
            sep = f' {separator} '
            items = [repr(str(each)) for each in obj]
            return f'{item}s ' + sep.join(items)
        return f'some {item}s'
    return repr(obj)

def get_summary(obj: object) -> str:
    """Get summary line for an object.

    This function returns the summary line of the documentation string for an
    object as specified in :PEP:`257`. If the documentation string is not
    provided the summary line is retrieved from the inheritance hierarchy.

    Args:
        obj: Arbitrary object

    Returns:
        Summary line for an object.

    """
    if isinstance(obj, str):
        if not obj:
            return 'empty string'
        return obj.split('\n', 1)[0].rstrip('\n\r .')
    return get_summary(inspect.getdoc(obj) or ' ')

def has_base(obj: object, base: StrOrType) -> bool:
    """Return true if the object has the given base class.

    Args:
        obj: Arbitrary object
        base: Class name of base class

    Returns:
        True if the given object has the named base as base

    """
    mro = getattr(obj, '__mro__', obj.__class__.__mro__)
    if isinstance(base, type):
        return base in mro
    return base in [cls.__name__ for cls in mro]

def get_methods(
        obj: object, pattern: OptStr = None, groupby: OptStr = None,
        key: OptStr = None, val: OptStr = None) -> NestRecDict:
    """Get methods from a given class instance.

    Args:
        obj: Class object
        pattern: Only methods, which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern
            is described in the standard library module :py:mod:`fnmatch`.
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
        ref = mapping.select(ref, pattern)

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

        # Change dictionary key, if argument 'key' is given
        if key:
            k = str(attr[key])
            if k in mdict:
                continue

        mdict[k] = attr

    # Group results
    if groupby:
        gdict = mapping.groupby(mdict, key=groupby)

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
