# -*- coding: utf-8 -*-
"""Classes."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
from nemoa.base import check
from nemoa.errors import ReadOnlyError, InvalidAttrError
from nemoa.types import Any, Callable, Date, OptClassInfo, Optional
from nemoa.types import OptStr, OptStrDict, OptType, StrDict, StrList, void

#
# Types
#

OptContainer = Optional['Container']

#
# Base Classes for Attribute Groups and Attributes
#

class BaseAttrGroup(ABC):
    """Abstract Base Class for Attribute Groups."""

    _name: str
    _prefix: str

    @abstractmethod
    def _get_parent(self) -> Optional['BaseAttrGroup']:
        pass

    @abstractmethod
    def _set_parent(self, obj: 'BaseAttrGroup') -> None:
        pass

class Attr(property):
    """Base Class for Attributes.

    Generally attribute descriptors are used for binding class instance
    attributes. Thereby, when any instance of a class contains an attribute
    descriptor as an attribute (i.e. a method), the descriptor class defines
    accessor and mutator methods of the respective attribute.

    The attribute descriptor features following extensions:
        * Type checking against given classinfo
        * Setting the default value of the property
        * Declaration of getters and setters by forward references
        * Attribute binding within a different object dictionaries. This is
            used for a physical aggregation of attributes by their type, i.e.
            content, metadata and temporary data.
        * Attribute binding to a different key, then the attribute name. This
            is used to provide different accessors for the same key e.g. for
            a readonly public access and a readwritable protected access.
        *

    Args:
        classinfo:
        bind:
        key:
        getter:
        setter:
        default: Default value, which is returned for a get request
        parent: Name of attribute, which references a parent object.
        readonly: Boolean value which determines if the attribute is read-only
        category: Attribute categories allow a free aggregation of attributes by
            their respective category values.

    """

    _name: str
    _classinfo: OptClassInfo
    _default: Any
    _readonly: bool
    _bind: OptStr
    _key: OptStr
    _getter: OptStr
    _setter: OptStr
    _inherit: bool
    _category: OptStr

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, category: OptStr = None,
            getter: OptStr = None, setter: OptStr = None, inherit: bool = False,
            readonly: bool = False) -> None:
        """Initialize Attribute Descriptor."""
        super().__init__()
        # Check Types of Arguments
        check.has_opt_type("argument 'classinfo'", classinfo, (type, tuple))
        check.has_type("argument 'readonly'", readonly, bool)
        check.has_opt_type("argument 'bind'", bind, str)
        check.has_opt_type("argument 'key'", key, str)
        check.has_opt_type("argument 'getter'", getter, str)
        check.has_opt_type("argument 'setter'", setter, str)
        check.has_type("argument 'inherit'", inherit, bool)
        check.has_opt_type("argument 'category'", category, str)

        # Set Descriptor Instance Attributes to Argument Values
        self._classinfo = classinfo
        self._default = default
        self._readonly = readonly
        self._dict = bind
        self._key = key
        self._getter = getter
        self._setter = setter
        self._inherit = inherit
        self._category = category

    def __set_name__(self, cls: type, name: str) -> None:
        """Set name of the Attribute."""
        self._name = name

    def __get__(self, obj: BaseAttrGroup, cls: OptType = None) -> Any:
        """Bypass get request."""
        if self._getter:
            return self._get_getter(obj)()
        name = self._get_name(obj)
        default = self._get_default(obj)
        if self._dict:
            return self._get_dict(obj).get(name, default)
        return obj.__dict__.get(name, default)

    def __set__(self, obj: BaseAttrGroup, val: Any) -> None:
        """Bypass and type check set request."""
        if self._readonly:
            raise ReadOnlyError(obj, self._name)
        if self._classinfo and not isinstance(val, type(self._default)):
            check.has_type(f"attribute '{self._name}'", val, self._classinfo)
        if self._setter:
            self._get_setter(obj)(val)
        else:
            name = self._get_name(obj)
            self._get_dict(obj)[name] = val

    def _get_name(self, obj: BaseAttrGroup) -> str:
        if isinstance(obj, AttrGroup):
            prefix = getattr(obj, '_prefix', None)
            if prefix:
                return '.'.join([prefix, self._key or self._name])
        return self._key or self._name

    def _get_dict(self, obj: BaseAttrGroup) -> dict:
        attr = self._dict
        if not attr:
            return obj.__dict__
        check.has_attr(obj, attr)
        check.has_type(attr, getattr(obj, attr), dict)
        return getattr(obj, attr)

    def _get_getter(self, obj: BaseAttrGroup) -> Callable:
        attr = self._getter
        if not attr:
            return void
        check.has_attr(obj, attr)
        check.is_callable(attr, getattr(obj, attr))
        return getattr(obj, attr)

    def _get_setter(self, obj: BaseAttrGroup) -> Callable:
        attr = self._setter
        if not attr:
            return void
        check.has_attr(obj, attr)
        check.is_callable(attr, getattr(obj, attr))
        return getattr(obj, attr)

    def _get_default(self, obj: BaseAttrGroup) -> Any:
        if not self._inherit:
            return self._default
        parent = obj._get_parent() # pylint: disable=W0212
        if not parent:
            return self._default
        return getattr(parent, self._name, self._default)


#
# Container Base Class and Container Attribute Classes
#

class AttrGroup(BaseAttrGroup):
    """Base class for Container Attribute Groups."""

    _data: StrDict
    _meta: StrDict
    _temp: StrDict

    def _get_parent(self) -> Optional[BaseAttrGroup]:
        try:
            return self._temp['parent']
        except AttributeError:
            return None
        except KeyError:
            return None

    def _set_parent(self, obj: BaseAttrGroup) -> None:
        if not hasattr(self, '_temp') or not isinstance(self._temp, dict):
            setattr(self, '_temp', {})
        self._temp['parent'] = obj

    #
    # Access Attributes by their group name, ClassInfo and category
    #

    @classmethod
    def _get_attr_groups(cls) -> StrDict:
        def get_groups(cls: type) -> StrDict:
            groups: StrDict = {}
            for base in cls.__mro__:
                for name, obj in base.__dict__.items():
                    if not isinstance(obj, AttrGroup):
                        continue
                    groups[name] = obj
                    for key, val in get_groups(type(obj)).items():
                        groups[name + '.' + key] = val
            return groups
        return get_groups(cls)

    @classmethod
    def _get_attr_names(
            cls, group: OptStr = None, classinfo: OptClassInfo = None,
            category: OptStr = None) -> StrList:
        # Locate the attribute group, that corresponds to the given group name.
        # By default identify the current class as attribute group
        if group:
            groups = cls._get_attr_groups()
            if not group in groups:
                raise InvalidAttrError(cls, group)
            root = type(groups[group])
        else:
            root = cls

        # Search for attributes within the attribute group, that match the
        # given attribute class and category
        names: StrList = []
        for base in root.__mro__:
            for name, val in base.__dict__.items():
                if not isinstance(val, Attr):
                    continue
                if category and not getattr(val, '_category', None) == category:
                    continue
                if classinfo and not isinstance(val, classinfo):
                    continue
                names.append(name)
        return names

    @classmethod
    def _get_attr_types(
            cls, group: OptStr = None, category: OptStr = None,
            classinfo: OptClassInfo = None) -> StrDict:
        # Locate the attribute group, that corresponds to the given group name.
        # By default identify the current class as attribute group
        if group:
            groups = cls._get_attr_groups()
            if not group in groups:
                raise InvalidAttrError(cls, group)
            root = type(groups[group])
        else:
            root = cls

        # Search for attributes within the attribute group, that match the
        # given attribute class and category
        types: StrDict = {}
        for base in root.__mro__:
            for name, obj in base.__dict__.items():
                if not isinstance(obj, Attr):
                    continue
                if category and not getattr(obj, '_category', None) == category:
                    continue
                if classinfo and not isinstance(obj, classinfo):
                    continue
                types[name] = getattr(obj, '_classinfo', None)
        return types

    def _get_attr_values(self,
            group: OptStr = None, classinfo: OptClassInfo = None,
            category: OptStr = None) -> StrDict:
        # Get attribute names
        attrs = self._get_attr_names(
            group=group, classinfo=classinfo, category=category)

        # If a group name is given, get the respective attribute group by
        # stepping downwards the attribute hierarchy. Otherwise identify self
        # with the attribute group
        obj = self
        if group:
            for attr in group.split('.'):
                obj = getattr(obj, attr)

        # Get and return attributes from attribute group
        return {attr: getattr(obj, attr) for attr in attrs}

    def _set_attr_values(self,
            data: dict, group: OptStr = None,
            classinfo: OptClassInfo = None, category: OptStr = None) -> None:
        if not data:
            return

        # Check if the given attribute names are valid with respect
        # to the group name, their class and the category
        if group or classinfo or category:
            valid = self._get_attr_names(
                group=group, classinfo=classinfo, category=category)
            check.is_subset(
                "given names", set(data.keys()),
                "attributes", set(valid))

        # If a group name is given, get the respective attribute group by
        # stepping downwards the attribute hierarchy. Otherwise identify self
        # with the attribute group
        obj = self
        if group:
            for attr in group.split('.'):
                obj = getattr(obj, attr)

        # Set attributes within the respective attribute group
        for key, val in data.items():
            setattr(obj, key, val)

class DataAttr(Attr):
    """Attributes for persistent content objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['bind'] = kwds.get('bind', '_data')
        super().__init__(*args, **kwds)

class MetaAttr(Attr):
    """Attributes for persistent metadata objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['bind'] = kwds.get('bind', '_meta')
        kwds['inherit'] = kwds.get('inherit', True)
        super().__init__(*args, **kwds)

class TempAttr(Attr):
    """Attributes for non persistent stored objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['bind'] = kwds.get('bind', '_temp')
        super().__init__(*args, **kwds)

class VirtAttr(Attr):
    """Attributes for non persistent virtual objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        check.has_type('getter', kwds.get('getter'), str)
        super().__init__(*args, **kwds)

class Container(AttrGroup):
    """Base class for Container Objects."""

    #
    # Public Attributes
    #

    parent: property = VirtAttr(
        BaseAttrGroup, getter='_get_parent', setter='_set_parent')
    parent.__doc__ = """Reference to parent container object."""

    #
    # Events
    #

    def __init__(
            self, data: OptStrDict = None, meta: OptStrDict = None,
            parent: OptContainer = None) -> None:
        """Initialize Container instance."""
        self._data = {} # Initialize buffer for content attributes
        self._meta = {} # Initialize buffer for metadata attributes
        self._temp = {} # Initialize buffer for temporary attributes

        if data: # Restore content attributes
            self._set_attr_values(data, classinfo=DataAttr)
        if meta: # Restore metadata attributes
            self._set_attr_values(meta, classinfo=MetaAttr)
        if parent: # Set parent container
            self.parent = parent

        # Bind attribute groups within the container
        self._bind_attr_groups()

    #
    # Accessors for Attribute Groups
    #

    def _bind_attr_groups(self) -> None:
        for fqn in self._get_attr_groups():
            # Get attribute group by stepping the attribute hierarchy
            # downwards the tokens of the fully qualified name
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)

            # Set group name and prefix to avoid namespace collision
            # within dictionary buffers
            setattr(obj, '_name', fqn.rsplit('.', 1)[-1])
            setattr(obj, '_prefix', fqn)

            # Bind dictionary buffers
            setattr(obj, '_data', self._data)
            setattr(obj, '_meta', self._meta)
            setattr(obj, '_temp', self._temp)

#
# Dublin Core (DC) Attributes
#

class DCAttr(MetaAttr):
    """Dublin Core Metadata Attribute."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['classinfo'] = kwds.get('classinfo', str)
        kwds['inherit'] = kwds.get('inherit', True)
        super().__init__(*args, **kwds)

class DCAttrGroup(AttrGroup):
    """Dublin Core Metadata Element Set, Version 1.1.

    The Dublin Core Metadata Element Set is a vocabulary of fifteen properties
    for use in resource description. The name "Dublin" is due to its origin at a
    1995 invitational workshop in Dublin, Ohio; "core" because its elements are
    broad and generic, usable for describing a wide range of resources.

    The fifteen element "Dublin Core" described in this standard is part of a
    larger set of metadata vocabularies and technical specifications maintained
    by the Dublin Core Metadata Initiative (DCMI). The full set of vocabularies,
    DCMI Metadata Terms [DCMI-TERMS]_, also includes sets of resource classes
    (including the DCMI Type Vocabulary [DCMI-TYPE]_), vocabulary encoding
    schemes, and syntax encoding schemes. The terms in DCMI vocabularies are
    intended to be used in combination with terms from other, compatible
    vocabularies in the context of application profiles and on the basis of the
    DCMI Abstract Model [DCAM]_.

    .. [DCMI-TERMS] http://dublincore.org/documents/dcmi-terms/
    .. [DCMI-TYPE] http://dublincore.org/documents/dcmi-type-vocabulary/
    .. [DCAM] http://dublincore.org/documents/2007/06/04/abstract-model/
    """

    title: property = DCAttr(category='content')
    title.__doc__ = """
    A name given to the resource. Typically, a Title will be a name by which the
    resource is formally known.
    """

    subject: property = DCAttr(category='content')
    subject.__doc__ = """
    The topic of the resource. Typically, the subject will be represented using
    keywords, key phrases, or classification codes. Recommended best practice is
    to use a controlled vocabulary.
    """

    description: property = DCAttr(category='content')
    description.__doc__ = """
    An account of the resource. Description may include but is not limited to:
    an abstract, a table of contents, a graphical representation, or a free-text
    account of the resource.
    """

    type: property = DCAttr(category='content')
    type.__doc__ = """
    The nature or genre of the resource. Recommended best practice is to use a
    controlled vocabulary such as the DCMI Type Vocabulary [DCMITYPE]_. To
    describe the file format, physical medium, or dimensions of the resource,
    use the Format element.

    .. [DCMITYPE] http://dublincore.org/documents/dcmi-type-vocabulary/
    """

    source: property = DCAttr(category='content')
    source.__doc__ = """
    A related resource from which the described resource is derived. The
    described resource may be derived from the related resource in whole or in
    part. Recommended best practice is to identify the related resource by means
    of a string conforming to a formal identification system.
    """

    coverage: property = DCAttr(category='content')
    coverage.__doc__ = """
    The spatial or temporal topic of the resource, the spatial applicability of
    the resource, or the jurisdiction under which the resource is relevant.
    Spatial topic and spatial applicability may be a named place or a location
    specified by its geographic coordinates. Temporal topic may be a named
    period, date, or date range. A jurisdiction may be a named administrative
    entity or a geographic place to which the resource applies. Recommended best
    practice is to use a controlled vocabulary such as the Thesaurus of
    Geographic Names [TGN]_. Where appropriate, named places or time periods can
    be used in preference to numeric identifiers such as sets of coordinates or
    date ranges.

    .. [TGN] http://www.getty.edu/research/tools/vocabulary/tgn/index.html
    """

    relation: property = DCAttr(category='content')
    relation.__doc__ = """
    A related resource. Recommended best practice is to identify the related
    resource by means of a string conforming to a formal identification system.
    """

    creator: property = DCAttr(category='property')
    creator.__doc__ = """
    An entity primarily responsible for making the resource. Examples of a
    Creator include a person, an organization, or a service. Typically, the name
    of a Creator should be used to indicate the entity.
    """

    publisher: property = DCAttr(category='property')
    publisher.__doc__ = """
    An entity responsible for making the resource available. Examples of a
    Publisher include a person, an organization, or a service. Typically, the
    name of a Publisher should be used to indicate the entity.
    """

    contributor: property = DCAttr(category='property')
    contributor.__doc__ = """
    An entity responsible for making contributions to the resource. Examples of
    a Contributor include a person, an organization, or a service. Typically,
    the name of a Contributor should be used to indicate the entity.
    """

    rights: property = DCAttr(category='property')
    rights.__doc__ = """
    Information about rights held in and over the resource. Typically, rights
    information includes a statement about various property rights associated
    with the resource, including intellectual property rights.
    """

    identifier: property = DCAttr(category='instantiation')
    identifier.__doc__ = """
    An unambiguous reference to the resource within a given context. Recommended
    best practice is to identify the resource by means of a string or number
    conforming to a formal identification system. Examples of formal
    identification systems include the Uniform Resource Identifier (URI)
    (including the Uniform Resource Locator (URL), the Digital Object Identifier
    (DOI) and the International Standard Book Number (ISBN).
    """

    format: property = DCAttr(category='instantiation')
    format.__doc__ = """
    The file format, physical medium, or dimensions of the resource. Examples of
    dimensions include size and duration. Recommended best practice is to use a
    controlled vocabulary such as the list of Internet Media Types [MIME]_.

    .. [MIME] http://www.iana.org/assignments/media-types/
    """

    language: property = DCAttr(category='instantiation')
    language.__doc__ = """
    A language of the resource. Recommended best practice is to use a controlled
    vocabulary such as RFC 4646 [RFC4646]_.

    .. [RFC4646] http://www.ietf.org/rfc/rfc4646.txt
    """

    date: property = DCAttr(classinfo=Date, category='instantiation')
    date.__doc__ = """
    A point or period of time associated with an event in the lifecycle of the
    resource. Date may be used to express temporal information at any level of
    granularity. Recommended best practice is to use an encoding scheme, such as
    the W3CDTF profile of ISO 8601 [W3CDTF]_.

    .. [W3CDTF] http://www.w3.org/TR/NOTE-datetime
    """
