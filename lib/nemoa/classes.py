# -*- coding: utf-8 -*-
"""Classes."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod

from nemoa.types import (
    Any, Callable, ClassVar, Dict, FileOrPathLike, Method, ClassInfo,
    OptClassInfo, OptDict, OptCallable, OptStr, OptType, StrDict, Tuple)

################################################################################
# Generic attribute descriptors for binding class instance attributes: When an
# instance of a class contains a descriptor class as a method, the descriptor
# class defines the accessor and mutator methods of the attribute, which is
# identified by the method's name.
################################################################################

class ReadWriteAttr(property):
    """Extended descriptor class for properties.

    Args:
        classinfo:
        bind:
        key:
        getter:
        setter:
        default:

    """

    #
    # Private Instance Variables
    #

    _args: dict
    _classinfo: ClassInfo
    _default: Any
    _getter: Callable
    _key: str
    _name: str
    _setter: Callable
    _store: dict

    #
    # Magic
    #

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, getter: OptStr = None,
            setter: OptStr = None) -> None:
        """Initialize instance variables."""
        if classinfo:
            if not isinstance(classinfo, (type, tuple)):
                raise TypeError(
                    "'classinfo' requires to be a type or a tuple of types")
            self._classinfo = classinfo
        self._args = {
            'bind': bind, 'key': key, 'getter': getter, 'setter': setter}
        self._default = default

    def __set_name__(self, owner: type, name: str) -> None:
        """Set name of the Attribute."""
        self._name = name

    def __get__(self, obj: object, owner: type) -> Any:
        """Wrap get requests to the Attribute."""
        if not hasattr(self, '_store'):
            self._bind(obj)
        if hasattr(self, '_getter'):
            return self._getter()
        return self._store.get(self._key, self._default)

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set requests to the Attribute."""
        # Check Type of Attribute
        if hasattr(self, '_classinfo') and not isinstance(val, self._classinfo):
            if isinstance(self._classinfo, type):
                typestr = self._classinfo.__name__
            elif isinstance(self._classinfo, tuple):
                names = [each.__name__ for each in self._classinfo]
                typestr = ' or '.join(names)
            else:
                typestr = '?'
            raise TypeError(
                f"'{self._name}' requires type {typestr}"
                f", not {type(val).__name__}")
        if not hasattr(self, '_store'):
            self._bind(obj)
        if hasattr(self, '_setter'):
            self._setter(val)
        else:
            self._store[self._key] = val

    #
    # Private Instance Methods
    #

    def _bind(self, obj: object) -> None:
        """Bind key, getter and setter functions."""
        # Bind key
        self._bind_key(obj, self._args['bind'], self._args['key'])

        # Bind getter
        if isinstance(self._args['getter'], str):
            self._bind_getter(obj, self._args['getter'])

        # Bind setter
        if isinstance(self._args['setter'], str):
            self._bind_setter(obj, self._args['setter'])

    def _bind_key(self, obj: object, mapping: OptStr, key: OptStr) -> None:
        if mapping is None:
            self._store = obj.__dict__
        elif not mapping in obj.__dict__:
            name = getattr(obj, '__name__', obj.__class__.__name__)
            raise AttributeError(
                f"{name} has no attribute {mapping}")
        elif not isinstance(obj.__dict__[mapping], dict):
            raise TypeError(
                f"'{mapping}' requires type mapping"
                f", not {type(obj.__dict__[mapping]).__name__}")
        else:
            self._store = obj.__dict__[mapping]
        if key is None:
            self._key = self._name
        elif not isinstance(key, str):
            raise TypeError(
                f"'key' requires type string"
                f", not '{type(key).__name__}'")
        else:
            self._key = key

    def _bind_getter(self, obj: object, getter: str) -> None:
        if not hasattr(obj, getter):
            name = getattr(obj, '__name__', obj.__class__.__name__)
            raise AttributeError(
                f"{name} has no attribute {getter}")
        elif not callable(getattr(obj, getter)):
            raise TypeError(
                f"'{getter}' requires to be callable"
                f", not {type(getattr(obj, getter)).__name__}")
        else:
            # linter complains if set directly
            setattr(self, '_getter', getattr(obj, getter))

    def _bind_setter(self, obj: object, setter: str) -> None:
        if not hasattr(obj, setter):
            name = getattr(obj, '__name__', obj.__class__.__name__)
            raise AttributeError(
                f"{name} has no attribute {setter}")
        elif not callable(getattr(obj, setter)):
            raise TypeError(
                f"'{setter}' requires to be callable"
                f", not {type(getattr(obj, setter)).__name__}")
        else:
            # linter complains if set directly
            setattr(self, '_setter', getattr(obj, setter))

class ReadOnlyAttr(ReadWriteAttr):
    """Descriptor Class for read-only Attribute binding."""

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set attribute requests."""
        raise AttributeError(
            f"'{self._name}' is a read-only property "
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
#     about: property = ReadWriteAttr(str, key='_attr')
#     about.__doc__ = """Summary of the workspace.
#
#     A short description of the contents, the purpose or the intended application
#     of the workspace. The attribute about is inherited by resources, that are
#     created inside the workspace and support the attribute.
#     """
#
#     email: property = ReadWriteAttr(str, key='_attr')
#     email.__doc__ = """Email address of the maintainer of the workspace.
#
#     Email address to a person, an organization, or a service that is responsible
#     for the content of the workspace. The attribute email is inherited by
#     resources, that are created inside the workspace and support the attribute.
#     """
#
#     license: property = ReadWriteAttr(str, key='_attr')
#     license.__doc__ = """License for the usage of the contents of the workspace.
#
#     Namereference to a legal document giving specified users an official
#     permission to do something with the contents of the workspace. The attribute
#     license is inherited by resources, that are created inside the workspace
#     and support the attribute.
#     """
#
#     maintainer: property = ReadWriteAttr(str, key='_attr')
#     maintainer.__doc__ = """Name of the maintainer of the workspace.
#
#     A person, an organization, or a service that is responsible for the content
#     of the workspace. The attribute maintainer is inherited by resources, that
#     are created inside the workspace and support the attribute.
#     """
