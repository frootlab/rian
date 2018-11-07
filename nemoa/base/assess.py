# -*- coding: utf-8 -*-
"""Python object functions.

.. References:
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html
.. _PEP 257: https://www.python.org/dev/peps/pep-0257/

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import ast
import importlib
import inspect
import pkgutil
from nemoa.base import check, ndict
from nemoa.types import Any, ClassInfo, OptStr, OptStrDictOfTestFuncs
from nemoa.types import OptModule, Module, StrList, OptFunction, Function
from nemoa.types import StrDict, AnyFunc, OptDict, Tuple, RecDict, NestRecDict
from nemoa.types import DictOfRecDicts, FuncWrapper, Method, StrOrType

#
# Module Functions
#

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

def get_name(obj: object) -> str:
    """Get name of an object.

    This function returns the name of an object. If the object does not have
    a name attribute, the name is retrieved from the object type.

    Args:
        obj: Arbitrary object

    Returns:
        Name of an object.

    """
    return getattr(obj, '__name__', obj.__class__.__name__)

def get_members(
        obj: object, pattern: OptStr = None, classinfo: ClassInfo = object,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> list:
    """List members of an object.

    This is a wrapper function to `get_members_dict`, but only returns the
    names of the members instead of the respective dictionary of attributes.
    """
    dicts = get_members_dict(
        obj, pattern=pattern, classinfo=classinfo, rules=rules, **kwds)
    return [member['name'] for member in dicts.values()]

def get_members_dict(
        obj: object, pattern: OptStr = None, classinfo: ClassInfo = object,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Get dictionary with an object's members dict attributes.

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
    if isinstance(obj, str):
        if not obj:
            return 'empty string'
        return obj.split('\n', 1)[0].rstrip('\n\r .')
    return get_summary(inspect.getdoc(obj) or ' ')

def get_module(name: str) -> OptModule:
    """Get reference to module instance from a fully qualified module name.

    Args:
        name: Fully qualified name of module

    Returns:
        Module reference of the given module name or None, if the name does not
        point to a valid module.

    """
    # Check type of 'name'
    check.has_type("argument 'name'", name, str)

    # Try to import module using importlib
    module: OptModule = None
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return module

    return module

def get_submodules(ref: Module, recursive: bool = False) -> StrList:
    """Get list with submodule names.

    Args:
        module: Module reference to search for submodules.
        recursive: Boolean value which determines, if the search is performed
            recursively within all submodules. Default: False

    Returns:
        List with full qualified submodule names.

    """
    # Check if given module is a package by the existence of a path attribute.
    # Otherwise the module does not contain any submodules and an empty list is
    # returned.
    subs: StrList = []
    if not hasattr(ref, '__path__'):
        return subs

    # Iterate submodules within package by using pkgutil
    prefix = ref.__name__ + '.'
    path = getattr(ref, '__path__')
    for finder, name, ispkg in pkgutil.iter_modules(path):
        fullname = prefix + name
        subs.append(fullname)
        if ispkg and recursive:
            sref = get_module(fullname)
            if isinstance(sref, Module):
                subs += get_submodules(sref, recursive=True)

    return subs

def get_function(name: str) -> OptFunction:
    """Get function instance for a given function name.

    Args:
        name: fully qualified function name

    Returns:
        Function instance or None, if the function could not be found.

    Examples:
        >>> get_function('nemoa.base.assess.get_function')

    """
    mname, fname = name.rsplit('.', 1)
    minst = get_module(mname)

    if not minst:
        return None

    func = getattr(minst, fname)
    if not isinstance(func, Function):
        return None

    return func

def get_function_kwds(func: AnyFunc, default: OptDict = None) -> StrDict:
    """Get keyword arguments of a function.

    Args:
        func: Function instance
        default: Dictionary containing alternative default values.
            If default is set to None, then all keywords of the function are
            returned with their standard default values.
            If default is a dictionary with string keys, then only
            those keywords are returned, that are found within default,
            and the returned values are taken from default.

    Returns:
        Dictionary of keyword arguments with default values.

    Examples:
        >>> get_kwds(get_kwds)
        {'default': None}
        >>> get_kwds(get_kwds, default = {'default': 'not None'})
        {'default': 'not None'}

    """
    # Check Arguments
    check.has_type("first argument 'key'", func, Function)
    check.has_opt_type("argument 'default'", default, dict)

    # Get keywords from inspect
    kwds: StrDict = {}
    struct = inspect.signature(func).parameters
    for key, val in struct.items():
        if '=' not in str(val):
            continue
        if default is None:
            kwds[key] = val.default
        elif key in default:
            kwds[key] = default[key]

    return kwds

def get_methods(
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

        # Change dictionary key, if argument 'key' is given
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

def split_args(text: str) -> Tuple[str, tuple, dict]:
    """Split a function call in the function name, its arguments and keywords.

    Args:
        text: Function call given as valid Python code. Beware: Function
            definitions are no valid function calls.

    Returns:
        A tuple consisting of the function name as string, the arguments as
        tuple and the keywords as dictionary.

    """
    # Check type of 'text'
    check.has_type("first argument 'text'", text, str)

    # Get function name
    try:
        tree = ast.parse(text)
        func = getattr(getattr(getattr(tree.body[0], 'value'), 'func'), 'id')
    except SyntaxError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err
    except AttributeError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err

    # Get tuple with arguments
    astargs = getattr(getattr(tree.body[0], 'value'), 'args')
    largs = []
    for astarg in astargs:
        typ = astarg._fields[0]
        val = getattr(astarg, typ)
        largs.append(val)
    args = tuple(largs)

    # Get dictionary with keywords
    astkwds = getattr(getattr(tree.body[0], 'value'), 'keywords')
    kwds = {}
    for astkw in astkwds:
        key = astkw.arg
        typ = astkw.value._fields[0]
        val = getattr(astkw.value, typ)
        kwds[key] = val

    return func, args, kwds

def wrap_attr(**attr: Any) -> FuncWrapper:
    """Wrap callable with additional attributes.

    Args:
        **attr: Arbitrary attributes

    Returns:
        Wrapper function with additional attributes

    """
    def wrapper(procedure): # type: ignore
        def wrapped_method(self, *args, **kwds): # type: ignore
            return procedure(*args, **kwds)
        def wrapped_function(*args, **kwds): # type: ignore
            return procedure(*args, **kwds)
        if isinstance(procedure, Method):
            wrapped = wrapped_method
        else:
            wrapped = wrapped_function
        for key, val in attr.items():
            setattr(wrapped, key, val)
        wrapped.__doc__ = procedure.__doc__
        return wrapped
    return wrapper

def search(
        ref: Module, pattern: OptStr = None,
        classinfo: ClassInfo = Function, key: OptStr = None, val: OptStr = None,
        groupby: OptStr = None, recursive: bool = True,
        rules: OptStrDictOfTestFuncs = None, **kwds: Any) -> dict:
    """Recursively search for objects within submodules.

    Args:
        ref: Reference to module or package, in which objects are searched.
        pattern: Only objects which names satisfy the wildcard pattern given
            by 'pattern' are returned. The format of the wildcard pattern is
            described in the standard library module `fnmatch`_. If pattern is
            None, then all objects are returned. Default: None
        classinfo: Classinfo given as a class, a type or a tuple containing
            classes, types or other tuples. Only members, which are ether an
            instance or a subclass of classinfo are returned. By default all
            types are allowed.
        key: Name of function attribute which is used as the key for the
            returned dictionary. If 'key' is None, then the fully qualified
            function names are used as keys. Default: None
        val: Name of function attribute which is used as the value for the
            returned dictionary. If 'val' is None, then all attributes of the
            respective objects are returned. Default: None
        groupby: Name of function attribute which is used to group the results.
            If 'groupby' is None, then the results are not grouped. Default:
            None
        recursive: Boolean value which determines if the search is performed
            recursively within all submodules. Default: True
        rules: Dictionary with individual filter rules, used by the attribute
            filter. The form is {<attribute>: <lambda>, ...}, where: <attribute>
            is a string with the attribute name and <lambda> is a boolean valued
            lambda function, which specifies the comparison of the attribute
            value against the argument value. Example: {'tags': lambda arg,
            attr: set(arg) <= set(attr)} By default any attribute, which is not
            in the filter rules is compared to the argument value by equality.
        **kwds: Keyword arguments, that define the attribute filter for the
            returned dictionary. For example if the argument "tags = ['test']"
            is given, then only objects are returned, which have the attribute
            'tags' and the value of the attribute equals ['test']. If, however,
            the filter rule of the above example is given, then any function,
            with attribute 'tags' and a corresponding tag list, that comprises
            'test' is returned.

    Returns:
        Dictionary with function information as specified in the arguments
        'key' and 'val'.

    """
    # Check Arguments
    check.has_opt_type("argument 'pattern'", pattern, str)

    # Get list with submodules
    mnames = [ref.__name__] + get_submodules(ref, recursive=recursive)

    # Create dictionary with member attributes
    fd = {}
    rules = rules or {}
    for mname in mnames:
        minst = get_module(mname)
        if minst is None:
            continue
        d = get_members_dict(
            minst, classinfo=classinfo, pattern=pattern, rules=rules, **kwds)

        # Ignore members if any required attribute is not available
        for name, attr in d.items():
            if key and not key in attr:
                continue
            if val and not val in attr:
                continue
            fd[name] = attr

    # Rename key for returned dictionary
    if key:
        d = {}
        for name, attr in fd.items():
            if key not in attr:
                continue
            kval = attr[key]
            if kval in d:
                continue
            d[kval] = attr
        fd = d

    # Group results
    if groupby:
        fd = ndict.groupby(fd, key=groupby)

    # Set value for returned dictionary
    if val:
        if groupby:
            for gn, group in fd.items():
                for name, attr in group.items():
                    fd[name] = attr[val]
        else:
            for name, attr in fd.items():
                fd[name] = attr[val]

    return fd
