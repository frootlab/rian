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

from nemoa.types import Any, Method, OptDict, OptCallable, OptStr, OptType

class Attr:
    """Descriptor with type checking and dictionary encapsulation."""

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
        self._type = vtype
        self._dict = key
        self._getter = getter
        self._setter = setter
        self._default = default

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, obj: object, owner: type) -> Any:
        if not isinstance(self._obj_dict, dict):
            self._bind(obj)
        if isinstance(self._obj_getter, Method):
            return self._obj_getter(obj)
        return self._obj_dict.get(self._name, self._default) # type: ignore

    def __set__(self, obj: object, val: Any) -> None:
        # Check Type of Attribute
        if self._type is not None and not isinstance(val, self._type):
            raise TypeError(
                f"'{self._name}' requires type {self._type.__name__} "
                f"not {type(val).__name__}")
        if not isinstance(self._obj_dict, dict):
            self._bind(obj)
        if isinstance(self._obj_setter, Method):
            self._obj_setter(obj, val)
        else:
            self._obj_dict[self._name] = val # type: ignore

    def _bind(self, obj: object) -> None:
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

class ReadOnlyAttr(Attr):
    def __set__(self, obj: object, val: Any) -> None:
        raise AttributeError(
            f"'{self._name}' is a read-only property "
            f"of class {type(obj).__name__}")

class ReadWriteAttr(Attr):
    pass
