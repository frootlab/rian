#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Setuptools based installation."""

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import os
import pathlib
import re
import sys
import subprocess
import setuptools
from setuptools.command.install import install as Installer

class CustomInstaller(Installer): # type: ignore
    """Customized setuptools install command."""

    def run(self) -> None:
        Installer.run(self)
        subprocess.call([sys.executable, __file__, 'postinstall'])

def install() -> None:
    """Setuptools based installation script."""

    # Parse top level module for attributes
    text = pathlib.Path('./nemoa/__init__.py').read_text()
    pattern = r"^[ ]*__([^\d\W]\w*)__[ ]*=[ ]*['\"]([^'\"]*)['\"]"
    matches = re.finditer(pattern, text, re.M)
    pkg = {str(m.group(1)): str(m.group(2)) for m in matches}

    # Install package
    setuptools.setup(
        name='nemoa',
        version=pkg['version'],
        description=pkg['description'],
        long_description=pathlib.Path('.', 'README.md').read_text(),
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
    		'Programming Language :: Python :: 3.7',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Database :: Database Engines/Servers',
            'Topic :: Software Development :: Libraries :: Python Modules'],
        keywords=(
            "data-analysis "
            "enterprise-data-analysis "
            "data-science "
            "collaborative-data-science "
            "data-visualization "
            "machine-learning "
            "artificial-intelligence "
            "deep-learning "
            "probabilistic-graphical-model "),
        url=pkg['url'],
        author=pkg['author'],
        author_email=pkg['email'],
        license=pkg['license'],
        packages=setuptools.find_packages(),
        package_dir={
            'nemoa': 'nemoa'},
        package_data={
            'nemoa': ['data/*.zip']},
        cmdclass={
            'install': CustomInstaller},
        python_requires='>=3.7',
        install_requires=[
            'ipython>=7.1',
            'matplotlib>=3.0',
            'networkx>=2.1',
            'numpy>=1.15',
            'flib>=0.9.2',
            'pandb>=0.1.10'],
        extras_require={
            'gui': ['pyside'],
            'gene': ['rpy2']},
        entry_points={
            'console_scripts': [
                'nemoa = nemoa.core.cli:main']},
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
    user_src_base = str(pathlib.Path('.', 'data', 'user'))
    user_tgt_base = appdirs.user_data_dir(
        appname='nemoa', appauthor='frootlab')
    user_tgt_base = str(pathlib.Path(user_tgt_base, 'workspaces'))
    copytree(user_src_base, user_tgt_base)

    # copy site workspaces
    site_src_base = str(pathlib.Path('.', 'data', 'site'))
    site_tgt_base = appdirs.site_data_dir(
        appname='nemoa', appauthor='frootlab')
    site_tgt_base = str(pathlib.Path(site_tgt_base, 'workspaces'))
    copytree(site_src_base, site_tgt_base)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'postinstall':
        post_install()
    else:
        install()
