# -*- coding: utf-8 -*-
"""Layered networks."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from nemoa.network.classes import base

class MultiLayer(base.Network):
    """Network with multi layer layout."""
    pass

class Shallow(base.Network):
    """Network with shallow layout."""
    pass

class Factor(base.Network):
    """Network with factor graph layout."""
    pass
