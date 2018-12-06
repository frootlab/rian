# -*- coding: utf-8 -*-
"""Abstract base classes for frequently used patterns."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import abc

class Proxy(metaclass=abc.ABCMeta):
    """Abstract Base Class for Proxies."""

    @abc.abstractmethod
    def pull(self) -> None:
        """Pull state changes from source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def push(self) -> None:
        """Push state changes to source."""
        raise NotImplementedError()
