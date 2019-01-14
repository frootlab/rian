# -*- coding: utf-8 -*-
"""Metaclasses and abstract base classes for frequently used patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import abc
import contextlib
from typing import Any, Dict
from nemoa.errors import DisconnectError

#
# Singletons
#

class SingletonMeta(type):
    """Metaclass for Singletons."""
    _store: Dict[type, object] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        if cls not in cls._store:
            cls._store[cls] = super(SingletonMeta, cls).__call__(*args, **kwds)
        return cls._store[cls]

    @classmethod
    def __instancecheck__(mcs, obj: object) -> bool:
        if obj.__class__ is mcs:
            return True
        return isinstance(obj.__class__, mcs)

class SingletonType(metaclass=SingletonMeta):
    """Dummy class for Singleton type checks."""

def singleton_object(cls: SingletonMeta) -> object:
    """Class decorator that instantiates a Singleton class."""
    # Adapt init, hash, repr, and reduce from class to allow instantiation,
    # representation, hashing and pickling
    setattr(cls, '__call__', lambda self, *args, **kwds: self)
    setattr(cls, '__hash__', lambda self: hash(cls))
    setattr(cls, '__repr__', lambda self: cls.__name__)
    setattr(cls, '__reduce__', lambda self: cls.__name__)

    # Instantiate Singleton class and return instance
    obj = cls()
    setattr(obj, '__name__', cls.__name__)
    return obj

#
# Proxies
#

class Proxy(metaclass=abc.ABCMeta):
    """Abstract Base Class for Proxies."""

    _connected: bool

    def __init__(self) -> None:
        """Initialize proxy instance."""
        self._connected = False

    def __del__(self) -> None:
        """Run destructor for instance."""
        with contextlib.suppress(DisconnectError):
            self.disconnect()

    @abc.abstractmethod
    def pull(self) -> None:
        """Pull state changes from source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def push(self) -> None:
        """Push state changes to source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def connect(self, *args: Any, **kwds: Any) -> None:
        """Establish connection to source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Close connection to source."""
        raise NotImplementedError()
