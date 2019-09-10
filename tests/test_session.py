# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Frootlab Rian, https://www.frootlab.org/rian
#
#  Rian is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rian is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Rian. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import rian
from hup.base import test

#
# Test Cases
#

class TestCase(test.GenericTest):

    def test_session_about(self) -> None:

        with self.subTest(cmd="rian.about()"):
            test = isinstance(rian.about(), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('about')"):
            test = isinstance(rian.about('about'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('version')"):
            test = isinstance(rian.about('version'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('description')"):
            test = isinstance(rian.about('description'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('url')"):
            test = isinstance(rian.about('url'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('license')"):
            test = isinstance(rian.about('license'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('copyright')"):
            test = isinstance(rian.about('copyright'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('author')"):
            test = isinstance(rian.about('author'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('email')"):
            test = isinstance(rian.about('email'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('maintainer')"):
            test = isinstance(rian.about('maintainer'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.about('credits')"):
            test = isinstance(rian.about('credits'), list)
            self.assertTrue(test)

    def test_session_get(self) -> None:
        with self.subTest(cmd="rian.get('base')"):
            test = isinstance(rian.get('base'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('workspace')"):
            test = isinstance(rian.get('workspace'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default')"):
            test = isinstance(rian.get('default'), dict)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype')"):
            test = isinstance(rian.get('default', 'filetype'), dict)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype', 'dataset')"):
            filetype = rian.get('default', 'filetype', 'dataset')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype', 'network')"):
            filetype = rian.get('default', 'filetype', 'network')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype', 'system')"):
            filetype = rian.get('default', 'filetype', 'system')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype', 'model')"):
            filetype = rian.get('default', 'filetype', 'model')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.get('default', 'filetype', 'script')"):
            filetype = rian.get('default', 'filetype', 'script')
            test = isinstance(filetype, str)
            self.assertTrue(test)

    def test_session_list(self) -> None:

        with self.subTest(cmd="rian.list('bases')"):
            test = 'user' in rian.list('bases')
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('workspaces')"):
            worktree = rian.list('workspaces')
            test = isinstance(worktree, dict) \
                and 'user' in worktree \
                and 'site' in worktree \
                and 'cwd' in worktree
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('workspaces', base = 'site')"):
            workspaces = rian.list('workspaces', base='site')
            test = isinstance(workspaces, list)
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('workspaces', base = 'user')"):
            workspaces = rian.list('workspaces', base='user')
            test = isinstance(workspaces, list)
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('datasets')"):
            datasets = rian.list('datasets')
            test = isinstance(datasets, list) \
                and 'linear' in datasets \
                and 'logistic' in datasets \
                and 'sinus' in datasets
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('networks')"):
            networks = rian.list('networks')
            test = isinstance(networks, list) \
                and 'deep' in networks \
                and 'shallow' in networks
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('systems')"):
            systems = rian.list('systems')
            test = isinstance(systems, list) \
                and 'ann' in systems \
                and 'dbn' in systems \
                and 'grbm' in systems \
                and 'rbm' in systems
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('models')"):
            models = rian.list('models')
            test = isinstance(models, list) and 'test' in models
            self.assertTrue(test)

        with self.subTest(cmd="rian.list('scripts')"):
            scripts = rian.list('scripts')
            test = isinstance(scripts, list)
            self.assertTrue(test)

    def test_session_path(self) -> None:

        with self.subTest(cmd="rian.path('basepath')"):
            self.assertTrue(isinstance(rian.path('basepath'), str))

        with self.subTest(cmd="rian.path('baseconf')"):
            self.assertTrue(isinstance(rian.path('baseconf'), str))

        with self.subTest(cmd="rian.path('datasets')"):
            self.assertTrue(isinstance(rian.path('datasets'), str))

        with self.subTest(cmd="rian.path('networks')"):
            test = isinstance(rian.path('networks'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('systems')"):
            test = isinstance(rian.path('systems'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('models')"):
            test = isinstance(rian.path('models'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('scripts')"):
            test = isinstance(rian.path('scripts'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('cache')"):
            test = isinstance(rian.path('cache'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('ini')"):
            test = isinstance(rian.path('ini'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('logfile')"):
            test = isinstance(rian.path('logfile'), str)
            self.assertTrue(test)

        with self.subTest(cmd="rian.path('expand')"):
            valid = rian.path(
                'expand', '%basepath%', '%workspace%', check=True)
            invalid = rian.path(
                'expand', '%basepath%', '%workspace%', 'invalid_path_name',
                check=True)

            self.assertTrue(valid and not invalid)

        # test paths of configured objects
        objtypes = ['dataset', 'network', 'system', 'model', 'script']
        for objtype in objtypes:
            for name in rian.list(objtype + 's'):
                cmd = "rian.path('%s', '%s')" % (objtype, name)
                with self.subTest(cmd=cmd):
                    path = rian.path(objtype, name)
                    self.assertIsInstance(path, str)
