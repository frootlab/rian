# -*- coding: utf-8 -*-
"""Table Proxy for textfiles containing delimiter-separated values."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import attrib
from nemoa.db import table
from nemoa.io import csv, ini
from nemoa.types import Any, FileRef, FileRefClasses
from nemoa.errors import ConnectError, DisconnectError

#
# CSV Table Proxy Class
#

class Table(table.ProxyBase):
    """CSV-Table Proxy."""

    _fileref: property = attrib.Temporary(classinfo=FileRefClasses)
    _file: property = attrib.Temporary(classinfo=csv.File)

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

        # Get metadata from CSV file
        metadata = ini.decode(fh.comment, flat=True, autocast=True)

        # Create table
        self.create(fh.name, fh.fields, metadata=metadata)
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
        self.name = self._file.name
        rows = self._file.read()
        self.insert(rows)

    def push(self) -> None:
        """Push all rows to CSV-File."""
        # TODO: Also push metadata to file
        comment = ini.encode(self.metadata, flat=True)
        self._file.comment = comment
        rows = self.select()
        self._file.write(rows)
