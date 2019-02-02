# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Metaclasses and Abstract Base Classes for frequently used design patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, Tuple, Optional, IO

#
# Creational Patterns
#

class IsolatedMeta(ABCMeta):
    """Metaclass for isolated classes.

    Isolated classes create a new subclass for any instance to allow the
    modification of class methods without side effects. Common use cases for
    isolated classes include Singletons, Multitons and built classes, that avoid
    generic programming in favor of higher efficiency or lower memory usage.

    """
    def __call__(cls, *args: Any, **kwds: Any) -> object:
        # Create new subclass of the given class. Set the attribute '__slots__'
        # to an empty list, to allow the usage of slots.
        subcls = IsolatedMeta(cls.__name__, (cls, ), {'__slots__': []})

        # Create an instance of the new subclass. Note, that if the class does
        # not implement an __init__ method a TypeError is raised. In this case
        # the class is called without arguments.
        try:
            return super(IsolatedMeta, subcls).__call__(*args, **kwds)
        except TypeError as err:
            if 'takes no arguments' in str(err):
                return super(IsolatedMeta, subcls).__call__()
            raise

class Isolated(metaclass=IsolatedMeta):
    """Abstract Base Class for per-instance isolated classes.

    The Isolated base class is a helper class, which is included to allow
    instance checking against the IsolatedMeta metaclass.

    """
    __slots__: list = []

class SingletonMeta(IsolatedMeta):
    """Metaclass for Singletons.

    Singleton classes only create a single instance per application and
    therefore by definition are special case of isolated classes. This creation
    pattern ensures the application global uniqueness and accessibility of
    instances, comparably to global variables. Common use cases comprise
    logging, sentinel objects and application global constants (given as
    immutable objects).

    """
    _instance: Optional[object] = None

    def __call__(cls, *args: Any, **kwds: Any) -> object:
        if not cls._instance:

            # Create an instance of the class. Note, that if the class does not
            # implement an __init__ method a TypeError is raised. In this case
            # the class is called without arguments.
            try:
                obj = super(SingletonMeta, cls).__call__(*args, **kwds)
            except TypeError as err:
                if 'takes no arguments' in str(err):
                    obj = super(SingletonMeta, cls).__call__()
                else:
                    raise
            cls._instance = obj

        return cls._instance

class Singleton(metaclass=SingletonMeta):
    """Abstract Base Class for Singletons.

    The Singleton base class is a helper class, which is included to allow
    instance checking against the SingletonMeta metaclass.

    """
    __slots__: list = []

class MultitonMeta(IsolatedMeta):
    """Metaclass for Multitons.

    Multiton Classes only create a single instance per given arguments by using
    a new subclass for class isolation. This allows a controlled creation of
    multiple distinct objects, that are globally accessible and unique. Multiton
    classes may be regarded as a generalization of Singletons in the sense of
    'Collections of Singletons'. Common use cases comprise application global
    configurations, caching and collections of constants (given as immutable
    objects).

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

        # Create new subclass of the given class. Set the attribute '__slots__'
        # to an empty list, to allow the usage of slots.
        subcls = MultitonMeta(cls.__name__, (cls, ), {'__slots__': []})

        # Create an instance of the class. Note, that if the class does not
        # implement an __init__ method a TypeError is raised. In this case the
        # class is called without arguments.
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
    """Abstract Base Class for Multiton Classes.

    The Multiton base class is a helper class, which is included to allow
    instance checking against the MultitonMeta metaclass.

    """
    __slots__: list = []

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
