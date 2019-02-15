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
"""Workspaces."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import datetime
from pathlib import Path
from typing import ClassVar, Optional
from flab.base import attrib, env
from nemoa.core import dcmeta
from flab.errors import FileFormatError
from flab.io import ini, zip as archive
from flab.base.types import StrList, PathLike, OptBytes, OptPathLike

class Workspace(archive.File, attrib.Group):
    """Workspaces.

    Workspaces are in-memory Zip-Archives with a given archive directory
    structure and a workspace configuration file 'workspace.ini' in the archives
    root.

    Args:
        filepath: String or :term:`path-like object`, that points to a valid
            ZipFile or None. If the filepath points to a valid ZipFile,
            then the class instance is initialized with a memory copy of
            the file. If the given file, however, does not exist, isn't a valid
            ZipFile, or does not contain a workspace configuration, respectively
            one of the errors FileNotFoundError, BadZipFile or FileFormatError
            is raised. The default behaviour, if the filepath is None, is to
            create an empty workspace in the memory, that uses the default
            folders layout. In this case the attribute maintainer is initialized
            with the current username.
        pwd: Bytes representing password of workspace file.

    """

    #
    # Protected Class Variables
    #

    _config_file: ClassVar[Path] = Path('workspace.ini')
    _default_config: ClassVar[ini.ConfigDict] = {
        'dc': {
            'creator': env.get_username(),
            'date': datetime.datetime.now()}}
    _default_dir_layout: ClassVar[StrList] = [
        'dataset', 'network', 'system', 'model', 'script']

    #
    # Public Attributes and Attribute Groups
    #

    dc: attrib.Group = dcmeta.Group()

    startup: property = attrib.MetaData(dtype=Path, category='hooks')
    startup.__doc__ = """
    The startup script is a path, that points to a python script inside the
    workspace, which is executed after loading the workspace.
    """

    def __init__(
            self, filepath: OptPathLike = None, pwd: OptBytes = None,
            parent: Optional[attrib.Group] = None) -> None:

        # Initialize in-memory ZipFile
        archive.File.__init__(self, filepath=filepath, pwd=pwd)

        # Initialize Attribute Group
        attrib.Group.__init__(self, parent=parent)

    def load(self, filepath: PathLike, pwd: OptBytes = None) -> None:
        """Load Workspace from file.

        Args:
            filepath: String or :term:`path-like object`, that points to a valid
                workspace file. If the filepath points to a valid workspace
                file, then the class instance is initialized with a memory copy
                of the file. If the given file, however, does not exist, isn't a
                valid ZipFile, or does not contain a workspace configuration,
                respectively one of the errors FileNotFoundError, BadZipFile or
                FileFormatError is raised.
            pwd: Bytes representing password of workspace file.

        """
        super().load(filepath, pwd=pwd)

        # Try to open and load workspace configuration from buffer
        scheme = {
            'dc': self._get_attr_types(group='dc'),
            'hooks': self._get_attr_types(category='hooks')}
        try:
            with self.open(self._config_file) as file:
                cfg = ini.load(file, scheme=scheme)
        except KeyError as err:
            if isinstance(self._path, Path):
                raise FileFormatError(self._path, 'nemoa workspace') from err
            raise

        # Link configuration
        self._set_attr_values(cfg.get('dc', {}), group='dc') # type: ignore


    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file.

        Args:
            filepath: String or :term:`path-like object`, that represents the
                name of a workspace file.

        """
        path = env.expand(filepath)

        # Update datetime
        self.date = datetime.datetime.now()

        # Update 'workspace.ini'
        with self.open(self._config_file, mode='w') as file:
            ini.save({
                'dc': self._get_attr_values(group='dc'),
                'hooks': self._get_attr_values(category='hooks')}, file)

        super().saveas(filepath)

    def _create_new(self) -> None:
        super()._create_new()

        # Create folders
        self._set_attr_values(self._default_config['dc'], group='dc')
        for folder in self._default_dir_layout:
            self.mkdir(folder)
