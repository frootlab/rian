# -*- coding: utf-8 -*-
"""Table Proxy for Microsoft Excel Office Open XML Files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import openpyxl
except ImportError as err:
    raise ImportError(
        "requires package openpyxl: "
        "https://pypi.org/project/openpyxl") from err

from nemoa.base import attrib
from nemoa.db import TableProxyBase

#
# Classes
#

class TableProxy(TableProxyBase):
    """Excel-Table Proxy."""

    _file: property = attrib.Temporary()
