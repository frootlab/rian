# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Attributes and Attribute Groups."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import copy
from typing import Any, Optional, Union, Callable
from nemoa import errors
from nemoa.base import abc, check
from nemoa.types import OptClassInfo, TypeHint, OptStr, OptStrDict, OptType
from nemoa.types import StrDict, StrList, void, OptDict, OptBool

#
# Structural Types
#

OptCallOrStr = Optional[Union[Callable, str]]

#
# Attribute Class
#

class Attribute(property, abc.Isolated):
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
            fset=fset if callable(fset) else None,
            fdel=fdel if callable(fdel) else None,
            doc=doc)

        # Check Types
        check.has_opt_type("'dtype'", dtype, TypeHint)
        check.has_type("'readonly'", readonly, bool)
        check.has_opt_type("'binddict'", binddict, str)
        check.has_opt_type("'bindkey'", bindkey, str)
        check.has_type("'remote'", inherit, bool)
        check.has_type("'inherit'", inherit, bool)
        check.has_opt_type("'category'", category, str)

        # Bind Instance Attributes to given Arguments
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

    def __get__(self, obj: 'Group', cls: OptType = None) -> Any:
        # Bypass getter requests
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

    def __set__(self, obj: 'Group', val: Any) -> None:
        # Bypass and type check setter requests
        if self._get_readonly(obj):
            raise errors.ReadOnlyAttrError(obj, self.name)
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

    def __delete__(self, obj: 'Group') -> None:
        # Bypass destructor requests
        if self._get_readonly(obj):
            raise errors.ReadOnlyAttrError(obj, self.name)
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

    def _get_bindict(self, obj: 'Group') -> dict:
        binddict = self.binddict
        if not binddict:
            return obj.__dict__
        check.has_attr(obj, binddict)
        check.has_type(binddict, getattr(obj, binddict), dict)
        return getattr(obj, binddict)

    def _get_bindkey(self, obj: 'Group') -> str:
        prefix = obj._attr_group_prefix # pylint: disable=W0212
        name = self.bindkey or self.name
        if prefix:
            return '.'.join([prefix, name])
        return name

    def _get_default(self, obj: 'Group') -> Any:
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

    def _get_readonly(self, obj: 'Group') -> bool:
        if obj is None:
            return self.readonly
        return obj._attr_group_defaults.get( # pylint: disable=W0212
            'readonly', self.readonly)

    def _is_remote(self, obj: 'Group') -> bool:
        if obj is None:
            return self.remote
        return obj._attr_group_defaults.get( # pylint: disable=W0212
            'remote', self.remote)

    def _get_remote(self, obj: 'Group') -> bool:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        return getattr(parent, self.name, self.default)

    def _set_remote(self, obj: 'Group', val: Any) -> None:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        setattr(parent, self.name, val)

    def _del_remote(self, obj: 'Group') -> None:
        parent = obj._attr_group_parent # pylint: disable=W0212
        if not parent:
            raise ReferenceError() # TODO
        delattr(parent, self.name)

#
# Standard Attribute Classes
#

class Content(Attribute):
    """Attributes for persistent content storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_attr_group_data'

class MetaData(Attribute):
    """Attributes for persistent metadata storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        kwds['inherit'] = kwds.get('inherit', True)
        super().__init__(*args, **kwds)
        self.binddict = '_attr_group_meta'

class Temporary(Attribute):
    """Attributes for non persistent storage objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        self.binddict = '_attr_group_temp'

class Virtual(Attribute):
    """Attributes for non persistent virtual objects."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize default values of attribute descriptor."""
        super().__init__(*args, **kwds)
        if not callable(self.fget) and not isinstance(self.sget, str):
            raise errors.MissingKwError('fget', self)
        self.readonly = not (callable(self.fset) or isinstance(self.sget, str))

#
# Attribute Groups
#

class Group(abc.Isolated):
    """Class for Attribute Groups.

    Attribute Groups are used to bind attributes (and other attribute groups)
    into tree structured objects with a hierarchical control interface. This
    includes a common interface to access and mutate the values of it's
    contained (sub)attributes as well as a common interface to superseed the
    settings of it's contained (sub)groups to control the group behaviour in
    different applications.

    Args:
        parent: Reference to logical parent :class:'attribute group
            <nemoa.base.attrib.Group>', which is used for inheritance and
            shared attributes. By default no parent is referenced. Note: The
            logical parent does not denote the attribute group, that contains
            this group, but an equally structured attribute, which is used
            to infere dynamical values for the attributes.
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
    __slots__ = [
        '_attr_group_init_state', '_attr_group_name', '_attr_group_prefix',
        '_attr_group_parent', '_attr_group_defaults', '_attr_group_data',
        '_attr_group_meta', '_attr_group_temp']

    _attr_group_init_state: StrDict
    _attr_group_name: str
    _attr_group_prefix: str
    _attr_group_parent: Optional['Group']
    _attr_group_defaults: StrDict
    _attr_group_data: StrDict
    _attr_group_meta: StrDict
    _attr_group_temp: StrDict

    #
    # Special Methods
    #

    def __init__(
            self, parent: Optional['Group'] = None, readonly: OptBool = None,
            remote: OptBool = None, inherit: OptBool = None,
            content: OptStrDict = None, metadata: OptStrDict = None) -> None:

        # When an Attribute Group countains furter Attribute Groups as
        # Subgroups, the Subgroups are bound to the Class and therefore shared
        # among the instances. To avoid this behaviour, the group class for any
        # instance is inherited from itself and created as a new class.
        self._create_attr_group()

        # Store initial state to allow later re-initialization, when
        # re-creating the Subgroups. Afterward initialize the instance with
        # initation states for settings, content, metadata and temporary storage
        state = {
            'parent': parent, 'readonly': readonly, 'remote': remote,
            'inherit': inherit, 'content': content, 'metadata': metadata}
        self._attr_group_init_state = state
        self._init_attr_group(state)

    def __repr__(self) -> str:
        return self.__class__.__name__

    #
    # Protected Class Methods
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
                raise errors.InvalidAttrError(cls, group)
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
                raise errors.InvalidAttrError(cls, group)
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

    #
    # Protected Methods
    #

    def _create_attr_group(self) -> None:

        # Create name space for new instance
        space: StrDict = {'__slots__': []}
        for attr in self._get_attr_subgroups():
            if '.' in attr:
                continue

            obj = getattr(self, attr)
            cls = type(obj)
            new_cls = type(cls.__name__, (cls, ), {'__slots__': []})
            space[attr] = new_cls(**obj._attr_group_init_state)
            del obj

        cls = self.__class__
        self.__class__ = type(cls.__name__, (cls, ), space)

    def _init_attr_group(self, state: StrDict) -> None:

        # Set Defaults
        self._attr_group_name = ''
        self._attr_group_prefix = ''
        self._attr_group_parent = state.get('parent', None)
        self._attr_group_defaults = {}
        self._attr_group_data = {}
        self._attr_group_meta = {}
        self._attr_group_temp = {}

        # Update attributes using state
        if isinstance(state.get('content', None), dict):
            self._attr_group_data = copy.deepcopy(state['content'])
        if isinstance(state.get('metadata', None), dict):
            self._attr_group_meta = copy.deepcopy(state['metadata'])
        if state.get('readonly', None) is not None:
            self._attr_group_defaults['readonly'] = state['readonly']
        if state.get('remote', None) is not None:
            self._attr_group_defaults['remote'] = state['remote']
        if state.get('inherit', None) is not None:
            self._attr_group_defaults['inherit'] = state['inherit']

        # Bind data dictionaries of subgroups
        self._bind_attr_subgroups()

        # Update Subgroup Settings
        self._upd_attr_subgroup_parent()
        self._upd_attr_subgroup_defaults()

    def _get_attr_group_parent(self) -> Optional['Group']:
        return self._attr_group_parent

    def _set_attr_group_parent(self, group: 'Group') -> None:
        self._attr_group_parent = group
        self._upd_attr_subgroup_parent()

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

    def _get_attr_group_defaults(self) -> OptDict:
        return self._attr_group_defaults

    def _bind_attr_subgroups(self) -> None:
        for fqn in self._get_attr_subgroups():

            # Get attribute group by stepping the attribute hierarchy
            # downwards the tokens of the fully qualified name
            obj = self
            for attr in fqn.split('.'):
                obj = getattr(obj, attr)

            # Set group name and prefix to avoid namespace collision within
            # dictionary buffers and bind dictionary buffers
            setattr(obj, '_attr_group_name', fqn.rsplit('.', 1)[-1])
            setattr(obj, '_attr_group_prefix', fqn)
            setattr(obj, '_attr_group_data', self._attr_group_data)
            setattr(obj, '_attr_group_meta', self._attr_group_meta)
            setattr(obj, '_attr_group_temp', self._attr_group_temp)

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

# #
# # Attribute Root Groups
# #
#
# class Root(Group):
#     """Base class for Attribute Root Groups.
#
#     Attribute Root Groups are Attribute Groups, which provide a public interface
#     to access and control it's contained Attributes and Attribute Groups.
#
#     Args:
#         parent: Reference to parent :class:'attribute group
#             <nemoa.base.attrib.Group>', which is used for inheritance and
#             shared attributes. By default no parent is referenced.
#         readonly: Boolean value, which superseeds the contained attributes
#             read-only behaviour. For the values True or False, all contained
#             attributes respectively are read-only or read-writable. By the
#             default value None, the attributes' settings are not superseeded.
#         remote: Boolean value, which superseeds the contained attributes remote
#             behaviour. For the value True, all contained attributes are shared
#             attributes of the parent attribute group, which must be referenced
#             and contain the respetive attributes, or an error is raised. For the
#             value False, all contained atributes are handled locally, regardless
#             of a parent group. By the default value None, the attributes'
#             settings are not superseeded.
#         inherit: Boolean value, which superseeds the contained attributes
#             inheritance behaviour. For the value True, all contained attributes
#             inherit their default values from the attribute values of the parent
#             attribute group, which must be referenced and contain the respetive
#             attributes, or an error is raised. For the value False, the default
#             values of the contained atributes are handled locally, regardless of
#             a parent group. By the default value None, the attributes settings
#             are not superseeded.
#         content:
#         metadata:
#
#     """
#
#     #
#     # Public Attributes
#     #
#
#     parent: property = Virtual(fget='_get_attr_group_parent',
#         fset='_set_attr_group_parent', dtype=Group)
#     parent.__doc__ = """Reference to parent Attribute Group."""
