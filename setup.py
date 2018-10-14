#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setuptools based installation."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import os
import re
import sys

from pathlib import Path

import setuptools
from setuptools.command.install import install as Installer

appname = 'nemoa'
appauthor = 'frootlab'
libdir = 'lib'

class CustomInstaller(Installer): # type: ignore
    """Customized setuptools install command."""

    def run(self) -> None:
        """Run installer."""
        Installer.run(self)
        # Run post installation script
        import subprocess
        subprocess.call([sys.executable, __file__, 'postinstall'])

def get_vars() -> dict:
    """Get __VAR__ module variables from package __init__ file."""
    text = Path(libdir, appname, '__init__.py').read_text()

    # Parse variables with regular expressions
    rekey = "__([a-zA-Z][a-zA-Z0-9_]*)__"
    reval = r"['\"]([^'\"]*)['\"]"
    regex = f"^[ ]*{rekey}[ ]*=[ ]*{reval}"
    dvars = {}
    for match in re.finditer(regex, text, re.M):
        key = str(match.group(1))
        val = str(match.group(2))
        dvars[key] = val
    return dvars

def install() -> None:
    """Setuptools based installation script."""
    # Update package variables from package init
    pkgvars = get_vars()

    # Install nemoa lib
    setuptools.setup(
        name=appname,
        version=pkgvars['version'],
        description=pkgvars['description'],
        long_description=Path('.', 'README.md').read_text(),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GPLv3',
            'Programming Language :: Python :: 3',
    		'Programming Language :: Python :: 3.6'],
        keywords=(
            "data-analysis "
            "data-science "
            "data-visualization "
            "machine-learning "
            "deep-learning "
            "probabilistic-graphical-models "),
        url=pkgvars['url'],
        author=pkgvars['author'],
        author_email=pkgvars['email'],
        license=pkgvars['license'],
        packages=setuptools.find_packages(libdir),
        package_dir={
            '': libdir},
        package_data={
            'nemoa': ['data/*.zip']},
        cmdclass={
            'install': CustomInstaller},
        python_requires='>=3.6',
        install_requires=[
            'appdirs>=1.4',
            'matplotlib>=3.0',
            'networkx>=2.1',
            'numpy>=1.15'],
        extras_require={
            'gui': ['pyside'],
            'gene': ['rpy2']},
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

    # copy user workspaces
    user_src_base = str(Path('.', 'data', 'user'))
    user_tgt_base = appdirs.user_data_dir(appname=appname, appauthor=appauthor)
    user_tgt_base = str(Path(user_tgt_base, 'workspaces'))
    copytree(user_src_base, user_tgt_base)

    # copy site workspaces
    site_src_base = str(Path('.', 'data', 'site'))
    site_tgt_base = appdirs.site_data_dir(appname=appname, appauthor=appauthor)
    site_tgt_base = str(Path(site_tgt_base, 'workspaces'))
    copytree(site_src_base, site_tgt_base)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'postinstall':
        post_install()
    else:
        install()
