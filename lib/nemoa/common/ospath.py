# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def basename(path):
    """Get basename of file.

    Args:
        path (string): path to file

    Returns:
        String containing basename of file.

    """

    import os

    filename = os.path.basename(get_norm_path(path))
    filebasename = os.path.splitext(filename)[0].rstrip('.')

    return filebasename

def copytree(src, tgt):

    import glob
    import os
    import shutil

    for srcsdir in glob.glob(os.path.join(src, '*')):
        tgtsdir = os.path.join(tgt, basename(srcsdir))

        if os.path.exists(tgtsdir):
            shutil.rmtree(tgtsdir)

        try:
            shutil.copytree(srcsdir, tgtsdir)

        # directories are the same
        except shutil.Error as e:
            print('Directory not copied. Error: %s' % e)

        # any error saying that the directory doesn't exist
        except OSError as e:
            print('Directory not copied. Error: %s' % e)

    return True


def directory(path):
    """Get directory path of file or directory.

    Args:
        path (string): path to file

    Returns:
        String containing normalized directory path of file.

    """

    import os

    return os.path.dirname(get_norm_path(path))

def fileext(path):
    """Get extension of file.

    Args:
        path (string): path to file

    Returns:
        String containing extension of file.

    """

    import os

    filename = os.path.basename(get_norm_path(path))
    ext = os.path.splitext(filename)[1].lstrip('.')

    return ext

def getcwd():
    """Get path of current working directory.

    Returns:
        String containing path of current working directory.

    """

    import os

    return os.getcwd() + os.path.sep

def gethome():
    """Get path to current users home directory.

    Returns:
        String containing path of home directory.

    """

    import os

    return os.path.expanduser('~')

def getstorage(name, *args, **kwargs):
    """Get paths to storage directories.

    This function maps generic names of storage directory to platform
    specific paths which allows platform independent usage of storage
    directories. This is a wrapper function to the module 'appdirs'.
    For details and usage see:

        http://github.com/ActiveState/appdirs

    Args:
        name (string): Storage path name: String describing storage
            directory. Allowed values are:

            'user_cache_dir' -- User specific application cache
            'user_config_dir' -- User specific application configuration
            'user_data_dir' -- User specific application data
            'user_log_dir' -- User specific application logging
            'site_config_dir' -- Shared application configuration
            'site_data_dir' -- Shared application configuration

        *args: Arguments passed to appdirs
        **kwargs: Keyword Arguments passed to appdirs

    Returns:
        String containing path of storage directory or False if
        storage path name is not supported.

    """

    import appdirs

    if name == 'user_cache_dir':
        return appdirs.user_cache_dir(*args, **kwargs)
    elif name == 'user_config_dir':
        return appdirs.user_config_dir(*args, **kwargs)
    elif name == 'user_data_dir':
        return appdirs.user_data_dir(*args, **kwargs)
    elif name == 'user_log_dir':
        return appdirs.user_log_dir(*args, **kwargs)
    elif name == 'user_cwd':
        return getcwd()
    elif name == 'site_config_dir':
        return appdirs.site_config_dir(*args, **kwargs)
    elif name == 'site_data_dir':
        return appdirs.site_data_dir(*args, **kwargs)

    return False

def joinpath(directory, name, extension):
    """Get path of file.

    Args:
        directory (string): file directory
        name (string): file basename
        extension (string): file extension

    Returns:
        String containing path of file.

    """

    import os

    path = '%s%s%s.%s' % (directory, os.sep, name, extension)
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)

    return path

def get_valid_filename_encode(arg):
    
    import base64
    
    return base64.urlsafe_b64encode(arg)

def get_valid_filename_decode(string):

    import base64
    
    return base64.urlsafe_b64decode(string)

def get_clean_filename(text):
    
    import string
    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(char for char in text if char in valid_chars)
    filename = filename.replace(' ', '_')

    return filename

def get_valid_path(*args):
    """Get valid path.

    Args:
        args (tuplee): tree of tuples, lists and basestrings describing
            path to file or directory

    Returns:
        String containing valid path.

    """

    import os

    # flatten tuple of tuples etc. to flat path list
    # and join list using os path seperators
    path = args
    if isinstance(path, (list, tuple)):
        path = list(path)
        char = 0
        while char < len(path):
            while isinstance(path[char], (list, tuple)):
                if not path[char]:
                    path.pop(char)
                    char -= 1
                    break
                else:
                    path[char:char + 1] = path[char]
            char += 1
        try:
            path = os.path.sep.join(list(path))
        except UnicodeDecodeError:
            return None

    return path

def get_norm_path(*args):
    """Get normalized path.

    Args:
        args:

    Returns:
        String containing normalized path.

    """

    import os

    path = get_valid_path(*args)
    if not path: return None
    
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)

    return path
