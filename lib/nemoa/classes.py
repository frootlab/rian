# -*- coding: utf-8 -*-
"""Classes."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod

from nemoa.types import (
    Any, ClassVar, Dict, FileOrPathLike, Method, OptClassInfo, OptDict,
    OptCallable, OptStr, OptType, StrDict, Tuple)

# Descriptors for binding class instance attributes: When an instance of a class
# contains a descriptor class as a method, the descriptor class defines the
# accessor and mutator methods of an attribute, which is identified with the
# method's name.

class Attr:
    """Generic Descriptor Class for Attributes.

    Args:
        vtype:
        bind:
        key:
        getter:
        setter:
        default:

    """

    name: str
    attr: dict

    store: OptDict = None
    key: OptStr = None
    classinfo: OptClassInfo = None
    getter: OptCallable = None
    setter: OptCallable = None
    default: Any = None

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, getter: OptStr = None,
            setter: OptStr = None) -> None:
        """Set attribute names of dictionary, getter, setter, etc."""
        self.attr = {
            'dict': bind, 'key': key, 'getter': getter, 'setter': setter}
        self.classinfo = classinfo
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        """Set name of the Attribute."""
        self.name = name

    def __get__(self, obj: object, owner: type) -> Any:
        """Wrap get requests to the Attribute."""
        if not isinstance(self.store, dict):
            self._bind(obj)
        if isinstance(self.getter, Method):
            return self.getter()
        if not self.store or not self.key in self.store:
            return self.default
        return self.store[self.key]

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set requests to the Attribute."""
        # Check Type of Attribute
        if self.classinfo and not isinstance(val, self.classinfo):
            if isinstance(self.classinfo, type):
                typeinfo = self.classinfo.__name__
            elif isinstance(self.classinfo, tuple):
                names = [each.__name__ for each in self.classinfo]
                typeinfo = ' or '.join(names)
            else:
                typeinfo = '?'
            raise TypeError(
                f"'{self.name}' requires type {typeinfo}, "
                f"not {type(val).__name__}")
        if not isinstance(self.store, dict):
            self._bind(obj)
        if isinstance(self.setter, Method):
            self.setter(val)
        else:
            self.store[self.key] = val # type: ignore

    def _bind(self, obj: object) -> None:
        """Bind dictionary, getter and setter functions."""
        # Bind dictionary and key
        if isinstance(self.attr['dict'], str):
            self.store = obj.__dict__.get(self.attr['dict'])
            if not isinstance(self.store, dict):
                raise TypeError(
                    f"'{self.attr['dict']}' requires type dict "
                    f"not {type(self.store).__name__}")
        else:
            self.store = obj.__dict__
        self.key = self.attr['key'] or self.name

        # Bind getter function
        if isinstance(self.attr['getter'], str):
            self.getter = getattr(obj, self.attr['getter'])
            if not isinstance(self.getter, Method):
                raise TypeError(
                    f"'{self.attr['getter']}' requires type function "
                    f"not {type(self.getter).__name__}")
        else:
            self.getter = None

        # Bind setter function
        if isinstance(self.attr['setter'], str):
            self.setter = getattr(obj, self.attr['setter'])
            if not isinstance(self.setter, Method):
                raise TypeError(
                    f"'{self.attr['setter']}' requires type function "
                    f"not {type(self.setter).__name__}")
        else:
            self.setter = None

class ReadWriteAttr(Attr):
    """Descriptor Class for read- and writeable Attribute binding."""

    pass

class ReadOnlyAttr(Attr):
    """Descriptor Class for read-only Attribute binding."""

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set attribute requests."""
        raise AttributeError(
            f"'{self.name}' is a read-only property "
            f"of class {type(obj).__name__}")

# ################################################################################
# # Base classes for File I/O
# ################################################################################
#
# class FileIOBase(ABC):
#     @abstractmethod
#     def load(self, file: FileOrPathLike) -> object:
#         """Load object from file."""
#         return object()
#     @abstractmethod
#     def save(self, obj: object, file: FileOrPathLike) -> None:
#         """Save object to file."""
#         return None

################################################################################
# Base classes for object model templates
################################################################################

# class ObjectIP:
#     """Base class for objects subjected to intellectual property.
#
#     Resources like datasets, networks, systems and models share common
#     descriptive metadata comprising authorship and copyright, as well as
#     administrative metadata like branch and version. This base class is
#     intended to provide a unified interface to access those attributes.
#
#     """
#
#     _attr: StrDict
#     _copy_map: ClassVar[Dict[str, Tuple[str, type]]] = {
#         'attr': ('_attr', dict)}
#
#     about: Attr = ReadWriteAttr(str, key='_attr')
#     about.__doc__ = """Summary of the workspace.
#
#     A short description of the contents, the purpose or the intended application
#     of the workspace. The attribute about is inherited by resources, that are
#     created inside the workspace and support the attribute.
#     """
#
#     email: Attr = ReadWriteAttr(str, key='_attr')
#     email.__doc__ = """Email address of the maintainer of the workspace.
#
#     Email address to a person, an organization, or a service that is responsible
#     for the content of the workspace. The attribute email is inherited by
#     resources, that are created inside the workspace and support the attribute.
#     """
#
#     license: Attr = ReadWriteAttr(str, key='_attr')
#     license.__doc__ = """License for the usage of the contents of the workspace.
#
#     Namereference to a legal document giving specified users an official
#     permission to do something with the contents of the workspace. The attribute
#     license is inherited by resources, that are created inside the workspace
#     and support the attribute.
#     """
#
#     maintainer: Attr = ReadWriteAttr(str, key='_attr')
#     maintainer.__doc__ = """Name of the maintainer of the workspace.
#
#     A person, an organization, or a service that is responsible for the content
#     of the workspace. The attribute maintainer is inherited by resources, that
#     are created inside the workspace and support the attribute.
#     """
