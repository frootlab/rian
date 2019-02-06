# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import test

#
# Test Cases
#

class TestCase(test.GenericTest):

    def test_session_about(self) -> None:

        with self.subTest(cmd="nemoa.about()"):
            test = isinstance(nemoa.about(), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('about')"):
            test = isinstance(nemoa.about('about'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('version')"):
            test = isinstance(nemoa.about('version'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('status')"):
            test = isinstance(nemoa.about('status'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('description')"):
            test = isinstance(nemoa.about('description'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('url')"):
            test = isinstance(nemoa.about('url'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('license')"):
            test = isinstance(nemoa.about('license'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('copyright')"):
            test = isinstance(nemoa.about('copyright'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('author')"):
            test = isinstance(nemoa.about('author'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('email')"):
            test = isinstance(nemoa.about('email'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('maintainer')"):
            test = isinstance(nemoa.about('maintainer'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.about('credits')"):
            test = isinstance(nemoa.about('credits'), list)
            self.assertTrue(test)

    def test_session_get(self) -> None:
        with self.subTest(cmd="nemoa.get('base')"):
            test = isinstance(nemoa.get('base'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('workspace')"):
            test = isinstance(nemoa.get('workspace'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default')"):
            test = isinstance(nemoa.get('default'), dict)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype')"):
            test = isinstance(nemoa.get('default', 'filetype'), dict)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype', 'dataset')"):
            filetype = nemoa.get('default', 'filetype', 'dataset')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype', 'network')"):
            filetype = nemoa.get('default', 'filetype', 'network')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype', 'system')"):
            filetype = nemoa.get('default', 'filetype', 'system')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype', 'model')"):
            filetype = nemoa.get('default', 'filetype', 'model')
            test = isinstance(filetype, str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.get('default', 'filetype', 'script')"):
            filetype = nemoa.get('default', 'filetype', 'script')
            test = isinstance(filetype, str)
            self.assertTrue(test)

    def test_session_list(self) -> None:

        with self.subTest(cmd="nemoa.list('bases')"):
            test = 'user' in nemoa.list('bases')
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('workspaces')"):
            worktree = nemoa.list('workspaces')
            test = isinstance(worktree, dict) \
                and 'user' in worktree \
                and 'site' in worktree \
                and 'cwd' in worktree
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('workspaces', base = 'site')"):
            workspaces = nemoa.list('workspaces', base='site')
            test = isinstance(workspaces, list)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('workspaces', base = 'user')"):
            workspaces = nemoa.list('workspaces', base='user')
            test = isinstance(workspaces, list)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('datasets')"):
            datasets = nemoa.list('datasets')
            test = isinstance(datasets, list) \
                and 'linear' in datasets \
                and 'logistic' in datasets \
                and 'sinus' in datasets
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('networks')"):
            networks = nemoa.list('networks')
            test = isinstance(networks, list) \
                and 'deep' in networks \
                and 'shallow' in networks
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('systems')"):
            systems = nemoa.list('systems')
            test = isinstance(systems, list) \
                and 'ann' in systems \
                and 'dbn' in systems \
                and 'grbm' in systems \
                and 'rbm' in systems
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('models')"):
            models = nemoa.list('models')
            test = isinstance(models, list) and 'test' in models
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.list('scripts')"):
            scripts = nemoa.list('scripts')
            test = isinstance(scripts, list)
            self.assertTrue(test)

    def test_session_path(self) -> None:

        with self.subTest(cmd="nemoa.path('basepath')"):
            self.assertTrue(isinstance(nemoa.path('basepath'), str))

        with self.subTest(cmd="nemoa.path('baseconf')"):
            self.assertTrue(isinstance(nemoa.path('baseconf'), str))

        with self.subTest(cmd="nemoa.path('datasets')"):
            self.assertTrue(isinstance(nemoa.path('datasets'), str))

        with self.subTest(cmd="nemoa.path('networks')"):
            test = isinstance(nemoa.path('networks'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('systems')"):
            test = isinstance(nemoa.path('systems'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('models')"):
            test = isinstance(nemoa.path('models'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('scripts')"):
            test = isinstance(nemoa.path('scripts'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('cache')"):
            test = isinstance(nemoa.path('cache'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('ini')"):
            test = isinstance(nemoa.path('ini'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('logfile')"):
            test = isinstance(nemoa.path('logfile'), str)
            self.assertTrue(test)

        with self.subTest(cmd="nemoa.path('expand', )"):
            valid = nemoa.path(
                'expand', '%basepath%', '%workspace%', check=True)

            invalid = nemoa.path(
                'expand', '%basepath%', '%workspace%', 'invalid_path_name',
                check=True)

            self.assertTrue(valid and not invalid)

        # test paths of configured objects
        objtypes = ['dataset', 'network', 'system', 'model', 'script']
        for objtype in objtypes:
            for name in nemoa.list(objtype + 's'):
                cmd = "nemoa.path('%s', '%s')" % (objtype, name)
                with self.subTest(cmd=cmd):
                    path = nemoa.path(objtype, name)
                    self.assertIsInstance(path, str)
