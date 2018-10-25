# -*- coding: utf-8 -*-
"""Classes."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import check
from nemoa.errors import SetReadOnlyAttrError
from nemoa.types import Any, Callable, ClassInfo, OptClassInfo, OptStr, StrDict

################################################################################
# Generic attribute descriptors for binding class instance attributes: When an
# instance of a class contains a descriptor class as a method, the descriptor
# class defines the accessor and mutator methods of the attribute, which is
# identified by the method's name.
################################################################################

class ReadWriteAttr(property):
    """Descriptor Class for read- and writable Attributes.

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
    _dict: dict

    #
    # __Magic__
    #

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, getter: OptStr = None,
            setter: OptStr = None) -> None:
        """Initialize instance variables."""
        # Check types of Arguments
        check.has_opt_type("argument 'classinfo'", classinfo, (type, tuple))
        check.has_opt_type("argument 'bind'", bind, str)
        check.has_opt_type("argument 'key'", key, str)
        check.has_opt_type("argument 'getter'", getter, str)
        check.has_opt_type("argument 'setter'", setter, str)

        # Set Instance Variables to Arguments
        if classinfo:
            self._classinfo = classinfo
        self._args = {
            'bind': bind, 'key': key, 'getter': getter, 'setter': setter}
        self._default = default

    def __set_name__(self, owner: type, name: str) -> None:
        """Set name of the Attribute."""
        self._name = name

    def __get__(self, obj: object, owner: type) -> Any:
        """Wrap get requests to the Attribute."""
        if not hasattr(self, '_dict'):
            self._bind(obj)
        if hasattr(self, '_getter'):
            return self._getter()
        return self._dict.get(self._key, self._default)

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set requests to the Attribute."""
        if hasattr(self, '_classinfo'):
            check.has_type(self._name, val, self._classinfo)
        if not hasattr(self, '_dict'):
            self._bind(obj)
        if hasattr(self, '_setter'):
            self._setter(val)
        else:
            self._dict[self._key] = val

    #
    # Private Instance Methods
    #

    def _bind(self, obj: object) -> None:
        self._dict = obj.__dict__
        self._key = self._name
        if isinstance(self._args['bind'], str):
            self._bind_dict(obj, self._args['bind']) # Bind custom dict
        if isinstance(self._args['key'], str):
            self._key = self._args['key'] # Bind custom key
        if isinstance(self._args['getter'], str):
            self._bind_getter(obj, self._args['getter']) # Bind custom getter
        if isinstance(self._args['setter'], str):
            self._bind_setter(obj, self._args['setter']) # Bind custom setter

    def _bind_dict(self, obj: object, bind: str) -> None:
        check.has_attr(obj, bind)
        check.has_type(bind, getattr(obj, bind), dict)
        self._dict = obj.__dict__[bind]

    def _bind_getter(self, obj: object, getter: str) -> None:
        check.has_attr(obj, getter)
        check.is_callable(getter, getattr(obj, getter))
        setattr(self, '_getter', getattr(obj, getter))

    def _bind_setter(self, obj: object, setter: str) -> None:
        check.has_attr(obj, setter)
        check.is_callable(setter, getattr(obj, setter))
        setattr(self, '_setter', getattr(obj, setter))

class ReadOnlyAttr(ReadWriteAttr):
    """Descriptor Class for read-only Attributes."""

    def __set__(self, obj: object, val: Any) -> None:
        """Wrap set attribute requests."""
        raise SetReadOnlyAttrError(obj, self._name)

class TreeReadWriteAttr(ReadWriteAttr):
    """Descriptor Class for rw-Attributes within a tree object hierarchy.

    Args:
        parent: Name of attribute, which references a parent object of identical
            type.

    """

    _parent: object

    #
    # __Magic__
    #

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, getter: OptStr = None,
            setter: OptStr = None, parent: OptStr = None) -> None:
        """Initialize instance variables."""
        super().__init__(
            classinfo=classinfo, bind=bind, key=key, default=default,
            getter=getter, setter=setter)
        self._args['parent'] = parent

    def __get__(self, obj: object, owner: type) -> Any:
        """Wrap get requests to the Attribute."""
        if not hasattr(self, '_dict'):
            self._bind(obj)
        if hasattr(self, '_getter'):
            return self._getter()
        if self._dict.get(self._key):
            return self._dict.get(self._key)
        if hasattr(self, '_parent') and hasattr(self._parent, self._name):
            return getattr(self._parent, self._name)
        return self._default

    def _bind(self, obj: object) -> None:
        super()._bind(obj)
        if isinstance(self._args['parent'], str):
            self._bind_parent(obj, self._args['parent'])

    def _bind_parent(self, obj: object, parent: str) -> None:
        check.has_attr(obj, parent)
        setattr(self, '_parent', getattr(obj, parent))

################################################################################
# Meta Data object model template
################################################################################

class MetaAttr(TreeReadWriteAttr):
    """Descriptor Class for MetaData Attributes."""

class ContentAttr(TreeReadWriteAttr):
    """Descriptor Class for Content Attributes."""

class MetaDataObject:
    """Base class for resources, that are subjected to intellectual property.

    Resources like documents, datasets, models or entire workspaces share common
    descriptive metadata comprising authorship and copyright, as well as further
    administrative metadata like branch and version. This base class is intended
    as an object model template for such resources.

    """

    #
    # Private Instance Variables
    #

    _meta: StrDict
    _content: StrDict
    _parent: 'MetaDataObject'

    #
    # Magic
    #

    def __init__(self) -> None:
        """Initialize instance members."""
        self._meta = {}

    #
    # Private Methods
    #

    def _get_meta_attrs(self) -> list:
        d = type(self).__dict__
        return [k for k, v in d.items() if isinstance(v, MetaAttr)]

    def _get_meta(self) -> dict:
        attrs = self._get_meta_attrs()
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_meta(self, meta: StrDict) -> None:
        check.has_type("first argument 'meta'", meta, dict)
        attrs = self._get_meta_attrs()
        check.is_subset(
            "argument 'meta'", set(meta.keys()),
            "meta data attributes", set(attrs))
        for attr, val in meta.items():
            setattr(self, attr, val)

    #
    # Puplic Methods
    #

    #
    # Puplic Attributes
    #

    about: property = MetaAttr(str, bind='_meta')
    about.__doc__ = """Summary of the resource.

    A short description of the contents, the purpose or the intended application
    of the resource. The default value of the attribute is inherited from
    resources, that are created upstream the resource hierarchy.
    """

    email: property = MetaAttr(str, bind='_meta')
    email.__doc__ = """Email address of the maintainer of the resource.

    Email address to a person, an organization, or a service that is responsible
    for the content of the resource. The default value of the attribute is
    inherited from resources, that are created upstream the resource hierarchy.
    """

    license: property = MetaAttr(str, bind='_meta')
    license.__doc__ = """License for the usage of the contents of the resource.

    Namereference to a legal document giving specified users an official
    permission to do something with the contents of the resource. The default
    value of the attribute is inherited from resources, that are created
    upstream the resource hierarchy.
    """

    maintainer: property = MetaAttr(str, bind='_meta')
    maintainer.__doc__ = """Name of the maintainer of the resource.

    A person, an organization, or a service, that is responsible for the content
    of the resource. The default value of the attribute is inherited from
    resources, that are created upstream the resource hierarchy.
    """
