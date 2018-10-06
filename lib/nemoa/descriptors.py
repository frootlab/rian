# -*- coding: utf-8 -*-
"""Descriptors for binding instance attributes.

When an instance of a class contains a descriptor class as a method, the
descriptor defines the getter and setter method of an attribute, which is
called by the method's name.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from nemoa.types import Any, OptType

class Attr:
    """Descriptor with type checking and dictionary encapsulation."""
    def __init__(self, valtype: OptType = None, key: str = '_cfg') -> None:
        """ """
        self.key = key
        self.valtype = valtype
    def __get__(self, instance: object, owner: object) -> Any:
        """ """
        return instance.__dict__[self.key][self.name]
    def __set__(self, instance, val):
        """ """
        # Type checking if valtype is not None
        if self.valtype is not None and not isinstance(val, self.valtype):
            raise ValueError(
                f"'{self.name}' requires types {self.valtype.__name__} "
                f"not {type(val).__name__}")

        instance.__dict__[self.key][self.name] = val
    def __set_name__(self, owner, name):
        self.name = name

class ReadOnlyAttr(Attr):
    def __init__(self, valtype: OptType = None, key: str = '_cfg') -> None:
        """ """
        self.key = key
        self.valtype = valtype
    def __get__(self, instance: object, owner: object) -> Any:
        """ """
        return instance.__dict__[self.key][self.name]
    def __set__(self, instance, val):
        raise AttributeError(
            f"'{self.name}' is a read-only property "
            f"of class {instance.__class__.__name__}")

class ReadWriteAttr(Attr):
    def __init__(self, valtype: OptType = None, key: str = '_cfg') -> None:
        """ """
        self.key = key
        self.valtype = valtype
    def __get__(self, instance: object, owner: object) -> Any:
        """ """
        return instance.__dict__[self.key].get(self.name)
    def __set__(self, instance, val) -> None:
        """ """
        # Check Type of Attribute
        if self.valtype is not None and not isinstance(val, self.valtype):
            raise ValueError(
                f"'{self.name}' requires type {self.valtype.__name__} "
                f"not {type(val).__name__}")
        instance.__dict__[self.key][self.name] = val
