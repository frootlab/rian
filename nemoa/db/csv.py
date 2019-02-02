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
"""Table Proxy for textfiles containing delimiter-separated values."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import attrib
from nemoa.db import table
from nemoa.io import csv, ini
from nemoa.types import Any, FileRef
from nemoa.errors import ConnectError, DisconnectError

#
# CSV Table Proxy Class
#

class Table(table.Proxy):
    """CSV-Table Proxy."""

    #
    # Public Attributes
    #

    # Remove setter from name, since the name is determined by the file name
    name: property = attrib.Virtual('_get_name')
    name.__doc__ = "Name of the table."

    #
    # Protected Attributes
    #

    _fileref: property = attrib.Temporary(dtype=csv.FileRefClasses)
    _file: property = attrib.Temporary(dtype=csv.File)

    #
    # Special Methods
    #

    def __init__(self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Initialize CSV-Table Proxy.

        Args:
            file:
            *args: Additional arguments, that are passed to
                :class:`csv.File <nemoa.io.csv.File>`.
            **kwds: Additional keyword arguments, that are passed to csv.File.

        """
        super().__init__() # Initialize table proxy
        self.connect(file, *args, **kwds) # Connect CSV File
        self._post_init() # Run post init hook

    #
    # Public Methods
    #

    def connect( # type: ignore
            self, file: FileRef, *args: Any, **kwds: Any) -> None:
        """Connect to given file reference."""
        if self._connected:
            raise ConnectError("the connection already has been established")

        # Create and reference CSV file
        fh = csv.File(file, *args, **kwds)
        self._file = fh

        # Get table name, structure and and metadata from CSV file
        name = fh.name.split('.', 1)[0]
        fields = fh.fields
        metadata = ini.decode(fh.comment, flat=True, autocast=True)

        # Create table
        self.create(name, fields, metadata=metadata)
        self._connected = True

    def disconnect(self) -> None:
        """Close connection to referenced file."""
        if not self._connected:
            raise DisconnectError("the proxy has not yet been connected")
        self._file.close()
        self._connected = False

    def pull(self) -> None:
        """Pull all rows from CSV-File."""
        comment = self._file.comment
        mapping = ini.decode(comment, flat=True, autocast=True)
        self._metadata.update(mapping)
        name = self._file.name.split('.', 1)[0] # Get name from filename
        self._set_name(name)
        rows = self._file.read()
        self.insert(rows)

    def push(self) -> None:
        """Push all rows to CSV-File."""
        comment = ini.encode(self.metadata, flat=True)
        self._file.comment = comment
        rows = self.select()
        self._file.write(rows)
