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

import nemoa.model.builder.base

def types(type = None):
    """Get supported model types of model builders."""

    type_dict = {}

    # get supported base models
    types = nemoa.model.builder.base.types()
    for key, val in list(types.items()): type_dict[key] = ('base', val)

    if type is None:
        return {key: val[1] for key, val in list(type_dict.items())}
    if type in type_dict: return type_dict[type]

    return {}

def build(type = 'model', *args, **kwds):
    """Build model from parameters, datasets, etc. ."""

    # test if type is supported
    if type not in types():
        return ValueError(f"type '{type}' is not supported")

    module_name = types(type)[0]

    if module_name == 'base':
         model = nemoa.model.builder.base.build(type, *args, **kwds)

    return model or {}
