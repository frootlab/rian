# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import inspect

def objective(name: str, title: str = '', tags: list = [], classes: list = [],
    optimum: str = 'min', **attr):
    """Attribute decorator for objective functions."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name)
        setattr(wrapped, 'title', title)
        setattr(wrapped, 'func', method)
        setattr(wrapped, 'classes', classes)
        setattr(wrapped, 'category', 'objective')
        setattr(wrapped, 'optimum', optimum)
        setattr(wrapped, 'tags', tags)
        wrapped.__doc__ = method.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper

def sampler(name: str, title: str = '', tags: list = [], classes: list = [],
    plot: str = 'histogram', **attr):
    """Attribute decorator for sampler."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name)
        setattr(wrapped, 'title', title)
        setattr(wrapped, 'func', method)
        setattr(wrapped, 'classes', classes)
        setattr(wrapped, 'category', 'sampler')
        setattr(wrapped, 'tags', tags)
        setattr(wrapped, 'plot', plot)
        wrapped.__doc__ = method.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper

def statistics(name: str, title: str = '', tags: list = [], classes: list = [],
    plot: str = 'histogram', **attr):
    """Attribute decorator for sample statistics."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name)
        setattr(wrapped, 'title', title)
        setattr(wrapped, 'func', method)
        setattr(wrapped, 'classes', classes)
        setattr(wrapped, 'category', 'statistics')
        setattr(wrapped, 'tags', tags)
        setattr(wrapped, 'plot', plot)
        wrapped.__doc__ = method.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper

def association(name: str, title: str = '', tags: list = [], classes: list = [],
    directed: bool = True, signed: bool = True, normal: bool = False,
    plot: str = 'heatmap', **attr):
    """Attribute decorator for association measures."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name)
        setattr(wrapped, 'title', title)
        setattr(wrapped, 'func', method)
        setattr(wrapped, 'classes', classes)
        setattr(wrapped, 'category', 'association')
        setattr(wrapped, 'tags', tags)
        setattr(wrapped, 'directed', directed)
        setattr(wrapped, 'signed', signed)
        setattr(wrapped, 'normal', normal)
        setattr(wrapped, 'plot', plot)
        wrapped.__doc__ = method.__doc__

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper















def attributes(**attr):
    """Generic attribute decorator for arbitrary class methods."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.items():
            setattr(wrapped, key, val)

        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper

def algorithm(**attr):
    """Attribute decorator for algorithm methods."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        for key, val in attr.items():
            setattr(wrapped, key, val)

        setattr(wrapped, 'func', method)
        wrapped.__doc__ = method.__doc__
        return wrapped

    return wrapper

def inference(name: str, title: str = '', category: str = '', tags: list = [],
    require: list = [], args: str = 'none',
    formater: type(abs) = lambda val: '%.3f' % (val), **attr):
    """Attribute decorator for inference functions."""

    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        # set attributes with metainformation about algorithm
        setattr(wrapped, 'name', name)
        setattr(wrapped, 'title', title)
        setattr(wrapped, 'category', category)
        if tags: setattr(wrapped, 'tags', ['inference'] + tags)
        else: setattr(wrapped, 'tags', ['inference'])
        wrapped.__doc__ = method.__doc__

        # information about algorithm
        setattr(wrapped, 'require', require)
        setattr(wrapped, 'args', args)
        setattr(wrapped, 'formater', formater)
        setattr(wrapped, 'func', method)

        # set additional attributes
        for key, val in attr.items(): setattr(wrapped, key, val)

        return wrapped

    return wrapper
