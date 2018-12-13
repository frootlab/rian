# -*- coding: utf-8 -*-
"""Attributes, Attribute Groups and Containers."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import check
from nemoa.errors import InvalidAttrError, MissingKwError, ReadOnlyAttrError
from nemoa.types import Any, Date, OptClassInfo, Optional, TypeHint
from nemoa.types import OptStr, OptStrDict, OptType, StrDict, StrList, void
from nemoa.types import OptDict, OptBool, Union, Callable

#
# Structural Types
#

OptCallOrStr = Optional[Union[Callable, str]]
OptGroup = Optional['Group']

#
# Group Class and Constructor
#

class Group:
    """Base Class for Attribute Groups.

    Attribute Groups are used to group a set of attribute declarations, so that
    they can be incorporated as a group into complex type definitions. Attribute
    Groups also allow superseeding the settings of their contained attributes to
    control the group behaviour in different applications.

    Args:
        parent: Reference to parent :class:'attribute group
            <nemoa.base.attrib.Group>', which is used for inheritance and
            shared attributes. By default no parent is referenced.
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
    _attr_group_parent: OptGroup
    _attr_group_defaults: dict

    #
    # Special Methods
    #

    def __init__(
            self, parent: OptGroup = None, readonly: OptBool = None,
            remote: OptBool = None, inherit: OptBool = None) -> None:
        self._attr_group_name = ''
        self._attr_group_prefix = ''
        self._attr_group_parent = parent
        self._attr_group_defaults = {}
        if readonly is not None:
            self._attr_group_defaults['readonly'] = readonly
        if remote is not None:
            self._attr_group_defaults['remote'] = remote
        if inherit is not None:
            self._attr_group_defaults['inherit'] = inherit

def create_group(
        cls: type, parent: Optional[Group] = None, readonly: OptBool = None,
        remote: OptBool = None, inherit: OptBool = None) -> Group:
    """Create new Attribute Group.

    Creates a new Attribute Group of a given Attribute Group Class with given,
    group settings. The instantiation by this contructor is mandatory for
    independent Attribute Groups of same classes, since the class has to be
    created per instance.

    Args:
        cls: Subclass of the :class:'Group class <nemoa.base.attrib.Group>'
        parent: Reference to parent object, which is used for attribute
            inheritance and remote/shared attributes. If provided, the parent
            object is required to by an instance of a subclass of the
            :class:'Group class <nemoa.base.attrib.Group>'. By default no parent
            object is referenced.
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
# Attribute Class
#

class Attribute(property):
    """Extended data descriptor for Attributes.

    Data descriptors are classes, used for binding attributes to fields and
    thereby provide an abstraction layer that facilitates encapsulation and
    modularity. When any class contains a data descriptor as a class attribute
    (i.e. a method), then the data descriptor class defines the accessor,
    mutator and manager methods of the respective attribute.

    A succinct way of building data descriptors is given by the :class:`property
    class <property>`, which automatically creates an accessor, a mutator and a
    destructor method from it's passed arguments. The `Attribute` class extends
    this automation by additional options for managing and controlling the
    behaviour of the attribute:

        * Declaration of accessor, mutator and destructor methods by *forward
          references*
        * Automatic *type checking* against given data type(s)
        * Restriction to *read-only* attributes
        * Setting of *default values*, ether as a fixed value, a factory
          function or by inheritance from a parental object
        * Binding to *arbitrary mappings*, to allow a namespace aggregation of
          the attributes data e.g. by their logical attribute type.
        * Binding to *arbitrary keys*, e.g. to provide different accessors to
          identical attribute data
        * Handling of *remote attributes* of a parent object, to allow sharing
          of attributes between different objects
        * Locical aggregation of attributes by *categories*

    Args:
        fget: Accessor method of the attribute. If provided, it must be a
            callable or a string, that references a valid method of the owner
            instance.
        fset: Mutator method of the attribute. If provided, it must be a
            callable or a string, that references a valid method of the owner
            instance.
        fdel: Destructor method of the attribute. If provided, it must be a
            callable or a string, that references a valid method of the owner
            instance.
        doc: Docstring of the attribute, which is retained throughout the
            runtime of the application. For more information and doctring
            convention see :PEP:`257`.
        dtype: Data type definition of the attribute given as a type or a tuple
            of types, which is used for type checking assignments to the
            attribute. If the value passed to the mutator method is not an
            instance of any of the given types, a
            :class:`~nemoa.errors.InvalidTypeError` is raised. By default type
            checking is disabled.
        default: Default value, which is returned by calling the getter method,
            if the following conditions are met: (1) The attribute is not a
            remote attribute of the parent, (2) the attribute is not inherited
            from the parent, (3) the attribute has not yet been set, (4) the
            attribute has no default factory.
        factory: Default method, which is called if a default value is required.
            If provided, it must be a callable or a string, that references a
            valid method of the owner instance. This method is called, if the
            following conditions are met: (1) The attribute is not a remote
            attribute of the parent, (2) the attribute is not inherited from the
            parent, (3) the attribute has not yet been set.
        binddict: Name of the dictionary (or arbitrary mapping), which comprises
            the key, which is used to store the attribute data. If provided, it
            must be a string, that references an attribute of the owner
            instance, with type mapping. By default, the special attribute
            :attr:`~object.__dict__` is used.
        bindkey: Name of key within the bound dictionary, which is used to store
            the attribute data. By default the name of the attribute is used.
        remote: Boolean value which determines, if the accessor, mutator and
            destructor methods are bypassed to the currently referenced parent
            attribute group. If no attribute group is referenced or the
            referenced attribute group, does not contain an attribute of the
            same name, a ReferenceError is raised on any request to the
            Attribute.
        inherit: Boolean value which determines if the default value is
            inherited from the (current) value of a referenced parent object. If
            no parent object is referenced or the referenced object, does not
            contain an attribute of the same name, then the default value is
            retrieved from the default factory, or if not given, from the
            default value. By default the default value is not inherited from
            the parent.
        readonly: Boolean value which determines, if the attribute is a
            read-only attribute. For read-only attributes the mutator method
            raises an AttributeError on requests to the mutator method. By
            default the attribute is read-writable.
        category: Optional name of category, which allows a logical aggregation
            of attributes. If given, that category has to be a string. By
            default not category is set.

    """

    #
    # Instance Variables
    #

    name: str
    sget: OptStr
    sset: OptStr
    sdel: OptStr
    dtype: OptClassInfo
    readonly: bool
    default: Any
    factory: OptCallOrStr
    binddict: OptStr
    bindkey: OptStr
    inherit: bool
    remote: bool
    category: OptStr

    #
    # Special Methods
    #

    def __init__(self,
            fget: OptCallOrStr = None, fset: OptCallOrStr = None,
            fdel: OptCallOrStr = None, doc: OptStr = None,
            dtype: OptClassInfo = None, readonly: bool = False,
            default: Any = None, factory: OptCallOrStr = None,
            binddict: OptStr = None, bindkey: OptStr = None,
            remote: bool = False, inherit: bool = False,
            category: OptStr = None) -> None:

        # Initialize Property Class
        super().__init__( # type: ignore
            fget=fget if callable(fget) else None,
            fset=fget if callable(fset) else None,
            fdel=fdel if callable(fdel) else None,
            doc=doc)

        # Check Types of Arguments
        check.has_opt_type("'dtype'", dtype, TypeHint)
        check.has_type("'readonly'", readonly, bool)
        check.has_opt_type("'binddict'", binddict, str)
        check.has_opt_type("'bindkey'", bindkey, str)
        check.has_type("'remote'", inherit, bool)
        check.has_type("'inherit'", inherit, bool)
        check.has_opt_type("'category'", category, str)

        # Bind Instance Attributes to Argument Values
        self.sget = fget if isinstance(fget, str) else None
        self.sset = fset if isinstance(fset, str) else None
        self.sdel = fdel if isinstance(fdel, str) else None
        self.dtype = dtype
        self.default = default
        self.factory = factory
        self.readonly = readonly
        self.binddict = binddict
        self.bindkey = bindkey
        self.remote = remote
        self.inherit = inherit
        self.category = category

    def __set_name__(self, cls: type, name: str) -> None:
        self.name = name # Set name of the Attribute

    def __get__(self, obj: Group, cls: OptType = None) -> Any:
        # Bypass get requests
        if self._is_remote(obj):
            return self._get_remote(obj)
        if callable(self.fget):
            return self.fget(obj) # type: ignore
        if isinstance(self.sget, str):
            return getattr(obj, self.sget, void)()
        binddict = self._get_bindict(obj)
        bindkey = self._get_bindkey(obj)
        try:
            return binddict[bindkey]
        except KeyError:
            pass
        return self._get_default(obj)

    def __set__(self, obj: Group, val: Any) -> None:
        # Bypass and type check set requests
        if self._get_readonly(obj):
            raise ReadOnlyAttrError(obj, self.name)
        if self._is_remote(obj):
            self._set_remote(obj, val)
            return
        dtype = self.dtype
        if dtype and not isinstance(val, type(self.default)):
            check.has_type(f"attribute '{self.name}'", val, dtype)
        if callable(self.fset):
            self.fset(obj, val) # type: ignore
            return
        if isinstance(self.sset, str):
            getattr(obj, self.sset, void)(val)
            return
        binddict = self._get_bindict(obj)
        bindkey = self._get_bindkey(obj)
        binddict[bindkey] = val

    def __delete__(self, obj: Group) -> None:
        # Bypass delete requests
        if self._get_readonly(obj):
            raise ReadOnlyAttrError(obj, self.name)
        if self._is_remote(obj):
            self._del_remote(obj)
            return
        if callable(self.fdel):
            self.fdel(obj) # type: ignore
            return
        if isinstance(self.sdel, str):
            getattr(obj, self.sdel, void)()
            return
        binddict = self._get_bindict(obj)
        bindkey = self._get_bindkey(obj)
        del binddict[bindkey]

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

        # Get default value from default factory
        if isinstance(self.factory, str):
            if hasattr(obj, self.factory):
                return getattr(obj, self.factory)()
        elif callable(self.factory):
            return self.factory()

        return self.default

    def _get_readonly(self, obj: Group) -> bool:
        if obj is None:
            return self.readonly
        return obj._attr_group_defaults.get( # pylint: disable=W0212
            'readonly', self.readonly)

    def _is_remote(self, obj: Group) -> bool:
        if obj is None:
            return self.remote
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

    def _del_remote(self, obj: Group) -> None:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        delattr(parent, self.name)

#
# Attribute Container Base Class Standard Attribute Classes for Containers
#

class Content(Attribute):
    """Attributes for persistent content storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_data_content'

class MetaData(Attribute):
    """Attributes for persistent metadata storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['inherit'] = kwds.get('inherit', True)
        super().__init__(*args, **kwds)
        self.binddict = '_data_metadata'

class Temporary(Attribute):
    """Attributes for non persistent storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_data_temporary'

class Virtual(Attribute):
    """Attributes for non persistent virtual objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        if not callable(self.fget):
            if not isinstance(self.sget, str):
                raise MissingKwError('fget', self)
        self.readonly = not (callable(self.fset) or isinstance(self.sget, str))

class Container(Group):
    """Base class for Attribute Containers.

    Attribute Containers are Attribute Groups, which support Standard Attribute
    Classes for Content, MetaData, Temporary Data and Virtual Attributes.
    Thereupon Attribute Containers provide a public interface to access and
    control it's contained Attributes and Attribute Groups.

    Args:
        parent: Reference to parent :class:'attribute group
            <nemoa.base.attrib.Group>', which is used for inheritance and
            shared attributes. By default no parent is referenced.
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
        content:
        metadata:

    """

    _data_content: StrDict
    _data_metadata: StrDict
    _data_temporary: StrDict

    #
    # Public Attributes
    #

    parent: property = Virtual(fget='_get_attr_group_parent',
        fset='_set_attr_group_parent', dtype=Group)
    parent.__doc__ = """Reference to parent Attribute Group."""

    #
    # Special Methods
    #

    def __init__(
            self, parent: Optional[Group] = None, readonly: OptBool = None,
            remote: OptBool = None, inherit: OptBool = None,
            content: OptStrDict = None, metadata: OptStrDict = None) -> None:
        """Initialize Instance Variables."""
        # Initialize Attribute Group
        super().__init__(
            parent=parent, readonly=readonly, remote=remote, inherit=inherit)

        # Initialize dictinaries for content, metadata and temporary fields
        self._data_content = content or {}
        self._data_metadata = metadata or {}
        self._data_temporary = {}

        # Bind Attribute Subgroups to fields and update Subgroup Settings
        self._bind_attr_subgroups()
        self._upd_attr_subgroup_parent()
        self._upd_attr_subgroup_defaults()

    #
    # Access Attributes by their group name, ClassInfo and category
    #

    @classmethod
    def _get_attr_subgroups(cls) -> StrDict:
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

        # Locate the attribute subgroup, that corresponds to the given group
        # name. By default identify the current class as attribute group
        if group:
            groups = cls._get_attr_subgroups()
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
            groups = cls._get_attr_subgroups()
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

    def _get_attr_group_parent(self) -> Optional[Group]:
        return self._attr_group_parent

    def _set_attr_group_parent(self, group: Group) -> None:
        self._attr_group_parent = group
        self._upd_attr_subgroup_parent()

    def _get_attr_group_defaults(self) -> OptDict:
        return self._attr_group_defaults

    def _bind_attr_subgroups(self) -> None:
        for fqn in self._get_attr_subgroups():

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
            setattr(obj, '_data_content', self._data_content)
            setattr(obj, '_data_metadata', self._data_metadata)
            setattr(obj, '_data_temporary', self._data_temporary)

    def _upd_attr_subgroup_parent(self) -> None:
        parent = self._attr_group_parent
        if not parent:
            return

        # Update group parents by simultaneously stepping downwards the object
        # hierachy, within self and within the parent, to obtain the same
        # attribute hierarchy: e.g. parent.group.attr -> child.group.attr
        for fqn in self._get_attr_subgroups():
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)
                if parent:
                    parent = getattr(parent, attr, None)
            obj._attr_group_parent = parent # pylint: disable=W0212

    def _upd_attr_subgroup_defaults(self) -> None:
        defaults = self._attr_group_defaults

        # Update groups defaults by stepping downwards the object hierarchy
        for fqn in self._get_attr_subgroups():
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)
            obj._attr_group_defaults.update(defaults) # pylint: disable=W0212

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
        self.dtype = self.dtype or str
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
    An account of the resource. Description may include - but is not limited to
    - an abstract, a table of contents, a graphical representation, or a
    free-text account of the resource.
    """

    type: property = DCAttr(category='content')
    type.__doc__ = """
    The nature or genre of the resource. Recommended best practice is to use a
    controlled vocabulary such as the DCMI Type Vocabulary [DCMI-TYPE]_. To
    describe the file format, physical medium, or dimensions of the resource,
    use the Format element.
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
    of a Creator should be used to indicate the otree.
    """

    publisher: property = DCAttr(category='property')
    publisher.__doc__ = """
    An entity responsible for making the resource available. Examples of a
    Publisher include a person, an organization, or a service. Typically, the
    name of a Publisher should be used to indicate the otree.
    """

    contributor: property = DCAttr(category='property')
    contributor.__doc__ = """
    An entity responsible for making contributions to the resource. Examples of
    a Contributor include a person, an organization, or a service. Typically,
    the name of a Contributor should be used to indicate the otree.
    """

    rights: property = DCAttr(category='property')
    rights.__doc__ = """
    Information about rights held in and over the resource. Typically, rights
    information includes a statement about various property rights associated
    with the resource, including intellectual property rights.
    """

    identifier: property = DCAttr(category='instance')
    identifier.__doc__ = """
    An unambiguous reference to the resource within a given context. Recommended
    best practice is to identify the resource by means of a string or number
    conforming to a formal identification system. Examples of formal
    identification systems include the Uniform Resource Identifier (URI)
    (including the Uniform Resource Locator (URL), the Digital Object Identifier
    (DOI) and the International Standard Book Number (ISBN).
    """

    format: property = DCAttr(category='instance')
    format.__doc__ = """
    The file format, physical medium, or dimensions of the resource. Examples of
    dimensions include size and duration. Recommended best practice is to use a
    controlled vocabulary such as the list of Internet Media Types [MIME]_.
    """

    language: property = DCAttr(category='instance')
    language.__doc__ = """
    A language of the resource. Recommended best practice is to use a controlled
    vocabulary such as :RFC:`4646`.
    """

    date: property = DCAttr(dtype=Date, factory=Date.now, category='instance')
    date.__doc__ = """
    A point or period of time associated with an event in the lifecycle of the
    resource. Date may be used to express temporal information at any level of
    granularity. Recommended best practice is to use an encoding scheme, such as
    the W3CDTF profile of ISO 8601 [W3CDTF]_.
    """
