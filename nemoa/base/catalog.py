# -*- coding: utf-8 -*-
"""Organization and handling of algorithms.

.. References:
.. _Objective functions:
    https://en.wikipedia.org/wiki/Objective_function

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
import fnmatch
from typing import Any, Callable, Dict, Hashable, List, Optional, Union
from nemoa.base import abc, pkg, stack
from nemoa.types import Module, OptStr, OptStrList, OptKey

OptModule = Optional[Module]

#
# Cards
#

REGISTERED = 0
VERIFIED = 1

@dataclasses.dataclass
class Card:
    """Class for Catalog Cards."""
    category: OptKey
    name: str
    module: str
    meta: Dict[str, Any]
    kwds: Dict[str, Any]
    reference: object
    state: int = REGISTERED

#
# Categories
#

class Category(abc.ABC):
    """Abstract Base class for catalog categories."""

def category(cls: type) -> Category:
    """Decorate class as catalog Category."""

    if not hasattr(cls, 'id'):
        raise AttributeError(
            f"{cls.__name__} is required to have an attribute 'id'")
    if not isinstance(cls.id, Hashable): # type: ignore
        raise TypeError(
            f"{cls.__name__}.id is required to be hashable")

    # Create category class as dataclass, using the base class Category
    space = dict(cls.__dict__)
    cid = space['id']
    space.pop('id')
    space['__annotations__'].pop('id', None)
    cat = type(cls.__name__, (cls, Category), dict(cls.__dict__))
    cat = dataclasses.dataclass(frozen=True)(cat)

    # Register the category if it is not yet registered in the Catalog
    catalog = Manager()
    if not catalog.has_category(cls.id): # type: ignore
        catalog.add_category(cls.id, cat) # type: ignore

    return cat # type: ignore

#
# Catalog Manager
#

class Manager(abc.Singleton):
    """Singleton Class for Catalog Manager."""
    _records: Dict[str, Card]
    _categories: Dict[OptKey, Category]

    def __init__(self) -> None:
        self._records = {}
        self._categories = {}

    def add_category(self, cid: OptKey, cat: Category) -> None:
        if cid in self._categories:
            raise ValueError() # TODO
        self._categories[cid] = cat

    def del_category(self, cid: OptKey) -> None:
        self._categories.pop(cid, None)

    def get_category(self, cid: OptKey) -> Category:
        return self._categories[cid]

    def has_category(self, cid: OptKey) -> bool:
        return cid in self._categories

    def add(
            self, cid: OptKey, kwds: dict, obj: Callable) -> None:
        path = obj.__module__ + '.' + obj.__qualname__
        rec = Card(
            category=cid, name=obj.__name__, module=obj.__module__,
            meta={}, kwds=kwds, reference=obj)
        if cid in self._categories:
            self.verify(rec)
        self._records[path] = rec

    def get(self, path: Union[str, Callable]) -> Card:
        if callable(path):
            path = path.__module__ + '.' + path.__qualname__
        rec = self._records[path]
        if rec.state != VERIFIED:
            self.verify(rec)
        return rec

    def verify(self, rec: Card) -> None:
        if rec.state == VERIFIED:
            return

        cat = self._categories[rec.category]
        meta = cat(**rec.kwds) # type: ignore
        rec.meta.update(dataclasses.asdict(meta))
        rec.state = VERIFIED

    def search(
            self, path: OptStr = None,
            category: OptKey = None, # pylint: disable=W0621
            **kwds: Any) -> List[Card]:
        results: List[Card] = []
        for key, rec in self._records.items():
            if rec.state != VERIFIED:
                self.verify(rec)
            if path and not fnmatch.fnmatch(key, path):
                continue
            if category and rec.category != category:
                continue
            if kwds and not kwds.items() <= rec.meta.items():
                continue
            results.append(rec)
        return results

#
# Helper functions
#

def register(cid: OptKey = None, **kwds: Any) -> Callable:
    """Decorator to register classes and functions in the catalog."""
    def add(obj: Callable) -> Callable:
        Manager().add(cid=cid, kwds=kwds, obj=obj)
        return obj
    return add

def search(
        path: OptStr = None, category: OptKey = None, # pylint: disable=W0621
        **kwds: Any) -> List[Card]:
    return Manager().search(path=path, category=category, **kwds)

def pick(
        path: OptStr = None, category: OptKey = None, # pylint: disable=W0621
        **kwds: Any) -> Card:
    results = Manager().search(path=path, category=category, **kwds)
    if not results:
        raise ValueError(f"no entry has been found")
    if len(results) > 1:
        raise ValueError(f"the search query is not unique")
    return results[0]

def search_old(module: OptModule = None, **kwds: Any) -> dict:
    """Search for algorithms, that pass given filters.

    Args:
        module: Module instance, which is used to recursively search in
            submodules for algorithms. Default: Use the module of the caller
            of this function.
        **kwds: Attributes, which are testet by using the filter rules

    Returns:
        Dictionary with function information.

    """
    # Set default value of 'module' to module of caller
    module = module or stack.get_caller_module()

    # Create filter rules for attributes
    rules = {
        'tags': lambda a, b: set(a) <= set(b), # requires all
        'classes': lambda a, b: bool(set(a) & set(b))} # requires any

    # Search for algorithms
    return pkg.search(module=module, rules=rules, **kwds)

#
# Operator Decorators
#

def custom(
        name: OptStr = None, category: OptStr = None,
        classes: OptStrList = None, tags: OptStrList = None,
        plot: OptStr = None, **attr: Any) -> Callable:
    """Attribute decorator for custom algorithms.

    For the case, that an algorithm does not fit into the builtin categories
    ('objective', 'sampler', 'statistic', 'association') then a custom
    category is required, which does not prescribe the function arguments
    and return values.

    Args:
        name: Name of the algorithm
        category: Custom category name for the algorithm.
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            The default value None indicates, that that results can not be
            visalized. Supported values are: None, 'Heatmap', 'Histogram',
            'Scatter2D' or 'Graph'
        **attr: Supplementary user attributes, with the purpose to identify and
            characterize the algorithm by their respective values.

    Returns:
        Decorated function or method.

    """
    def wrapper(func): # type: ignore
        def wrapped(*args, **kwds): # type: ignore
            return func(*args, **kwds)

        # Set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', category)
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items():
            setattr(wrapped, key, val)

        return wrapped

    return wrapper

def objective(
        name: OptStr = None, classes: OptStrList = None,
        tags: OptStrList = None, optimum: str = 'min', scope: str = 'local',
        plot: OptStr = None, **attr: Any) -> Callable:
    """Attribute decorator for objective functions.

    `Objective functions` are scalar functions, thet specify the goal of an
    optimization problem. Thereby the objective function identifies local or
    global objectives by it's extremal points, which allows the application
    of approximations.

    Args:
        name: Name of the algorithm
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            The default value None indicates, that that results can not be
            visalized. Supported values are: None, 'Heatmap', 'Histogram',
            'Scatter2D' or 'Graph'
        scope: Scope of optimizer: Ether 'local' or 'global'
        optimum: String describung the optimum of the objective functions.
            Supported values are 'min' and 'max'
        **attr: Supplementary user attributes, with the purpose to identify and
            characterize the algorithm by their respective values.

    Returns:
        Decorated function or method.

    """
    def wrapper(func): # type: ignore
        def wrapped(data, *args, **kwds): # type: ignore
            return func(data, *args, **kwds)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'objective')
        setattr(wrapped, 'optimum', optimum)
        setattr(wrapped, 'scope', scope)
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items():
            setattr(wrapped, key, val)

        return wrapped

    return wrapper

def sampler(
        name: OptStr = None, classes: OptStrList = None,
        tags: OptStrList = None, plot: OptStr = 'Histogram',
        **attr: Any) -> Callable:
    """Attribute decorator for statistical samplers.

    Statistical samplers are random functions, that generate samples from
    a desired posterior distribution in Bayesian data analysis. Thereby the
    different approaches exploit properties of the underlying dependency
    structure. For more information see e.g. [1]

    Args:
        name: Name of the algorithm
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            Supported values are: None, 'Heatmap', 'Histogram', 'Scatter2D' or
            'Graph'. The default value is 'Histogram'
        **attr: Supplementary user attributes, with the purpose to identify and
            characterize the algorithm by their respective values.

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Gibbs_sampling

    """
    def wrapper(func): # type: ignore
        def wrapped(data, *args, **kwds): # type: ignore
            return func(data, *args, **kwds)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'sampler')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items():
            setattr(wrapped, key, val)

        return wrapped

    return wrapper

def statistic(
        name: OptStr = None, classes: OptStrList = None,
        tags: OptStrList = None, plot: OptStr = 'Histogram',
        **attr: Any) -> Callable:
    """Attribute decorator for sample statistics.

    Sample statistics are measures of some attribute of the individual columns
    of a sample, e.g. the arithmetic mean values. For more information see [1]

    Args:
        name: Name of the algorithm
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            Supported values are: None, 'Heatmap', 'Histogram', 'Scatter2D' or
            'Graph'. The default value is 'Histogram'
        **attr: Supplementary user attributes, with the purpose to identify and
            characterize the algorithm by their respective values.

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Statistic

    """
    def wrapper(func): # type: ignore
        def wrapped(data, *args, **kwds): # type: ignore
            return func(data, *args, **kwds)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'statistic')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items():
            setattr(wrapped, key, val)

        return wrapped

    return wrapper

def association(
        name: OptStr = None, tags: OptStrList = None,
        classes: OptStrList = None, plot: OptStr = 'Histogram',
        directed: bool = True, signed: bool = True, normal: bool = False,
        **attr: Any) -> Callable:
    """Attribute decorator for :term:`association measure`.

    Args:
        name: Name of the measure of association
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching.
        classes: Optional list of model class names, that can be processed by
            the algorithm.
        plot: Name of plot class, which is used to interpret the results.
            Supported values are: None, 'Heatmap', 'Histogram', 'Scatter2D' or
            'Graph'. Default: 'Heatmap'.
        directed: Boolean value which indicates if the measure of association is
            dictected. Default: True.
        signed: Boolean value which indicates if the measure of association is
            signed. Default: True.
        normal: Boolean value which indicates if the measure of association is
            normalized. Default: False.
        **attr: Supplementary user attributes, with the purpose to identify and
            characterize the algorithm by their respective values.

    Returns:
        Decorated function or method.

    """
    def wrapper(func): # type: ignore
        def wrapped(data, *args, **kwds): # type: ignore
            return func(data, *args, **kwds)
    # def wrapper(func: NpArrayFunc) -> NpArrayFunc:
    #     def wrapped(data: NpArrayLike, *args: Any, **kwds: Any) -> NpArray:
    #         return func(data, *args, **kwds)

        # Set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'association')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'directed', directed)
        setattr(wrapped, 'signed', signed)
        setattr(wrapped, 'normal', normal)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items():
            setattr(wrapped, key, val)

        return wrapped

    return wrapper
