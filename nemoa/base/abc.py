# -*- coding: utf-8 -*-
"""Metaclasses and Abstract Base Classes for frequently used design patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, Tuple, Optional, IO

#
# Creational Design Patterns
#

class SingletonMeta(ABCMeta):
    """Metaclass for Singleton Classes.

    Singleton Classes create a single instance per application.

    Args:

    """
    _registry: Dict[type, object] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        try:
            obj = cls._registry[cls]
        except KeyError:
            obj = super(SingletonMeta, cls).__call__(*args, **kwds)
            cls._registry[cls] = obj
        return obj

    @classmethod
    def __instancecheck__(mcs, obj: object) -> bool:
        if obj.__class__ is mcs:
            return True
        return isinstance(obj.__class__, mcs)

class Singleton(metaclass=SingletonMeta):
    """Base Class for Singleton Classes."""
    __slots__: list = []

def singleton_object(cls: SingletonMeta) -> object:
    """Class decorator that instantiates a Singleton class.

    Args:

    Return:

    """
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

class MultitonMeta(ABCMeta):
    """Metaclass for Multiton Classes.

    Moltiton Classes allow the controlled creation of multiple instances, by
    comparing the given arguments and keyword arguments with entries in a
    registry.

    """
    _registry: Dict[Tuple[type, tuple, Any], object] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        # Create 'fingerprint' of instance. Beware: The fingerprint is only
        # hashable if all given arguments and keywords are hashable
        try:
            key = (cls, args, frozenset(kwds.items()))
        except TypeError:
            print(cls, args, kwds) # TODO
            raise

        # Check registry for the fingerprint. If the fingerprint is not hashable
        # create and return and an instance of the class. If the the fingerprint
        # could not not be found in the registry, create a class instance, add
        # it to the registry and return the instance.
        try:
            return cls._registry[key]
        except TypeError:
            hashable = False
        except KeyError:
            hashable = True

        # Create an instance of the class. (Note, that if the class does not
        # implement a __init__ method, then it does not accept arguments)
        try:
            obj = super(MultitonMeta, cls).__call__(*args, **kwds)
        except TypeError:
            obj = super(MultitonMeta, cls).__call__()

        # If the fingerprint is hashable, add an entry to the registry and
        # finally return the instance.
        if hashable:
            cls._registry[key] = obj
        return obj

    @classmethod
    def __instancecheck__(mcs, obj: object) -> bool:
        if obj.__class__ is mcs:
            return True
        return isinstance(obj.__class__, mcs)

class Multiton(metaclass=MultitonMeta):
    """Base Class for Multiton Classes."""
    __slots__: list = []

#
# Proxies
#

class Proxy(metaclass=ABCMeta):
    """Abstract Base Class for Proxies."""

    _connected: bool

    def __init__(self) -> None:
        """Initialize proxy instance."""
        self._connected = False

    def __del__(self) -> None:
        """Run destructor for instance."""
        try:
            self.disconnect()
        finally:
            pass

    @abstractmethod
    def pull(self) -> None:
        """Pull state changes from source."""
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a method 'pull'")

    @abstractmethod
    def push(self) -> None:
        """Push state changes to source."""
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a method 'push'")

    @abstractmethod
    def connect(self, *args: Any, **kwds: Any) -> None:
        """Establish connection to source."""
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a method 'connect'")

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to source."""
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a method 'disconnect'")

#
# Accessor
#

class FileAccessor(ABC):
    """File Accessor/Opener Base Class."""

    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a property 'name'")

    @abstractmethod
    def open(self, *args: Any, **kwds: Any) -> IO[Any]:
        raise NotImplementedError(
            f"'{type(self).__name__}' is required "
            "to implement a method 'open'")
