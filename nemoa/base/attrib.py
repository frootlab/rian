# -*- coding: utf-8 -*-
"""Attributes, Attribute Groups and Containers."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import check
from nemoa.errors import InvalidAttrError, MissingKwError, ReadOnlyAttrError
from nemoa.types import Any, Date, OptClassInfo, Optional, OptCallable
from nemoa.types import OptStr, OptStrDict, OptType, StrDict, StrList, void
from nemoa.types import OptDict, OptBool, Union, Callable, CallableClasses

#
# Types
#

OptCallOrStr = Optional[Union[Callable, str]]

#
# Attribute Group Base Class and Constructor
#

class Group:
    """Base Class for Attribute Groups.

    Attribute Groups are used to group a set of attribute declarations, so that
    they can be incorporated as a group into complex type definitions. Attribute
    Groups also allow superseeding the settings of their contained attributes to
    control the group behaviour in different applications.

    Args:
        readonly: Boolean value, which superseeds the contained attributes
            read-only behaviour. For the values True or False, all contained
            attributes respectively are read-only or read-writable. By the
            default value None, the attributes' settings are not superseeded.
        remote: Boolean value, which superseeds the contained attributes remote
            behaviour. For the value True, all contained attributes are shared
            attributes of the parent attribute group, which must be referenced
            and contain the respetive attributes, or an error is raised. For the
            value False, all contained atributes are handled locally, regardless
            of a parent group. By the default value None, the attributes'
            settings are not superseeded.
        inherit: Boolean value, which superseeds the contained attributes
            inheritance behaviour. For the value True, all contained attributes
            inherit their default values from the attribute values of the parent
            attribute group, which must be referenced and contain the respetive
            attributes, or an error is raised. For the value False, the default
            values of the contained atributes are handled locally, regardless of
            a parent group. By the default value None, the attributes settings
            are not superseeded.

    """

    _attr_group_name: str
    _attr_group_prefix: str
    _attr_group_parent: Optional['Group']
    _attr_group_defaults: dict

    def __init__(
            self, readonly: OptBool = None, remote: OptBool = None,
            inherit: OptBool = None) -> None:
        self._attr_group_name = ''
        self._attr_group_prefix = ''
        self._attr_group_parent = None
        self._attr_group_defaults = {}
        if readonly is not None:
            self._attr_group_defaults['readonly'] = readonly
        if remote is not None:
            self._attr_group_defaults['remote'] = remote
        if inherit is not None:
            self._attr_group_defaults['inherit'] = inherit

def create_group(
        cls: type, readonly: OptBool = None, remote: OptBool = None,
        inherit: OptBool = None) -> Group:
    """Create new Attribute Group.

    Creates a new Attribute Group of a given Attribute Group Class with given,
    group settings. The instantiation by this contructor is mandatory for
    independent Attribute Groups of same classes, since the class has to be
    created per instance.

    Args:
        cls: Attribute Group Class
        readonly: Boolean value, which superseeds the contained attributes
            read-only behaviour. For the values True or False, all contained
            attributes respectively are read-only or read-writable. By the
            default value None, the attributes' settings are not superseeded.
        remote: Boolean value, which superseeds the contained attributes remote
            behaviour. For the value True, all contained attributes are shared
            attributes of the parent attribute group, which must be referenced
            and contain the respetive attributes, or an error is raised. For the
            value False, all contained atributes are handled locally, regardless
            of a parent group. By the default value None, the attributes'
            settings are not superseeded.
        inherit: Boolean value, which superseeds the contained attributes
            inheritance behaviour. For the value True, all contained attributes
            inherit their default values from the attribute values of the parent
            attribute group, which must be referenced and contain the respetive
            attributes, or an error is raised. For the value False, the default
            values of the contained atributes are handled locally, regardless of
            a parent group. By the default value None, the attributes settings
            are not superseeded.

    Returns:
        New Attribute Group instance of given Attribute Group Class.

    """
    new_cls = type(cls.__name__, (cls,), {})
    new_obj = new_cls(readonly=readonly, remote=remote, inherit=inherit)

    return new_obj

#
# Attribute Base Class
#

class Attribute(property):
    """Extended data descriptor for Attributes.

    Data descriptors are classes, used for binding attributes to fields and
    thereby provide an abstraction layer that facilitates encapsulation and
    modularity. When any class contains a data descriptor as a class attribute
    (i.e. a method), then the data descriptor class defines the accessor,
    mutator and manager methods of the respective attribute.

    A succinct way of building data descriptors is given by the `property`_
    factory, which automatically creates a getter, a setters and a deleter
    method from it's passed arguments. Thereupon the `Attribute` class extends
    the options to control the behaviour of the Attribute by the following
    amplifications:
        * Declaration of accessor and mutator by forward references
        * Type checking against given classinfo
        * Read-only attributes
        * Default values by a fixed value, a factory function or by inheritance
            from a parent attribute group
        * Binding of fields within a different dictionary of the, e.g. to allow
            an aggregation of the fields by their respective attribute type.
        * Binding of fields to different keys, then the attributes name, e.g. to
            provide different accessors for the same key
        * Remote attribute handling of a parent attribute, to allow shared
            attributes
        * Aggregation of attributes by categories

    Args:
        fget: Callable or String, which points to a valid Method of the
            underlying Attribute Group, which is used as the accessor method
            of the attribute.
        fset: Callable or String, which points to a valid Method of the
            underlying Attribute Group, which is used as the mutator method
            of the attribute.
        fdel: Callable or String, which points to a valid Method of the
            underlying Attribute Group, which is used as the destructor method
            of the attribute.
        doc:
        classinfo:
        default: Default value, which is returned for a get request to an unset
            field.
        default_factory: If provided, it must be a zero-argument callable that
            will be called when a default value is needed for this field. Among
            other purposes, this can be used to specify fields with mutable
            default values.
        binddict:
        bindkey:
        remote:
        inherit:
        readonly: Boolean value which determines if the attribute is read-only
        category: Attribute categories allow a free aggregation of attributes by
            their respective category values.

    """

    #
    # Instance Variables
    #

    name: str
    sget: OptStr
    sset: OptStr
    sdel: OptStr
    classinfo: OptClassInfo
    readonly: bool
    default: Any
    default_factory: OptCallable
    binddict: OptStr
    bindkey: OptStr
    inherit: bool
    remote: bool
    category: OptStr

    #
    # Events
    #

    def __init__(self,
            fget: OptCallOrStr = None, fset: OptCallOrStr = None,
            fdel: OptCallOrStr = None, doc: OptStr = None,
            classinfo: OptClassInfo = None, readonly: bool = False,
            default: Any = None, default_factory: OptCallable = None,
            binddict: OptStr = None, bindkey: OptStr = None,
            remote: bool = False, inherit: bool = False,
            category: OptStr = None) -> None:
        """Initialize Attribute Descriptor."""
        # Initialize Property Class
        super_kwds: dict = {
            'fget': fget if callable(fget) else None,
            'fset': fget if callable(fset) else None,
            'fdel': fdel if callable(fdel) else None,
            'doc': doc}
        super().__init__(**super_kwds)

        # Check Types of Arguments
        check.has_opt_type("argument 'classinfo'", classinfo, (type, tuple))
        check.has_type("argument 'readonly'", readonly, bool)
        check.has_opt_type("argument 'binddict'", binddict, str)
        check.has_opt_type("argument 'bindkey'", bindkey, str)
        check.has_type("argument 'remote'", inherit, bool)
        check.has_type("argument 'inherit'", inherit, bool)
        check.has_opt_type("argument 'category'", category, str)

        # Set Instance Attributes to Argument Values
        self.sget = fget if isinstance(fget, str) else None
        self.sset = fset if isinstance(fset, str) else None
        self.sdel = fdel if isinstance(fdel, str) else None
        self.classinfo = classinfo
        self.default = default
        self.default_factory = default_factory
        self.readonly = readonly
        self.binddict = binddict
        self.bindkey = bindkey
        self.remote = remote
        self.inherit = inherit
        self.category = category

    def __set_name__(self, cls: type, name: str) -> None:
        """Set name of the Attribute."""
        self.name = name

    def __get__(self, obj: Group, cls: OptType = None) -> Any:
        """Bypass get request."""
        if self._is_remote(obj):
            return self._get_remote(obj)
        if callable(self.fget):
            return self.fget(obj) # type: ignore
        if isinstance(self.sget, str):
            return getattr(obj, self.sget, void)()
        binddict = self._get_bindict(obj)
        bindkey = self._get_bindkey(obj)
        default = self._get_default(obj)
        return binddict.get(bindkey, default)

    def __set__(self, obj: Group, val: Any) -> None:
        """Bypass and type check set request."""
        if self._get_readonly(obj):
            raise ReadOnlyAttrError(obj, self.name)
        if self._is_remote(obj):
            self._set_remote(obj, val)
            return
        classinfo = self.classinfo
        if classinfo and not isinstance(val, type(self.default)):
            check.has_type(f"attribute '{self.name}'", val, classinfo)
        if callable(self.fset):
            self.fset(obj, val) # type: ignore
            return
        if isinstance(self.sset, str):
            getattr(obj, self.sset, void)(val)
            return
        binddict = self._get_bindict(obj)
        bindkey = self._get_bindkey(obj)
        binddict[bindkey] = val

    #
    # Protected Methods
    #

    def _get_bindict(self, obj: Group) -> dict:
        binddict = self.binddict
        if not binddict:
            return obj.__dict__
        check.has_attr(obj, binddict)
        check.has_type(binddict, getattr(obj, binddict), dict)
        return getattr(obj, binddict)

    def _get_bindkey(self, obj: Group) -> str:
        prefix = obj._attr_group_prefix # pylint: disable=W0212
        name = self.bindkey or self.name
        if prefix:
            return '.'.join([prefix, name])
        return name

    def _get_default(self, obj: Group) -> Any:
        group = obj._attr_group_defaults # pylint: disable=W0212

        # Inherit default value from parent
        inherit = group.get('inherit', self.inherit)
        if inherit:
            parent = obj._attr_group_parent # pylint: disable=W0212
            if parent and hasattr(parent, self.name):
                return getattr(parent, self.name)

        # Get default value from factory
        if callable(self.default_factory):
            return self.default_factory()

        return self.default

    def _get_readonly(self, obj: Group) -> bool:
        return obj._attr_group_defaults.get( # pylint: disable=W0212
            'readonly', self.readonly)

    def _is_remote(self, obj: Group) -> bool:
        return obj._attr_group_defaults.get( # pylint: disable=W0212
            'remote', self.remote)

    def _get_remote(self, obj: Group) -> bool:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        return getattr(parent, self.name, self.default)

    def _set_remote(self, obj: Group, val: Any) -> None:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        setattr(parent, self.name, val)

#
# Attribute Container Base Class Standard Attribute Classes for Containers
#

class Content(Attribute):
    """Attributes for persistent content objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_dict_data'

class MetaData(Attribute):
    """Attributes for persistent metadata objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['inherit'] = kwds.get('inherit', True)
        super().__init__(*args, **kwds)
        self.binddict = '_dict_meta'

class Temporary(Attribute):
    """Attributes for non persistent stored objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_dict_temp'

class Virtual(Attribute):
    """Attributes for non persistent virtual objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        if not isinstance(self.fget, CallableClasses):
            if not isinstance(self.sget, str):
                raise MissingKwError('fget', self)
        self.readonly = not (
            isinstance(self.fset, CallableClasses)
            or isinstance(self.sget, str))

class Container(Group):
    """Base class for Attribute Containers.

    Attribute Containers are Attribute Groups, which support Standard Attribute
    Classes for Content, MetaData, Temporary Data and Virtual Attributes.
    Thereupon Attribute Containers provide a public interface to access and
    control it's contained Attributes and Attribute Groups.

    Args:
        parent:
        readonly: Boolean value, which superseeds the contained attributes
            read-only behaviour. For the values True or False, all contained
            attributes respectively are read-only or read-writable. By the
            default value None, the attributes' settings are not superseeded.
        remote: Boolean value, which superseeds the contained attributes remote
            behaviour. For the value True, all contained attributes are shared
            attributes of the parent attribute group, which must be referenced
            and contain the respetive attributes, or an error is raised. For the
            value False, all contained atributes are handled locally, regardless
            of a parent group. By the default value None, the attributes'
            settings are not superseeded.
        inherit: Boolean value, which superseeds the contained attributes
            inheritance behaviour. For the value True, all contained attributes
            inherit their default values from the attribute values of the parent
            attribute group, which must be referenced and contain the respetive
            attributes, or an error is raised. For the value False, the default
            values of the contained atributes are handled locally, regardless of
            a parent group. By the default value None, the attributes settings
            are not superseeded.

    """

    _dict_data: StrDict
    _dict_meta: StrDict
    _dict_temp: StrDict

    #
    # Public Attributes
    #

    parent: property = Virtual(classinfo=Group,
        fget='_get_attr_group_parent', fset='_set_attr_group_parent')
    parent.__doc__ = """Reference to parent container object."""

    #
    # Events
    #

    def __init__(
            self, parent: Optional[Group] = None, readonly: OptBool = None,
            remote: OptBool = None, inherit: OptBool = None,
            data: OptStrDict = None, meta: OptStrDict = None) -> None:
        """Initialize Instance Variables."""
        # Initialize Attribute Group
        super().__init__(readonly=readonly, remote=remote, inherit=inherit)

        # Initialize dictinaries for content, metadata and temporary fields
        self._dict_data = {}
        self._dict_meta = {}
        self._dict_temp = {}

        # Bind attribute subgroups to fields and update subgroup settings
        self._bind_attr_groups()
        if parent:
            self._set_attr_group_parent(parent)
        self._set_attr_group_defaults(
            readonly=readonly, remote=remote, inherit=inherit)

        # Update content and metedata field values from given arguments
        if data:
            self._set_attr_values(data, classinfo=Content)
        if meta:
            self._set_attr_values(meta, classinfo=MetaData)

    #
    # Access Attributes by their group name, ClassInfo and category
    #

    @classmethod
    def _get_attr_groups(cls) -> StrDict:
        def get_groups(cls: type) -> StrDict:
            groups: StrDict = {}
            for base in cls.__mro__:
                for name, obj in base.__dict__.items():
                    if not isinstance(obj, Group):
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
                if not isinstance(val, Attribute):
                    continue
                if category and not getattr(val, 'category', None) == category:
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
                if not isinstance(obj, Attribute):
                    continue
                if category and not getattr(obj, 'category', None) == category:
                    continue
                if classinfo and not isinstance(obj, classinfo):
                    continue
                types[name] = getattr(obj, 'classinfo', None)
        return types

    def _bind_attr_groups(self) -> None:
        for fqn in self._get_attr_groups():

            # Get attribute group by stepping the attribute hierarchy
            # downwards the tokens of the fully qualified name
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)

            # Set group name and prefix to avoid namespace collision
            # within dictionary buffers
            setattr(obj, '_attr_group_name', fqn.rsplit('.', 1)[-1])
            setattr(obj, '_attr_group_prefix', fqn)

            # Bind dictionary buffers
            setattr(obj, '_dict_data', self._dict_data)
            setattr(obj, '_dict_meta', self._dict_meta)
            setattr(obj, '_dict_temp', self._dict_temp)

    def _get_attr_group_parent(self) -> Optional[Group]:
        return self._attr_group_parent

    def _set_attr_group_parent(self, parent: Group) -> None:
        self._attr_group_parent = parent

        # Update group parents by simultaneously stepping downwards the object
        # hierachy, within self and within the parent, to obtain the same
        # attribute hierarchy: e.g. parent.group.attr -> child.group.attr
        for fqn in self._get_attr_groups():
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)
                if parent:
                    parent = getattr(parent, attr, None)
            obj._attr_group_parent = parent # pylint: disable=W0212

    def _get_attr_group_defaults(self) -> OptDict:
        return self._attr_group_defaults

    def _set_attr_group_defaults(self, **kwds: Any) -> None:
        stated = {key: val for key, val in kwds.items() if val is not None}
        self._attr_group_defaults = {**self._attr_group_defaults, **stated}

        # Update groups defaults by stepping downwards the object hierarchy
        for fqn in self._get_attr_groups():
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)
            obj._attr_group_defaults = { # pylint: disable=W0212
                **obj._attr_group_defaults, **stated} # pylint: disable=W0212

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

#
# Dublin Core (DC) Attributes
#

class DCAttr(MetaData):
    """Dublin Core Metadata Attribute."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.classinfo = self.classinfo or str
        self.inherit = True

class DCGroup(Group):
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

    date: property = DCAttr(
        classinfo=Date, default_factory=Date.now, category='instantiation')
    date.__doc__ = """
    A point or period of time associated with an event in the lifecycle of the
    resource. Date may be used to express temporal information at any level of
    granularity. Recommended best practice is to use an encoding scheme, such as
    the W3CDTF profile of ISO 8601 [W3CDTF]_.

    .. [W3CDTF] http://www.w3.org/TR/NOTE-datetime
    """
