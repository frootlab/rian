# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class Metadata:
    """Base class for classes with metadata.

    Classes like Dataset, Network, System or Model share common
    descriptive metadata like author and license, as well as
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

    _attr_meta = {
        'author': 'rw', 'email': 'rw', 'license': 'rw', 'about': 'rw',
        'fullname': 'r', 'name': 'rw', 'branch': 'rw', 'version': 'rw',
        'type': 'r', 'path': 'rw' }

    def __init__(self, *args, **kwargs):
        """Import object configuration and content from dictionary."""

        self._set_copy(**kwargs)

    def __getattr__(self, key):
        """Attribute wrapper for getter methods."""

        if key in self._attr_meta:
            if 'r' in self._attr_meta[key]: return self._get_meta(key)
            raise AttributeError(f"attribute '{key}' is not readable")
        if key in self._attr:
            if 'r' in self._attr[key]: return self.get(key)
            raise AttributeError(f"attribute '{key}' is not readable")

        raise AttributeError("%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def __setattr__(self, key, val):
        """Attribute wrapper to setter methods."""

        if key in self._attr_meta:
            if 'w' in self._attr_meta[key]:
                return self._set_meta(key, val)
            raise AttributeError(f"attribute '{key}' is not writeable")
        if key in self._attr:
            if 'w' in self._attr[key]: return self.set(key, val)
            raise AttributeError(f"attribute '{key}' is not writeable")

        self.__dict__[key] = val

    def _get_meta(self, key):
        """Get metadata like 'author' or 'version'.

        Returns:
            Value of requested attribute.

        """

        if key == 'about':    return self._get_about()
        if key == 'author':   return self._get_author()
        if key == 'branch':   return self._get_branch()
        if key == 'email':    return self._get_email()
        if key == 'fullname': return self._get_fullname()
        if key == 'license':  return self._get_license()
        if key == 'name':     return self._get_name()
        if key == 'path':     return self._get_path()
        if key == 'type':     return self._get_type()
        if key == 'version':  return self._get_version()

        raise Warning("%s instance has no attribute '%r'."
            % (self.__class__.__name__, key))

    def _get_about(self):
        """Get a short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Basestring containing a description of the resource.

        """

        return self._config.get('about', None)

    def _get_author(self):
        """Get the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Basestring containing the name of the author.

        """

        return self._config.get('author', None)

    def _get_branch(self):
        """Get the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Basestring containing the name of the branch.

        """

        return self._config.get('branch', None)

    def _get_email(self):
        """Get an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Basestring containing an email address of the author.

        """

        return self._config.get('email', None)

    def _get_fullname(self):
        """Get full name including 'branch' and 'version'.

        String concatenation of 'name', 'branch' and 'version'. Branch
        and version are only conatenated if they have allready been set.
        The fallname has to be unique for a given class and a given
        workspace.

        Returns:
            Basestring containing fullname of the resource.

        """

        l = [self._get_name(), self._get_branch(), self._get_version()]
        return '.'.join([str(i) for i in l if i])

    def _get_license(self):
        """Get the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Basestring containing the license reference of the resource.

        """

        return self._config.get('license', None)

    def _get_name(self):
        """Get the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            Basestring containing the name of the resource.

        """

        return self._config.get('name', None)

    def _get_path(self):
        """Get filepath.

        Path to a potential file containing or referencing the resource.

        Returns:
            Basestring containing the (potential) path of the resource.

        """

        return self._config.get('path', self._get_path_default())

    def _get_path_default(self):
        """Get default filepath.

        Path to a potential file containing or referencing the resource.

        Returns:
            Basestring containing the potential path of the resource.

        """

        module = self.__module__.split('.')[1]
        fileext = nemoa.get('default', 'filetype', module)
        path = nemoa.path(module + 's') or nemoa.common.ospath.getcwd()
        filename = '%s.%s' % (nemoa.common.ospath.get_clean_filename(
            self._get_fullname()), fileext)

        return nemoa.common.ospath.get_norm_path(path, filename)

    def _get_type(self):
        """Get instance type, using module name and class name.

        String concatenation of module name and class name of the
        instance.

        Returns:
            Basestring containing instance type identifier.

        """

        mname = self.__module__.split('.')[-1]
        cname = self.__class__.__name__

        return mname + '.' + cname

    def _get_version(self):
        """Get the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Integer value used as the version number of the resource.

        """

        return self._config.get('version', None)

    def _set_meta(self, key, *args, **kwargs):
        """Set meta information like 'author' or 'version'.

        Returns:
            Boolean value which is True on success, else False.

        """

        if key == 'about':   return self._set_about(*args, **kwargs)
        if key == 'author':  return self._set_author(*args, **kwargs)
        if key == 'branch':  return self._set_branch(*args, **kwargs)
        if key == 'email':   return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)
        if key == 'name':    return self._set_name(*args, **kwargs)
        if key == 'path':    return self._set_path(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)

        raise Warning("%s instance has no attribute '%r'."
            % (self.__class__.__name__, key))

    def _set_about(self, val):
        """Set short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'about' is required to be of type string")
        self._config['about'] = val
        return True

    def _set_author(self, val):
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

    def _set_branch(self, val):
        """Set the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'branch' is required to be of type string")
        self._config['branch'] = val
        return True

    def _set_email(self, val):
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

    def _set_license(self, val):
        """Set the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'livense' is required to be of type string")
        self._config['license'] = val
        return True

    def _set_name(self, val):
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

    def _set_path(self, val):
        """Set filepath.

        Path to a file containing or referencing the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, str): raise TypeError(
            "attribute 'path' is required to be of type string")
        self._config['path'] = val
        return True

    def _set_version(self, val):
        """Set the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, int): raise TypeError(
            "attribute 'version' is required to be of type integer")
        self._config['version'] = val
        return True
