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

    filename = os.path.basename(path)
    filebasename = os.path.splitext(filename)[0].rstrip('.')

    return filebasename



def cwd():
    """Get path of current working directory.

    Returns:
        String containing path of current working directory.

    """
    
    import os
    
    return os.getcwd() + os.sep

def directory(path):
    """Get directory path of file.

    Args:
        path (string): path to file

    Returns:
        String containing normalized directory path of file.

    """

    import os

    if isinstance(path, (tuple, list)):
        path = os.path.sep.join(path)

    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)

    return os.path.dirname(path)

def fileext(path):
    """Get extension of file.

    Args:
        path (string): path to file

    Returns:
        String containing extension of file.

    """

    import os

    filename = os.path.basename(path)
    file_ext = os.path.splitext(filename)[1].lstrip('.')

    return file_ext

def home():
    """Get path to current users home directory.
    
    Returns:
        String containing path of home directory.
    
    """
    
    import os
    
    return os.path.expanduser('~')

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
    path = os.path.abspath(path)
    path = os.path.normpath(path)

    return path

def special(name):
    """Get paths to special directories.
    
    Args:
        name (string):

    Returns:
        String containing path of special directory or dictionary
        containing all platform specific special directories that
        are implemented.

    """

    def _special_folders_linux(name):
        
        return True

    def _special_folders_windows(name):
        """
        
        Args:
            name (string):
        
        """

        try:
            import winshell
        except:
            return False

        if name in ['Application Data', 'userdata']:
            return winshell.application_data()
        elif name == 'Bookmarks':
            return winshell.bookmarks()
        elif name in ['Common Application Data', 'shareddata']:
            return winshell.application_data(True)
        elif name == 'Common Bookmarks':
            return winshell.bookmarks(True)
        elif name == 'Common Desktop':
            return winshell.desktop(True)
        elif name == 'Common Programs':
            return winshell.programs(True)
        elif name == 'Common Start Menu':
            return winshell.start_menu(True)
        elif name == 'Common Startup':
            return winshell.startup(True)
        elif name == 'Desktop':
            return winshell.desktop()
        elif name == 'My Documents':
            return winshell.my_documents()
        elif name == 'Programs':
            return winshell.programs()
        elif name == 'Recent':
            return winshell.recent()
        elif name == 'SendTo':
            return winshell.sendto()
        elif name == 'Start Menu':
            return winshell.start_menu()
        elif name == 'Startup':
            return winshell.startup()

        return False
    
    import platform
    ostype = platform.system().lower()

    if ostype == 'linux': return _special_folders_linux(name)
    if ostype == 'windows': return _special_folders_windows(name)

    return False

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
