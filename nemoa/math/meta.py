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

from nemoa.base import entity, this
from nemoa.types import Any, FuncWrapper, OptModule, OptStr, OptStrList

def search(module: OptModule = None, **kwds: Any) -> dict:
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
    module = module or this.get_caller_module()

    # Create filter rules for algorithm attributes
    rules = {
        'tags': lambda a, b: set(a) <= set(b), # requires all
        'classes': lambda a, b: bool(set(a) & set(b))} # requires any

    # Search for algorithms
    return entity.search(ref=module, rules=rules, **kwds)

def custom(
        name: OptStr = None, category: OptStr = None,
        classes: OptStrList = None, tags: OptStrList = None,
        plot: OptStr = None, **attr: Any) -> FuncWrapper:
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
        plot: OptStr = None, **attr: Any) -> FuncWrapper:
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
        **attr: Any) -> FuncWrapper:
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
        **attr: Any) -> FuncWrapper:
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
        **attr: Any) -> FuncWrapper:
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
