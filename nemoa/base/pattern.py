# -*- coding: utf-8 -*-
"""Abstract base classes for frequently used patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import abc
import contextlib
from nemoa.types import Any
from nemoa.errors import DisconnectError

class Proxy(metaclass=abc.ABCMeta):
    """Abstract Base Class for Proxies."""

    _connected: bool

    def __init__(self) -> None:
        """Initialize proxy instance."""
        self._connected = False

    def __del__(self) -> None:
        """Run destructor for instance."""
        with contextlib.suppress(DisconnectError):
            self.disconnect()

    @abc.abstractmethod
    def pull(self) -> None:
        """Pull state changes from source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def push(self) -> None:
        """Push state changes to source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def connect(self, *args: Any, **kwds: Any) -> None:
        """Establish connection to source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Close connection to source."""
        raise NotImplementedError()
