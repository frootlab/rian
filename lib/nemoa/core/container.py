# -*- coding: utf-8 -*-
"""Classes."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import check
from nemoa.errors import ReadOnlyError
from nemoa.types import Any, Callable, ClassInfo, OptClassInfo, Optional
from nemoa.types import OptStr, OptStrDict, StrDict, StrList, void

################################################################################
# Generic attribute descriptor for binding class instance attributes: When an
# instance of a class contains a descriptor class as a method, the descriptor
# class defines the accessor and mutator methods of the attribute, which is
# identified by the method's name.
################################################################################

class Attr(property):
    """Generic Descriptor Class for Attributes.

    Args:
        classinfo:
        bind:
        key:
        getter:
        setter:
        default: Default value, which is returned for a get request
        parent: Name of attribute, which references a parent object.
        readonly: Boolean value which determines if the attribute is read-only

    """

    _name: str
    _getter: OptStr
    _setter: OptStr
    _dict: OptStr
    _key: OptStr
    _default: Any
    _parent: OptStr
    _classinfo: OptClassInfo
    _readonly: bool

    # __Magic__

    def __init__(
            self, classinfo: OptClassInfo = None, bind: OptStr = None,
            key: OptStr = None, default: Any = None, getter: OptStr = None,
            setter: OptStr = None, parent: OptStr = None,
            readonly: bool = False) -> None:
        """Initialize Attribute Descriptor."""
        # Check Types of Arguments
        check.has_opt_type("argument 'classinfo'", classinfo, (type, tuple))
        check.has_opt_type("argument 'bind'", bind, str)
        check.has_opt_type("argument 'key'", key, str)
        check.has_opt_type("argument 'getter'", getter, str)
        check.has_opt_type("argument 'setter'", setter, str)
        check.has_type("argument 'readonly'", readonly, bool)

        # Set Descriptor Instance Attributes to Argument Values
        self._classinfo = classinfo
        self._dict = bind
        self._getter = getter
        self._setter = setter
        self._key = key
        self._parent = parent
        self._default = default
        self._readonly = readonly

    def __set_name__(self, owner: type, name: str) -> None:
        """Set name of the Attribute."""
        self._name = name

    def __get__(self, obj: object, owner: type) -> Any:
        """Bypass Attribute's get requests."""
        if self._getter:
            return self._get_getter(obj)()
        key = self._key or self._name
        default = self._get_default(obj)
        if self._dict:
            return self._get_dict(obj).get(key, default)
        return obj.__dict__.get(key, default)

    def __set__(self, obj: object, val: Any) -> None:
        """Bypass and type check Attribute's set requests."""
        if self._readonly:
            raise ReadOnlyError(obj, self._name)
        if self._classinfo:
            check.has_type(f"attribute '{self._name}'", val, self._classinfo)
        if self._setter:
            self._get_setter(obj)(val)
        else:
            key = self._key or self._name
            self._get_dict(obj)[key] = val

    def _get_dict(self, obj: object) -> dict:
        attr = self._dict
        if not attr:
            return obj.__dict__
        check.has_attr(obj, attr)
        check.has_type(attr, getattr(obj, attr), dict)
        return getattr(obj, attr)

    def _get_getter(self, obj: object) -> Callable:
        attr = self._getter
        if not attr:
            return void
        check.has_attr(obj, attr)
        check.is_callable(attr, getattr(obj, attr))
        return getattr(obj, attr)

    def _get_setter(self, obj: object) -> Callable:
        attr = self._setter
        if not attr:
            return void
        check.has_attr(obj, attr)
        check.is_callable(attr, getattr(obj, attr))
        return getattr(obj, attr)

    def _get_default(self, obj: object) -> Any:
        if not self._parent:
            return self._default
        parent = getattr(obj, self._parent, None)
        if not parent:
            return self._default
        return getattr(parent, self._name, self._default)

################################################################################
# Base Container Class
################################################################################

class ContentAttr(Attr):
    """Attributes for persistent content storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        kwds['bind'] = kwds.get('bind', '_data')
        super().__init__(*args, **kwds)

class MetadataAttr(Attr):
    """Attributes for persistent metadata storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        kwds['bind'] = kwds.get('bind', '_meta')
        kwds['parent'] = kwds.get('parent', 'parent')
        super().__init__(*args, **kwds)

class TransientAttr(Attr):
    """Attributes for not persistent storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        kwds['bind'] = kwds.get('bind', '_temp')
        super().__init__(*args, **kwds)

class VirtualAttr(Attr):
    """Attributes for not pesistent virtual objects.

    Virtual objects require the implementation of a getter function.
    """

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        check.has_type('getter', kwds.get('getter'), str)
        super().__init__(*args, **kwds)

class DescrAttr(MetadataAttr):
    """Attributes for descriptive metadata."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        kwds['classinfo'] = kwds.get('classinfo', str)
        super().__init__(*args, **kwds)

class RightsAttr(MetadataAttr):
    """Attributes for rights metadata."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize Attribute Descriptor."""
        kwds['classinfo'] = kwds.get('classinfo', str)
        super().__init__(*args, **kwds)

class TechAttr(MetadataAttr):
    """Attributes for technical metadata."""

class BaseContainer:
    """Base class for Container Objects."""

    _data: StrDict
    _meta: StrDict
    _temp: StrDict

    #
    # Transient Attributes
    #

    parent: property = TransientAttr(object)
    parent.__doc__ = """Reference to parent object."""

    #
    # Magic
    #

    def __init__(
            self, metadata: OptStrDict = None, content: OptStrDict = None,
            parent: Optional['BaseContainer'] = None) -> None:
        """Initialize instance members."""
        self._data = {}
        self._meta = {}
        self._temp = {}
        #self._parent = parent

        if metadata:
            self._set_metadata(metadata)
        if content:
            self._set_content(content)

    #
    # Getters and Setters for Attribute Groups
    #

    def _get_attrs(self, classinfo: ClassInfo) -> StrList:
        attrs: StrList = []
        for attr, obj in type(self).__dict__.items():
            if isinstance(obj, classinfo):
                attrs.append(attr)
        return attrs

    def _set_attrs(self, classinfo: ClassInfo, attrs: dict) -> None:
        check.has_type("second argument 'attrs'", attrs, dict)
        check.is_subset(
            "given values", set(attrs.keys()),
            "attributes", set(self._get_attrs(classinfo)))
        for attr, obj in attrs.items():
            setattr(self, attr, obj)

    def _get_content(self) -> dict:
        attrs = self._get_attrs(ContentAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_content(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(ContentAttr, attrs)

    def _get_metadata(self) -> dict:
        attrs = self._get_attrs(MetadataAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_metadata(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(MetadataAttr, attrs)

    def _get_descr_metadata(self) -> dict:
        attrs = self._get_attrs(DescrAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_descr_metadata(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(DescrAttr, attrs)

    def _get_rights_metadata(self) -> dict:
        attrs = self._get_attrs(DescrAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_rights_metadata(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(DescrAttr, attrs)

    def _get_tech_metadata(self) -> dict:
        attrs = self._get_attrs(TechAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_tech_metadata(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(TechAttr, attrs)

    def _get_transient(self) -> dict:
        attrs = self._get_attrs(TransientAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_transient(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(TransientAttr, attrs)

    def _get_virtual(self) -> dict:
        attrs = self._get_attrs(VirtualAttr)
        return {attr: getattr(self, attr) for attr in attrs}

    def _set_virtual(self, attrs: StrDict) -> None:
        check.has_type("argument 'attrs'", attrs, dict)
        self._set_attrs(VirtualAttr, attrs)

################################################################################
# Container class with Dublin Core metadata
################################################################################

class CoreContainer(BaseContainer):
    """Container class, that implements the Dublin Core Schema.

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

    title: property = DescrAttr()
    title.__doc__ = """
    A name given to the resource. Typically, a Title will be a name by which the
    resource is formally known.
    """

    subject: property = DescrAttr()
    subject.__doc__ = """
    The topic of the resource. Typically, the subject will be represented using
    keywords, key phrases, or classification codes. Recommended best practice is
    to use a controlled vocabulary.
    """

    description: property = DescrAttr()
    description.__doc__ = """
    An account of the resource. Description may include but is not limited to:
    an abstract, a table of contents, a graphical representation, or a free-text
    account of the resource.

    """

    date: property = DescrAttr()
    date.__doc__ = """
    A point or period of time associated with an event in the lifecycle of the
    resource. Date may be used to express temporal information at any level of
    granularity. Recommended best practice is to use an encoding scheme, such as
    the W3CDTF profile of ISO 8601 [W3CDTF]_.

    .. [W3CDTF] http://www.w3.org/TR/NOTE-datetime
    """

    type: property = DescrAttr()
    type.__doc__ = """
    The nature or genre of the resource. Recommended best practice is to use a
    controlled vocabulary such as the DCMI Type Vocabulary [DCMITYPE]_. To
    describe the file format, physical medium, or dimensions of the resource,
    use the Format element.

    .. [DCMITYPE] http://dublincore.org/documents/dcmi-type-vocabulary/
    """

    format: property = DescrAttr()
    format.__doc__ = """
    The file format, physical medium, or dimensions of the resource. Examples of
    dimensions include size and duration. Recommended best practice is to use a
    controlled vocabulary such as the list of Internet Media Types [MIME]_.

    .. [MIME] http://www.iana.org/assignments/media-types/
    """

    identifier: property = DescrAttr()
    identifier.__doc__ = """
    An unambiguous reference to the resource within a given context. Recommended
    best practice is to identify the resource by means of a string or number
    conforming to a formal identification system. Examples of formal
    identification systems include the Uniform Resource Identifier (URI)
    (including the Uniform Resource Locator (URL), the Digital Object Identifier
    (DOI) and the International Standard Book Number (ISBN).
    """

    source: property = DescrAttr()
    source.__doc__ = """
    A related resource from which the described resource is derived. The
    described resource may be derived from the related resource in whole or in
    part. Recommended best practice is to identify the related resource by means
    of a string conforming to a formal identification system.
    """

    language: property = DescrAttr()
    language.__doc__ = """
    A language of the resource. Recommended best practice is to use a controlled
    vocabulary such as RFC 4646 [RFC4646]_.

    .. [RFC4646] http://www.ietf.org/rfc/rfc4646.txt
    """

    coverage: property = DescrAttr()
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

    relation: property = DescrAttr()
    relation.__doc__ = """
    A related resource. Recommended best practice is to identify the related
    resource by means of a string conforming to a formal identification system.
    """

    creator: property = RightsAttr()
    creator.__doc__ = """
    An entity primarily responsible for making the resource. Examples of a
    Creator include a person, an organization, or a service. Typically, the name
    of a Creator should be used to indicate the entity.
    """

    publisher: property = RightsAttr()
    publisher.__doc__ = """
    An entity responsible for making the resource available. Examples of a
    Publisher include a person, an organization, or a service. Typically, the
    name of a Publisher should be used to indicate the entity.
    """

    contributor: property = RightsAttr()
    contributor.__doc__ = """
    An entity responsible for making contributions to the resource. Examples of
    a Contributor include a person, an organization, or a service. Typically,
    the name of a Contributor should be used to indicate the entity.
    """

    rights: property = RightsAttr()
    rights.__doc__ = """
    Information about rights held in and over the resource. Typically, rights
    information includes a statement about various property rights associated
    with the resource, including intellectual property rights.
    """
