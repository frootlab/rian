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

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import nemoa.system.classes.base
import importlib

def new(*args, **kwds):
    """Return system instance."""

    if not kwds: kwds = {'config': {'type': 'base.System'}}

    if len(kwds.get('config', {}).get('type', '').split('.')) != 2:
        raise ValueError("configuration is not valid")

    stype = kwds['config']['type']
    mname = 'nemoa.system.classes.' + stype.split('.', 1)[0]
    cname = stype.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
        system = getattr(module, cname)(**kwds)
    except ImportError:
        raise ValueError("""could not create system:
            unknown system type '%s'.""" % stype) or None

    return system
