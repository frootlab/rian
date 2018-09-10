# -*- coding: utf-8 -*-
"""Collection of frequently used algorithm decorators."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Callable, List, Optional

def generic(name: Optional[str] = None, category: Optional[str] = None,
    classes: Optional[List[str]] = None, tags: Optional[List[str]] = None,
    plot: Optional[str] = None, **attr: Any) -> Callable:
    """Generic attribute decorator for algorithms.

    Args:
        name: Name of the algorithm
        category: Category name of the algorithm, which is used to specify the
            required data, as well as the returned results of the algorithm.
            Supported categories are: 'objective', 'sampler', 'statistics',
            'association'
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
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper


def objective(name: Optional[str] = None, classes: Optional[List[str]] = None,
    tags: Optional[List[str]] = None, optimum: str = 'min',
    scope: str = 'local', plot: Optional[str] = None, **attr: Any) -> Callable:
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

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

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
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper


def sampler(name: Optional[str] = None, classes: Optional[List[str]] = None,
    tags: Optional[List[str]] = None, plot: Optional[str] = 'Histogram',
    **attr: Any) -> Callable:
    """Attribute decorator for statistical samplers.

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

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'sampler')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper


def statistics(name: Optional[str] = None, classes: Optional[List[str]] = None,
    tags: Optional[List[str]] = None, plot: Optional[str] = 'Histogram',
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

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Statistic

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'statistics')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper


def association(name: Optional[str] = None, classes: Optional[List[str]] = None,
    tags: Optional[List[str]] = None, plot: Optional[str] = 'Histogram',
    directed: bool = True, signed: bool = True, normal: bool = False,
    **attr: Any) -> Callable:
    """Attribute decorator for statistical association measures.

    Association measures are pairwise statistical relationships, whether causal
    or not, between given random variables, which are realized by a sample.
    For more information see [1].

    Args:
        name: Name of the association measure
        tags: List of strings, that describe the algorithm and allow it to be
            found by browsing or searching
        classes: Optional list of model class names, that can be processed by
            the algorithm
        plot: Name of plot class, which is used to interpret the results.
            Supported values are: None, 'Heatmap', 'Histogram', 'Scatter2D' or
            'Graph'. The default value is 'Heatmap'
        directed: Boolean value which indicates if the association measure is
            dictected. Default is True.
        signed: Boolean value which indicates if the association measure is
            signed. Default is True.
        normal: Boolean value which indicates if the association measure is
            normalized. Default is False.

    Returns:
        Decorated function or method.

    References:
        [1] https://en.wikipedia.org/wiki/Correlation_and_dependence

    """

    def wrapper(func: Callable) -> Callable:

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name or func.__name__)
        setattr(wrapped, 'category', 'sampler')
        setattr(wrapped, 'classes', classes or [])
        setattr(wrapped, 'plot', plot)
        setattr(wrapped, 'directed', directed)
        setattr(wrapped, 'signed', signed)
        setattr(wrapped, 'normal', normal)
        setattr(wrapped, 'tags', tags or [])
        setattr(wrapped, 'func', func)
        wrapped.__doc__ = func.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper
