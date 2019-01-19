# -*- coding: utf-8 -*-
"""Metaclasses and Abstract Base Classes for frequently used patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, Tuple, Optional, IO

#
# Creational Patterns
#

class SingletonMeta(ABCMeta):
    """Metaclass for Singleton Classes.

    Singleton classes only create a single instance per application. This
    creation behaviour is comparable to global variables and used to ensure the
    application global uniqueness and accessibility of an object. Common use
    cases for Singletons comprise logging, sentinel objects and application
    global constants (given as immutable objects).

    """
    _instance: Optional[type] = None

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        if not cls._instance:
            cls._instance = super(SingletonMeta, cls).__call__(*args, **kwds)
        return cls._instance

class Singleton(metaclass=SingletonMeta):
    """Base Class for Singleton Classes.

    The usage of a Singleton base class allows the usage if :func:`isinstance`
    to check the type of an object against Singleton.

    """
    __slots__: list = []

class MultitonMeta(ABCMeta):
    """Metaclass for Multiton Classes.

    Multiton Classes only create a single instance per given arguments. This
    allows a controlled creation of multiple objects, that are globally
    accessible and unique. Multiton classes may be regarded as generalizations
    of Singleton Classes in the sense of a 'Collection of Singletons'. Common
    use cases comprise application global configurations, caching and
    collections of constants (given as immutable objects).

    """
    _registry: Dict[Tuple[type, tuple, Any], object] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        # Create 'fingerprint' of instance. Beware: The fingerprint is only
        # hashable if all given arguments and keywords are hashable. Therupon
        # Check registry for the fingerprint. If the fingerprint is not hashable
        # create and return and an instance of the class. If the the fingerprint
        # could not not be found in the registry, create a class instance, add
        # it to the registry and return the instance.
        try:
            key = (cls, args, frozenset(kwds.items()))
            return cls._registry[key]
        except TypeError as err:
            if 'unhashable' in str(err):
                register = False
            else:
                raise
        except KeyError:
            register = True

        # Create an instance of the class. Note, that if the class does not
        # implement a __init__ method, then it does not accept arguments. In
        # this case a TypeError is raised.
        try:
            obj = super(MultitonMeta, cls).__call__(*args, **kwds)
        except TypeError as err:
            if 'takes no arguments' in str(err):
                obj = super(MultitonMeta, cls).__call__()
            else:
                raise

        # If the fingerprint is hashable, add the instance to the registry and
        # finally return it.
        if register:
            cls._registry[key] = obj
        return obj

class Multiton(metaclass=MultitonMeta):
    """Base Class for Multiton Classes."""
    __slots__: list = []

def objectify(cls: SingletonMeta) -> object:
    """Class decorator that objectifies a Singleton class.

    Args:
        cls: Subclass of the class :class:`Singleton`

    Returns:
        Instance of the given Singleton class

    """
    return cls()

def sentinel(cls: SingletonMeta) -> object:
    """Class decorator that creates a Sentinel from a Singleton class.

    Args:
        cls: Subclass of the class :class:`Singleton`

    Returns:
        Instance of the given Singleton class, which adopts a class like
        behaviour, including the ability of instantion, hashing and its
        representation.

    """
    # Wrap class methods to itself (in the original class), to provide a
    # class like behaviour of the sentinel object, including the ability of
    # instantion, hashing and its representation.
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

class Proxy(ABC):
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
