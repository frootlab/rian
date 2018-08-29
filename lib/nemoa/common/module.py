# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from types import FunctionType, ModuleType

def get_curname(frame: int = 0):
    """Get name of module, which calls this function.

    Kwargs:
        frame (integer, optional): Frame index relative to the current frame
            in the callstack, which is identified with 0. Negative values
            consecutively identify previous modules within the callstack.
            default: 0

    Returns:
        String with name of module.

    """

    if not isinstance(frame, int) or frame > 0: raise TypeError(
        'First argument is required to be a negative integer')

    import inspect

    caller = inspect.currentframe()

    for i in range(abs(frame - 1)):
        if caller is None: break
        caller = caller.f_back

    if caller is None: return ''
    mname = caller.f_globals['__name__']

    return mname

def get_submodules(minst: ModuleType = None, recursive: bool = False):
    """Get list with submodule names.

    Kwargs:
        minst (ModuleType, optional): Module instance to search for submodules
            default: Use current module, which called this function
        recursive (bool, optional): Search recursively within submodules
            default: Do not search recursively

    Returns:
        List with submodule names.

    """

    if minst is None: minst = get_module(get_curname(-1))
    elif not isinstance(minst, ModuleType): raise TypeError(
        'First argument is required to be of ModuleType')

    # check if module is a package or a file
    if not hasattr(minst, '__path__'): return []

    import pkgutil

    mpref = minst.__name__ + '.'
    mpath = minst.__path__

    mlist = []
    for path, name, ispkg in pkgutil.iter_modules(mpath):
        mlist += [mpref + name]
        if not ispkg or not recursive: continue
        mlist += get_submodules(get_module(mpref + name), recursive = True)

    return mlist

def get_module(mname: str):
    """Get module instance for a given qualified module name."""

    import importlib

    try:
        minst = importlib.import_module(mname)
    except ModuleNotFoundError:
        return None

    return minst

def get_functions(minst: ModuleType = None, details: bool = False,
    filters: dict = {}, **kwargs):
    """Get filtered list of function names within given module instance.

    Kwargs:
        minst (ModuleType, optional): Module instance to search for submodules
            default: Use current module, which called this function
        details (bool, optional):
            default: False
        filters (dict, optional):
            default: {}

    Returns:
        List with full qualified function names.

    Example:
        all = lambda a, b: frozenset(a) <= frozenset(b)
        get_functions(filters = {'tags': all}, tags = ['fast', 'stable'])

    """

    if minst is None: minst = get_module(get_curname(-1))
    elif not isinstance(minst, ModuleType): raise TypeError(
        "first argument is required to be of ModuleType")

    import inspect

    funcs = inspect.getmembers(minst, inspect.isfunction)
    pref = minst.__name__ + '.'

    if not details and not kwargs:
        return [pref + name for name, ref in funcs]

    # create dictionary with function attributes
    if len(funcs) == 0: return {}
    fdetails = {}
    for name, ref in funcs:
        # set default attributes
        fdict = {'name': name, 'about': get_shortdoc(ref), 'reference': ref }
        # update attributes
        for key, val in ref.__dict__.items():
            fdict[key] = val
        # filter entry by attributes
        passed = True
        for key, val in kwargs.items():
            if not key in fdict:
                passed = False
                break
            if key in filters:
                if filters[key](val, fdict[key]): continue
                passed = False
                break
            if val == fdict[key]: continue
            passed = False
            break
        if passed: fdetails[pref + name] = fdict

    if details: return fdetails

    return fdetails.keys()

def locate_functions(minst: ModuleType = None, recursive = True,
    details: bool = False, filters: dict = {},  **kwargs):
    """Recursively search for functions within submodules."""

    if minst is None: minst = get_module(get_curname(-1))
    elif not isinstance(minst, ModuleType): raise TypeError(
        "first argument is required to be of ModuleType")

    mnames = get_submodules(minst, recursive = recursive)

    # create list with qualified function names
    if not details:
        funcs = []
        for mname in mnames:
            subinst = get_module(mname)
            if subinst is None: continue
            funcs += get_functions(subinst, details = False,
                filters = filters, **kwargs)
        return funcs

    # create dictionary with function attributes
    funcs = {}
    for mname in mnames:
        subinst = get_module(mname)
        if subinst is None: continue
        fdict = get_functions(subinst, details = True,
            filters = filters, **kwargs)
        for key, val in fdict.items():
            funcs[key] = val

    return funcs

def get_function(fname: str):
    """Return function instance for a given full qualified function name.

    Example:
        get_function("nemoa.common.module.get_function")

    """

    minst = get_module('.'.join(fname.split('.')[:-1]))
    if minst is None: return None
    finst = getattr(minst, fname.split('.')[-1])

    return finst

def get_shortdoc(finst: FunctionType):
    """Get short description of a given function instance."""

    if finst.__doc__ is None: return ""
    return finst.__doc__.split('\n', 1)[0].strip(' .')

def get_kwargs(finst: FunctionType, d: dict = None):
    """Get the keyword arguments of a given function instance."""

    if not isinstance(finst, FunctionType): raise TypeError(
        'first argument is required to be of FunctionType')

    import inspect

    all = inspect.signature(finst).parameters
    l = [key for key, val in all.items() if '=' in str(val)]

    if d is None: return l

    kwargs = {key: d.get(key) for key in l if key in d}

    return kwargs


# deprecated

def get_methods(cinst: type, attribute = None, grouping = None,
    prefix: str = '', removeprefix: bool = True, renamekey = None):
    """Get the methods of a given class instance.

    Args:
        cinst: instance of class

    Kwargs:
        prefix (string): only methods with given prefix are returned.
        removeprefix (bool): remove prefix in dictionary keys if True.
        renamekey (string):
        attribute (string):
        grouping (string):

    Returns:
        Dictionary containing the methods of an instance including
        their attributes.

    """

    import inspect

    # get references from module inspection and filter prefix
    methods = dict(inspect.getmembers(cinst, inspect.ismethod))
    if prefix:
        for name in list(methods.keys()):
            if not name.startswith(prefix) or name == prefix:
                del methods[name]
                continue
            if removeprefix:
                methods[name[len(prefix):]] = methods.pop(name)
    if not grouping and not renamekey and attribute == 'reference':
        return methods

    # get attributes from decorators
    methoddict = {}
    for name, method in methods.items():
        methoddict[name] = { 'reference': method, 'about': '' }

        # copy method attributes and docstring to dictionary
        for attr in method.__dict__:
            methoddict[name][attr] = method.__dict__[attr]
        if isinstance(method.__doc__, str):
            methoddict[name]['about'] = \
                method.__doc__.split('\n', 1)[0].strip(' .')

        # filter methods by required attributes
        if renamekey and not renamekey in methoddict[name]:
            del methoddict[name]
        elif attribute and not attribute in methoddict[name]:
            del methoddict[name]
        elif grouping and not grouping in methoddict[name]:
            del methoddict[name]
    methods = methoddict

    # (optional) group methods, rename key and reduce to attribute
    if grouping:
        groups = {}
        for ukey, udata in methods.items():
            group = udata[grouping]
            key = udata[renamekey] if renamekey else ukey
            if group not in groups: groups[group] = {}
            if key in groups[group]: continue
            if attribute: groups[group][key] = udata[attribute]
            else: groups[group][key] = udata
        methods = groups
    elif renamekey:
        renamend = {}
        for ukey, udata in methods.items():
            key = udata[renamekey]
            if key in renamend: continue
            if attribute: renamend[key] = udata[attribute]
            else: renamend[key] = udata
        methods = renamend

    return methods
