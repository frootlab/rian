# -*- coding: utf-8 -*-
"""Proxy Classes and constructors for Data Integration."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
from nemoa.base import attrib
from nemoa.data import table
from nemoa.errors import NemoaError
from nemoa.types import Any

#
# Constants
#

PROXY_FLAG_CACHE = 0b0001
PROXY_FLAG_INCREMENTAL = 0b0010

#
# Exceptions
#

class ProxyError(NemoaError):
    """Base Exception for Proxy Errors."""

class PushError(ProxyError):
    """Raises when a push-request could not be finished."""

class PullError(ProxyError):
    """Raises when a pull-request could not be finished."""

#
# Classes
#

class Table(table.Table, ABC):
    """Table Proxy Base Class."""

    _proxy_mode: property = attrib.MetaData(classinfo=int, default=1)

    def __init__(self, *args: Any, proxy_mode: int = 0, **kwds: Any) -> None:
        """Initialize Table Proxy.

        Args:
            proxy_mode:
            *args:
            **kwds:

        """
        super().__init__(*args, **kwds)
        self._proxy_mode = proxy_mode
        if proxy_mode & PROXY_FLAG_CACHE:
            self.pull()

    def commit(self) -> None:
        """Push changes to source table and apply changes to local table."""
        # For incremental updates of the source, the push request requires, that
        # changes have not yet been applied to the local table
        if self._proxy_mode & PROXY_FLAG_INCREMENTAL:
            self.push()
            super().commit()
            return
        # For full updates of the source, the push request requires, that all
        # changes have been applied to the local table
        super().commit()
        self.push()

    @abstractmethod
    def pull(self) -> None:
        """Pull rows from source table."""
        raise NotImplementedError()

    @abstractmethod
    def push(self) -> None:
        """Push changes to source table."""
        raise NotImplementedError()
