# -*- coding: utf-8 -*-
"""Collection of functions for the organization and handling of algorithms."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common.ntype import (
    Any, Callable, List, Optional, Sequence, Union, Module, OptModule,
    OptStr, OptStrList)

Array = Union[np.ndarray, Sequence[np.ndarray]]

def search(minst: OptModule = None, **kwargs: Any) -> dict:
    """Search for algorithms, that pass given filters.

    Args:
        minst: Module instance, which is used to recursively search in
            submodules for algorithms. Default: Use the module of the caller
            of this function.
        **kwargs: Attributes, which are testet by using the filter rules

    Returns:
        Dictionary with function information.

    """

    from nemoa.common import nmodule

    if minst is None:
        minst = nmodule.objectify(nmodule.curname(-1))
    elif not isinstance(minst, Module):
        raise TypeError("argument 'minst' is required to be a module instance")

    # create filter rules for algorithms attributes
    rules = {
        'tags': lambda a, b: set(a) <= set(b), # requires all
        'classes': lambda a, b: bool(set(a) & set(b)) # requires any
    }

    # search for algorithms
    algs = nmodule.search(minst=minst, rules=rules, **kwargs)

    return algs

def custom(
        name: OptStr = None, category: OptStr = None,
        classes: OptStrList = None, tags: OptStrList = None,
        plot: OptStr = None, **attr: Any
    ) -> Callable:
    """Attribute decorator for custom algorithms.

    For the case, that an algorithm does not fit into the builtin categories
    ('objective', 'sampler', 'statistic', 'association') then a custom
    category is required, which does not prescribe the function arguments
    and return values.

    Args:
        name: Name of the algorithm
        category: Custom category name of the algorithm.
            Supported categories are:
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            The default value None indicates, that that results can not be
            visalized. Supported values are: None, 'Heatmap', 'Histogram',
            'Scatter2D' or 'Graph'

    Returns:
        Decorated function or method.

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # set attributes with metainformation about algorithm
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
        tags: OptStrList = None, optimum: str = 'min',
        scope: str = 'local', plot: OptStr = None, **attr: Any
    ) -> Callable:
    """Attribute decorator for objective functions.

    Objective functions are real valued functions, thet specify the goal
    of an optimization problem. Therby the objective function can describe
    a local or global objective, which is to be minimized or maximized. For
    more information see [1].

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

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Mathematical_optimization

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(data: Array, *args: Any, **kwargs: Any) -> float:
            return func(data, *args, **kwargs)

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
        tags: OptStrList = None, plot: OptStr = 'Histogram', **attr: Any
    ) -> Callable:
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

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Gibbs_sampling

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(data: Array, *args: Any, **kwargs: Any) -> Array:
            return func(data, *args, **kwargs)

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
        tags: OptStrList = None, plot: OptStr = 'Histogram', **attr: Any
    ) -> Callable:
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

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Statistic

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(data: Array, *args: Any, **kwargs: Any) -> Array:
            return func(data, *args, **kwargs)

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
        name: Optional[str] = None, tags: Optional[List[str]] = None,
        classes: Optional[List[str]] = None, plot: Optional[str] = 'Histogram',
        directed: bool = True, signed: bool = True, normal: bool = False,
        **attr: Any
    ) -> Callable:
    """Attribute decorator for statistical measures of association.

    Measures of association refer to a wide variety of coefficients that measure
    the statistical strength of relationships between the variables of interest.
    These measures can be directed / undirected, signed / unsigned and
    normalized or unnormalized. Examples for measures of association are the
    Pearson correlation coefficient, Mutual information or Statistical
    Interactions. For more information see [1].

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

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Correlation_and_dependence

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(data: Array, *args: Any, **kwargs: Any) -> Any:
            return func(data, *args, **kwargs)

        # set attributes with metainformation about algorithm
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
