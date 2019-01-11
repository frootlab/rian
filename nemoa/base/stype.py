# -*- coding: utf-8 -*-
"""Structured types."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import NamedTuple, Hashable, Tuple, Union, Optional
from nemoa.errors import InvalidTypeError
from nemoa.types import OptType, NoneType

FieldID = Hashable # <field>
Frame = Tuple[FieldID, ...] # <fields>
DomLike = Union[OptType, Tuple[OptType, Frame], 'Domain']

#
# Parameter Classes
#

class Domain(NamedTuple):
    """Class for the storage of domain definitions."""
    type: type
    frame: Frame

#
# Constructors
#

def create_domain(
    domain: DomLike = None, default_type: type = NoneType,
    default_frame: Optional[Frame] = None) -> Domain:
    """Create a Domain object.

    Args:
        domain: Optional :term:`domain like` parameter, that specifies the type
            and (if required) the frame of a domain.
        default_type: Optional parameter, that specifies the default domain type
            which is used if no type is given within the argument `domain`. If
            provided, the argument has to be given as a :class:`type`.
        default_frame: Optional parameter, that specifies the default domain
            frame which is used if no frame is given within the argument
            `domain`. If provided, the argument has to be given as a
            :class:`tuple`.

    """

    # Get domain definition parameters
    if domain is None:
        dom_type = default_type
        dom_frame = default_frame or tuple()
    elif isinstance(domain, Domain):
        dom_type = domain.type
        dom_frame = domain.frame
    elif isinstance(domain, type):
        dom_type = domain
        dom_frame = default_frame or tuple()
    elif isinstance(domain, tuple):
        dom_type = domain[0] or default_type
        dom_frame = domain[1] or default_frame or tuple()
    else:
        allowed = (NoneType, type, tuple, Domain)
        raise InvalidTypeError('domain', domain, allowed)

    # Verify parameters
    if len(set(dom_frame)) < len(dom_frame):
        raise ValueError() # TODO

    return Domain(dom_type, dom_frame)
