# -*- coding: utf-8 -*-
"""Collection of frequently used base classes."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from typing import Any, Dict, Optional, Sequence, Union

PathLike = Sequence[Union['PathLike', str]]

class ObjectIP:
    """Base class for objects subjected to intellectual property.

    Resources like datasets, networks, systems and models share common
    descriptive metadata comprising authorship and copyright, as well as
    administrative metadata like branch and version. This base class is
    intended to provide a unified interface to access those attributes.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute.
        copyright (str): Notice of statutorily prescribed form that informs
            users of the underlying resource to published copyright ownership.
            Hint: Read- & writeable wrapping attribute.
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute.
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute.
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute.
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute.
        path (str): Path to a file containing or referencing the
            resource.
            Hint: Read- & writeable wrapping attribute.
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute.
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute.

    """

    _attr: Dict[str, int] = {
        'author': 0b11, 'email': 0b11, 'license': 0b11, 'copyright': 0b11,
        'fullname': 0b01, 'name': 0b11, 'branch': 0b11, 'version': 0b11,
        'about': 0b11, 'type': 0b01, 'path': 0b11
    }

    _config: Optional[Dict[str, dict]] = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Import object configuration and content from dictionary."""

        if self._config is None: self._config = {}

        self._set_copy(*args, **kwargs)

    def __getattr__(self, key: str) -> None:
        """Attribute wrapper for getter methods."""

        if key in self._attr:
            if not self._attr[key] & 0b01: raise AttributeError(
                f"attribute '{key}' is not readable")
            if not hasattr(self, '_get_' + key): raise AttributeError(
                f"{self.__class__.__name__} instance "
                f"has no attribute '_get_{key}'")
            return getattr(self, '_get_' + key)()

        raise AttributeError(
            f"{self.__class__.__name__} instance "
            f"has no attribute '{key}'")

    def __setattr__(self, key: str, val: Any) -> None:
        """Attribute wrapper to setter methods."""

        if key in self._attr:
            if not self._attr[key] & 0b10: raise AttributeError(
                f"attribute '{key}' is not writeable")
            if not hasattr(self, '_set_' + key): raise AttributeError(
                f"{self.__class__.__name__} instance has "
                f"no attribute '_set_{key}'")
            return getattr(self, '_set_' + key)(val)

        self.__dict__[key] = val

    def get(self, key: str = 'name', *args: Any, **kwargs: Any) -> Any:
        """Call private getter methods of the class instance.

        Returns:
            Arbitrary typed return value of the respective private getter
            method of the class instance.

        """

        # get readable attributes
        if self._attr.get(key, 0b00) & 0b01:
            return getattr(self, '_get_' + key)(*args, **kwargs)

        # call getter method if it exists
        if hasattr(self, '_get_' + key):
            return getattr(self, '_get_' + key)(*args, **kwargs)

        raise KeyError(f"key '{key}' is not valid")

    def _get_config(self, key: Optional[str] = None) -> Any:
        """Get configuration or configuration value.


        """

        import copy
        conf = self._config or {}
        if key is None: return copy.deepcopy(conf)
        if not isinstance(key, str): raise TypeError(
            "argument 'key' is required to be of type 'str' or 'None', "
            f"not '{type(key)}'")
        if key in conf:
            if isinstance(conf[key], dict): return copy.deepcopy(conf)
            return conf[key]

        raise KeyError(f"key '{key}' is not valid")

    def _get_about(self) -> Optional[str]:
        """Get a short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            String containing a description of the resource.

        """

        return self._config.get('about', None)

    def _get_author(self) -> str:
        """Get the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            String containing the name of the author.

        """

        return self._config.get('author', None)

    def _get_branch(self) -> Optional[str]:
        """Get the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            String containing the name of the branch.

        """

        return self._config.get('branch', None)

    def _get_copyright(self) -> Optional[str]:
        """Get the copyright notice of the resource.

        Notice of statutorily prescribed form that informs users of the
        underlying resource to published copyright ownership.

        Returns:
            String containing the copyright notice of the resource.

        """

        return self._config.get('copyright', None)

    def _get_email(self) -> Optional[str]:
        """Get an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            String containing an email address of the author.

        """

        return self._config.get('email', None)

    def _get_fullname(self) -> Optional[str]:
        """Get full name including 'branch' and 'version'.

        String concatenation of 'name', 'branch' and 'version'. Branch
        and version are only conatenated if they have already been set.
        The fullname has to be unique for a given class and a given
        workspace.

        Returns:
            String containing fullname of the resource.

        """

        l = [self._get_name(), self._get_branch(), self._get_version()]
        return '.'.join([str(val) for val in l if val])

    def _get_getter(self) -> list:
        """Get sorted list of keys, which are accepted by the 'get' method.

        The class method 'get' wraps given keys to private getter methods of
        the class instance, which are identified by an initial prefix '_get_'
        in the method name.

        Returns:
            Sorted list of keys, which are accepted by the 'get' method.

        """

        from nemoa.common import nclass, ndict
        d = nclass.methods(self, filter = '_get_*')
        return sorted(ndict.reduce(d, '_get_'))

    def _get_license(self) -> Optional[str]:
        """Get the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            String containing the license reference of the resource.

        """

        return self._config.get('license', None)

    def _get_name(self) -> Optional[str]:
        """Get the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            String containing the name of the resource.

        """

        return self._config.get('name', None)

    def _get_path(self) -> Optional[str]:
        """Get filepath.

        Path to a potential file containing or referencing the resource.

        Returns:
            String containing the (potential) path of the resource.

        """

        if 'path' in self._config:
            path = str(self._config['path'])
            if path: return path

        from nemoa.common import npath
        from nemoa import session

        mname = self.__module__.split('.')[-1]
        dname = session.path(mname + 's')
        if not dname: return None
        fbase = npath.clear(self._get_fullname())
        if not fbase: return None
        fext = session.get('default', 'filetype', mname)
        if not fext: return None
        path = npath.join(dname, fbase + '.' + fext)

        return path

    def _get_setter(self) -> list:
        """Get sorted list of keys, which are accepted by the 'set' method.

        The class method 'set' wraps given keys to private getter methods of
        the class instance, which are identified by an initial prefix '_set_'
        in the method name.

        Returns:
            Sorted list of keys, which are accepted by the 'set' method.

        """

        from nemoa.common import nclass, ndict
        d = nclass.methods(self, filter = '_set_*')
        return sorted(ndict.reduce(d, '_set_'))

    def _get_type(self) -> Optional[str]:
        """Get instance type, using module name and class name.

        String concatenation of module name and class name of the instance.

        Returns:
            String containing instance type identifier.

        """

        mname = self.__module__.split('.')[-1]
        cname = self.__class__.__name__

        return '.'.join([mname, cname])

    def _get_version(self) -> Optional[int]:
        """Get the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Integer value used as the version number of the resource.

        """

        return self._config.get('version', None)

    def set(self, key: str, *args: Any, **kwargs: Any) -> bool:
        """Call private setter methods of the class instance.

        Returns:
            Boolean value which is returned by the respoective private setter
            method of the class instance.

        """

        # set writeable attributes
        if self._attr.get(key, 0b00) & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwargs)

        # supplementary setter methods
        if hasattr(self, '_get_' + key):
            return getattr(self, '_get_' + key)(*args, **kwargs)

        raise KeyError(f"key '{key}' is not valid")

    def _set_copy(self, **kwargs: Any) -> bool:
        """Call setter methods for all keywords.

        Args:
            **kwargs:

        Returns:
            Bool which is True if and only if no error occured.

        """

        for key, val in kwargs.items():
            if not isinstance(key, str): continue
            if not hasattr(self, '_set_' + key): raise AttributeError(
                f"{self.__class__.__name__} instance "
                f"has no method '_set_{key}'")
            getattr(self, '_set_' + key)(val)

        return True

    def _set_about(self, val: str) -> bool:
        """Set short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'about' is required to be of type string")
        self._config['about'] = val
        return True

    def _set_author(self, val: str) -> bool:
        """Set the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'author' is required to be of type string")
        self._config['author'] = val
        return True

    def _set_branch(self, val: str) -> bool:
        """Set the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'branch' is required to be of type string")
        self._config['branch'] = val
        return True

    def _set_copyright(self, val: str) -> bool:
        """Set a copyright notice.

        Notice of statutorily prescribed form that informs users of the
        underlying resource to published copyright ownership.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'copyright' is required to be of type string")
        self._config['copyright'] = val
        return True

    def _set_email(self, val: str) -> bool:
        """Set an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'email' is required to be of type string")
        self._config['email'] = val
        return True

    def _set_license(self, val: str) -> bool:
        """Set a license for the usage of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'livense' is required to be of type string")
        self._config['license'] = val
        return True

    def _set_name(self, val: str) -> bool:
        """Set the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'name' is required to be of type string")
        self._config['name'] = val
        return True

    def _set_path(self, path: PathLike) -> bool:
        """Set filepath.

        Path to a file containing or referencing the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(path, (str, tuple)): raise TypeError(
            "attribute 'path' is required to be of type 'str' "
            f"or 'tuple of str', not '{type(path)}'")

        from nemoa.common import npath
        import pathlib
        self._config['path'] = pathlib.Path(npath.expand(path))
        return True

    def _set_version(self, val: int) -> bool:
        """Set the version number of the branch of the resource.

        Version number of the branch of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, int): raise TypeError(
            "attribute 'version' is required to be of type integer")
        self._config['version'] = val
        return True
