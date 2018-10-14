#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setuptools based installation."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import codecs
import io
import os
import re
import sys

from typing import Union

import setuptools
from setuptools.command.install import install as Installer

# Module variables
pkgname = 'nemoa'
libdir = 'lib'

# Module classes
class CustomInstaller(Installer): # type: ignore
    """Customized setuptools install command."""

    def run(self) -> None:
        """Run installer."""
        Installer.run(self)

        # Run post installation script
        import subprocess
        subprocess.call([sys.executable, __file__, 'postinstall'])

# Module functions
def get_path(filepath: Union[str, list, tuple]) -> str:
    """Get absolute filepath from string or iterable."""
    here = os.path.abspath(os.path.dirname(__file__))
    if not filepath:
        return here
    if isinstance(filepath, str):
        return os.path.join(here, filepath)
    if isinstance(filepath, (tuple, list)):
        return os.path.join(here, os.path.sep.join(filepath))
    raise RuntimeError(f"Invalid filepath {str(filepath)}")

def get_vars(filepath: Union[str, list, tuple]) -> dict:
    """Get all __VARIABLE__ from given file."""
    # Get file content
    path = get_path(filepath)
    with io.open(path, encoding='utf8') as file_handler:
        content = file_handler.read()

    # Parse variables with regular expressions
    key_regex = """__([a-zA-Z][a-zA-Z0-9]*)__"""
    val_regex = """['\"]([^'\"]*)['\"]"""
    regex = r"^[ ]*%s[ ]*=[ ]*%s" % (key_regex, val_regex)
    dvars = {}
    for match in re.finditer(regex, content, re.M):
        key = str(match.group(1))
        val = str(match.group(2))
        dvars[key] = val
    return dvars

def read_text(filepath: Union[str, list, tuple]) -> str:
    """Read the content from a textfile."""
    path = get_path(filepath)
    with codecs.open(path, encoding='utf-8') as file:
        text = file.read()
    return text

def install() -> None:
    """Setuptools based installation script."""
    # Update package variables from package init
    srcfile = (libdir, pkgname, '__init__.py')
    pkg_vars = get_vars(srcfile)

    # Install nemoa lib
    setuptools.setup(
        version=pkg_vars['version'],
        description=pkg_vars['description'],
        url=pkg_vars['url'],
        author=pkg_vars['author'],
        author_email=pkg_vars['email'],
        license=pkg_vars['license'],
        packages=setuptools.find_packages(libdir),
        package_dir={'': libdir},
        long_description=read_text('README.md'),
        cmdclass={'install': CustomInstaller},
        package_data={
            'nemoa': ['data/*.zip']},
        keywords='data-analysis deeplearning ann rbm dbn dbm',
        python_requires='>=3.6',
        install_requires=[
            'appdirs>=1.4',
            'matplotlib>=3.0',
            'networkx>=2.1',
            'numpy>=1.15'],
        extras_require={
            'gui': ['pyside'],
            'gene': ['rpy2']},
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GPLv3',
            'Programming Language :: Python :: 3',
    		'Programming Language :: Python :: 3.6'],
        entry_points={
            'console_scripts': [
                'nemoa = nemoa.session.console:main']},
        zip_safe=False)

def post_install() -> None:
    """Post installation script."""
    import appdirs

    def copytree(src: str, tgt: str) -> None:
        import glob
        import shutil

        print(f"copying {src} -> {tgt}")

        for srcsdir in glob.glob(os.path.join(src, '*')):
            tgtsdir = os.path.join(tgt, os.path.basename(srcsdir))

            if os.path.exists(tgtsdir):
                shutil.rmtree(tgtsdir)

            try:
                shutil.copytree(srcsdir, tgtsdir)
            except shutil.Error as err: # unknown error
                print(f"directory not copied: {str(err)}")
            except OSError as err: # directory doesn't exist
                print(f"directory not copied: {str(err)}")

    print('running postinstall')

    appname = 'nemoa'
    appauthor = 'frootlab'

    # copy user workspaces
    user_src_base = get_path(('data', 'user'))
    user_tgt_base = appdirs.user_data_dir(appname=appname, appauthor=appauthor)
    user_tgt_base = get_path((user_tgt_base, 'workspaces'))
    copytree(user_src_base, user_tgt_base)

    # copy site workspaces
    site_src_base = get_path(('data', 'site'))
    site_tgt_base = appdirs.site_data_dir(appname=appname, appauthor=appauthor)
    site_tgt_base = get_path((site_tgt_base, 'workspaces'))
    copytree(site_src_base, site_tgt_base)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'postinstall':
        post_install()
    else:
        install()
