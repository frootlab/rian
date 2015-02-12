# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class ClassesBaseClass:
    """Base Class for content specific classes.

    Content specific classes like Dataset, Network, System or Model
    share common properties like metadata about author and license.
    This Base Class is intended to provide a common interface and
    implementation of those common properties.

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
        'fullname': 'r', 'type': 'r', 'about': 'rw',
        'name': 'rw', 'branch': 'rw', 'version': 'rw',
        'author': 'rw', 'email': 'rw', 'license': 'rw',
        'path': 'rw'}

    def __init__(self, *args, **kwargs):
        """Import object configuration and content from dictionary."""
        self._set_copy(**kwargs)

    def __getattr__(self, key):
        """Attribute wrapper to getter methods."""

        if key in self._attr_meta:
            if 'r' in self._attr_meta[key]: return self._get_meta(key)
            return nemoa.log('warning',
                "attribute '%s' is not readable." % (key))
        if key in self._attr:
            if 'r' in self._attr[key]: return self.get(key)
            return nemoa.log('warning',
                "attribute '%s' is not readable." % (key))

        raise AttributeError("%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def __setattr__(self, key, val):
        """Attribute wrapper to setter methods."""

        if key in self._attr_meta:
            if 'w' in self._attr_meta[key]:
                return self._set_meta(key, val)
            return nemoa.log('warning',
                "attribute '%s' is not writeable." % (key))
        if key in self._attr:
            if 'w' in self._attr[key]: return self.set(key, val)
            return nemoa.log('warning',
                "attribute '%s' is not writeable." % (key))

        self.__dict__[key] = val

    def _get_meta(self, key):
        """Get meta information like 'author' or 'version'."""

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

        return nemoa.log('warning', "%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def _get_about(self):
        """Get a short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Basestring containing a description of the resource.

        """

        if 'about' in self._config: return self._config['about']
        return None

    def _get_author(self):
        """Get the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Basestring containing the name of the author.

        """

        if 'author' in self._config: return self._config['author']
        return None

    def _get_branch(self):
        """Get the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Basestring containing the name of the branch.

        """

        if 'branch' in self._config: return self._config['branch']
        return None

    def _get_email(self):
        """Get an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Basestring containing an email address of the author.

        """

        if 'email' in self._config: return self._config['email']
        return None

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
        return '.'.join([str(item) for item in l if item])

    def _get_license(self):
        """Get the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Basestring containing the license reference of the resource.

        """

        if 'license' in self._config: return self._config['license']
        return None

    def _get_name(self):
        """Get the name of the resource.

        The name has to be unique for a given class and a given
        workspace in the sence, that all resources with the same name
        have to be branches or other versions of the same resource.

        Returns:
            Basestring containing the name of the resource.

        """

        if 'name' in self._config: return self._config['name']
        return None

    def _get_path(self):
        """Get filepath.

        Path to a file containing or referencing the resource.

        Returns:
            Basestring containg the path of the resource.

        """

        if 'path' in self._config: return self._config['path']
        return None

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

        if 'version' in self._config: return self._config['version']
        return None

    def _set_meta(self, key, *args, **kwargs):
        """Set meta information like 'author' or 'version'."""

        if key == 'about':   return self._set_about(*args, **kwargs)
        if key == 'author':  return self._set_author(*args, **kwargs)
        if key == 'branch':  return self._set_branch(*args, **kwargs)
        if key == 'email':   return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)
        if key == 'name':    return self._set_name(*args, **kwargs)
        if key == 'path':    return self._set_path(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)

        return nemoa.log('warning', "%s instance has no attribute '%r'"
            % (self.__class__.__name__, key))

    def _set_about(self, val):
        """Set short description of the content of the resource.

        Short description of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'about' requires datatype 'basestring'.")
        self._config['about'] = val
        return True

    def _set_author(self, val):
        """Set the name of the author of the resource.

        A person, an organization, or a service that is responsible for
        the creation of the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'author' requires datatype 'basestring'.")
        self._config['author'] = val
        return True

    def _set_branch(self, val):
        """Set the name of the current branch.

        Name of a duplicate of the original resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'branch' requires datatype 'basestring'.")
        self._config['branch'] = val
        return True

    def _set_email(self, val):
        """Set an email address of the author.

        Email address to a person, an organization, or a service that is
        responsible for the content of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'email' requires datatype 'basestring'.")
        self._config['email'] = val
        return True

    def _set_license(self, val):
        """Set the license of the resource.

        Namereference to a legal document giving specified users an
        official permission to do something with the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'license' requires datatype 'basestring'.")
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

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'name' requires datatype 'basestring'.")
        self._config['name'] = val
        return True

    def _set_path(self, val):
        """Set filepath.

        Path to a file containing or referencing the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, basestring): return nemoa.log('warning',
            "attribute 'path' requires datatype 'basestring'.")
        self._config['path'] = val
        return True

    def _set_version(self, val):
        """Set the version number of the branch of the resource.

        Versionnumber of branch of the resource.

        Returns:
            Boolean value which is True on success, else False.

        """

        if not isinstance(val, int): return nemoa.log('warning',
            "attribute 'version' requires datatype 'int'.")
        self._config['version'] = val
        return True
