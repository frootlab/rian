# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from types import FunctionType, ModuleType
from typing import Optional

def curname(frame: int = 0) -> str:
    """Get name of module, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack.
            default: 0

    Returns:
        String with name of module.

    """

    if not isinstance(frame, int):
        raise TypeError(f"frame requires type 'int', not '{type(frame)}'")
    if frame > 0:
        raise ValueError("frame is required to be zero or negative")

    import inspect

    caller = inspect.currentframe()

    for i in range(abs(frame - 1)):
        if caller is None: break
        caller = caller.f_back

    if caller is None: return ''
    mname = caller.f_globals['__name__']

    return mname

def callername(frame: int = 0) -> str:
    """Get name of the callable, which calls this function.

    Args:
        frame: Frame index relative to the current frame in the callstack,
            which is identified with 0. Negative values consecutively identify
            previous modules within the callstack.
            default: 0

    Returns:
        String with name of the caller.

    """

    if not isinstance(frame, int):
        raise TypeError(f"frame requires type 'int', not '{type(frame)}'")
    if frame > 0:
        raise ValueError("frame is required to be zero or negative")

    import inspect

    stack = inspect.stack()[abs(frame - 1)]
    mname = inspect.getmodule(stack[0]).__name__
    fname = stack[3]

    return '.'.join([mname, fname])

def submodules(minst: Optional[ModuleType] = None,
    recursive: bool = False) -> list:
    """Get list with submodule names.

    Args:
        minst: Module instance to search for submodules
            default: Use current module, which called this function
        recursive: Search recursively within submodules
            default: Do not search recursively

    Returns:
        List with submodule names.

    """

    if minst is None: minst = get_module(curname(-1))
    elif not isinstance(minst, ModuleType):
        raise TypeError('minst is required to be of ModuleType')

    # check if module is a package or a file
    if not hasattr(minst, '__path__'): return []

    import pkgutil

    mpref = minst.__name__ + '.'
    mpath = minst.__path__

    mlist = []
    for path, name, ispkg in pkgutil.iter_modules(mpath):
        mlist += [mpref + name]
        if not ispkg or not recursive: continue
        mlist += submodules(get_module(mpref + name), recursive = True)

    return mlist

def get_submodule(s: str) -> Optional[ModuleType]:
    """Get module instance, by name of current submodule."""

    return get_module('.'.join([curname(-1), s]))

def get_module(s: str) -> Optional[ModuleType]:
    """Get module instance for a given qualified module name."""

    import importlib

    try: minst = importlib.import_module(s)
    except ModuleNotFoundError: return None

    return minst

def get_functions(minst: Optional[ModuleType] = None, details: bool = False,
    filters: dict = {}, **kwargs) -> list:
    """Get filtered list of function names within given module instance.

    Args:
        minst: Module instance to search for submodules
            default: Use current module, which called this function
        details:
            default: False
        filters:
            default: {}

    Returns:
        List with full qualified function names.

    Example:
        all = lambda a, b: frozenset(a) <= frozenset(b)
        get_functions(filters = {'tags': all}, tags = ['fast', 'stable'])

    """

    if minst is None: minst = get_module(curname(-1))
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

def locate_functions(minst: Optional[ModuleType] = None, recursive: bool = True,
    details: bool = False, filters: dict = {},  **kwargs):
    """Recursively search for functions within submodules."""

    if minst is None: minst = get_module(curname(-1))
    elif not isinstance(minst, ModuleType): raise TypeError(
        "first argument is required to be of ModuleType")

    mnames = submodules(minst, recursive = recursive)

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

def get_function(fname: str) -> Optional[FunctionType]:
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
