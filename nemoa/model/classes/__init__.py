# -*- coding: utf-8 -*-
# Copyright (C) 2019 Frootlab Developers
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://github.com/frootlab/nemoa
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

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.classes.base
import importlib

def new(*args, **kwds):
    """Return model instance."""

    type = kwds.get('config', {}).get('type', 'base.Model')
    module_name = 'nemoa.model.classes.' + type.split('.', 1)[0]
    class_name = type.rsplit('.', 1)[-1]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
        model = getattr(module, class_name)(**kwds)
    except ImportError:
        raise ValueError("""could not create model:
            unknown model type '%s'.""" % (type))

    return model
