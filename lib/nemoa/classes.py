# -*- coding: utf-8 -*-
"""Descriptors for binding class instance attributes.

When an instance of a class contains a descriptor class as a method, the
descriptor class defines the accessor and mutator methods of an attribute, which
is identified with the method's name.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.types import (
    Any, ClassVar, Dict, Method, OptDict, OptCallable, OptStr, OptType,
    StrDict, Tuple)

################################################################################
# Descriptors
################################################################################

class Attr:
    """Generic Descriptor Class for Attributes.

    Args:
        vtype:
        key:
        getter:
        setter:
        default:

    """

    _name: str
    _type: OptType = None
    _default: Any = None
    _dict: OptStr = None
    _getter: OptStr = None
    _setter: OptStr = None
    _obj_dict: OptDict = None
    _obj_getter: OptCallable = None
    _obj_setter: OptCallable = None

    def __init__(
            self, vtype: OptType = None, key: OptStr = None,
            getter: OptStr = None, setter: OptStr = None,
            default: Any = None) -> None:
        """Set optional names of dictionary, getter, setter, etc."""
        self._type = vtype
        self._dict = key
        self._getter = getter
        self._setter = setter
        self._default = default

    def __set_name__(self, owner: type, name: str) -> None:
        """Set name of the Attribute."""
        self._name = name

    def __get__(self, obj: object, owner: type) -> Any:
        """Wrap get requests to the Attribute."""
        if not isinstance(self._obj_dict, dict):
            self._bind(obj)
        if isinstance(self._obj_getter, Method):
            return self._obj_getter()
        return self._obj_dict.get(self._name, self._default) # type: ignore

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set requests to the Attribute."""
        # Check Type of Attribute
        if self._type is not None and not isinstance(val, self._type):
            raise TypeError(
                f"'{self._name}' requires type {self._type.__name__} "
                f"not {type(val).__name__}")
        if not isinstance(self._obj_dict, dict):
            self._bind(obj)
        if isinstance(self._obj_setter, Method):
            self._obj_setter(val)
        else:
            self._obj_dict[self._name] = val # type: ignore

    def _bind(self, obj: object) -> None:
        """Bind dictionary, getter and setter functions."""
        # Bind dictionary
        if isinstance(self._dict, str):
            self._obj_dict = obj.__dict__.get(self._dict)
            if not isinstance(self._obj_dict, dict):
                raise TypeError(
                    f"'{self._dict}' requires type dict "
                    f"not {type(self._obj_dict).__name__}")
        else:
            self._obj_dict = obj.__dict__

        # Bind getter function
        if isinstance(self._getter, str):
            self._obj_getter = getattr(obj, self._getter)
            if not isinstance(self._obj_getter, Method):
                raise TypeError(
                    f"'{self._getter}' requires type function "
                    f"not {type(self._obj_getter).__name__}")
        else:
            self._obj_getter = None

        # Bind setter function
        if isinstance(self._setter, str):
            self._obj_setter = getattr(obj, self._setter)
            if not isinstance(self._obj_setter, Method):
                raise TypeError(
                    f"'{self._setter}' requires type function "
                    f"not {type(self._obj_setter).__name__}")
        else:
            self._obj_setter = None

class ReadWriteAttr(Attr):
    """Descriptor Class for read- and writeable Attribute binding."""

    pass

class ReadOnlyAttr(Attr):
    """Descriptor Class for read-only Attribute binding."""

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set attribute requests."""
        raise AttributeError(
            f"'{self._name}' is a read-only property "
            f"of class {type(obj).__name__}")

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
