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
"""Unittests for module 'nemoa.base.env'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import pathlib
from nemoa.base import env
from nemoa.types import PathLikeList
import test
from test import Case

#
# Test Cases
#

class TestEnv(test.ModuleTest):
    module = env

    def setUp(self) -> None:
        self.sys_dirs = ['home', 'cwd']
        self.app_dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        self.dist_dirs = ['site_package_dir']
        self.pkg_dirs = ['package_dir', 'package_data_dir', 'package_temp_dir']
        self.site_dirs = ['site_temp_dir']
        self.app_vars = [
            'name', 'author', 'version', 'license', 'encoding', 'hostname',
            'username', 'osname']

    def is_dir_valid(
            self, dirname: str, path: pathlib.Path, appname: str,
            appauthor: str) -> bool:
        if dirname in self.sys_dirs: # Check system directories
            return True
        if dirname in self.app_dirs: # Check application dir
            if env.get_osname() == 'Linux':
                return appname in str(path)
            return appname in str(path) and appauthor in str(path)
        if dirname in self.dist_dirs: # Check distribution dir
            return appname in str(path)
        if dirname in self.pkg_dirs: # Check package dir
            # TODO (patrick.michl@gmail.com): Check if root package name is in
            # str(path)
            return True
        if dirname in self.site_dirs:
            # Site directories can be of arbitrary structure
            return True
        return False

    def is_dirs_valid(self, d: dict, appname: str, appauthor: str) -> bool:
        keys = set(
            self.sys_dirs + self.app_dirs + self.dist_dirs
            + self.pkg_dirs + self.site_dirs)
        if not d.keys() == keys:
            return False
        for key in keys:
            if not self.is_dir_valid(key, d[key], appname, appauthor):
                return False
        return True

    def test_update_dirs(self) -> None:
        app_name = 'funniest'
        app_author = 'Flying Circus'
        dirs_exist = hasattr(env, '_dirs')
        if dirs_exist:
            prev_dirs = getattr(env, '_dirs').copy()
        try:
            env.update_dirs(appname=app_name, appauthor=app_author)
            new_dirs = getattr(env, '_dirs').copy()
            self.assertTrue(self.is_dirs_valid(new_dirs, app_name, app_author))
        finally:
            if dirs_exist:
                setattr(env, '_dirs', prev_dirs)
            else:
                delattr(env, '_dirs')

    def test_get_dirs(self) -> None:
        app_name = env.get_var('name') or 'no name'
        app_author = env.get_var('author') or 'no author'
        app_dirs = env.get_dirs()
        is_valid = self.is_dirs_valid(app_dirs, app_name, app_author)
        self.assertTrue(is_valid)

    def test_get_dir(self) -> None:
        app_name = env.get_var('name') or 'no name'
        app_author = env.get_var('author') or 'no author'
        keys = set(self.app_dirs + self.dist_dirs + self.pkg_dirs)
        for key in keys:
            with self.subTest(f"get_dir('{key}')"):
                path = pathlib.Path(env.get_dir(key))
                is_valid = self.is_dir_valid(key, path, app_name, app_author)
                self.assertTrue(is_valid)

    def test_get_temp_dir(self) -> None:
        path = env.get_temp_dir()
        self.assertFalse(path.exists())
        path.mkdir()
        self.assertTrue(path.is_dir())
        path.rmdir()
        self.assertFalse(path.exists())

    def test_get_temp_file(self) -> None:
        path = env.get_temp_file()
        self.assertFalse(path.exists())
        path.touch()
        self.assertTrue(path.is_file())
        path.unlink()
        self.assertFalse(path.exists())

    def test_update_vars(self) -> None:
        vars_exist = hasattr(env, '_vars')
        try:
            if vars_exist:
                prev_vars = getattr(env, '_vars').copy()
            env.update_vars(__file__)
            new_vars = getattr(env, '_vars').copy()
            self.assertEqual(new_vars.get('author'), __author__)
            self.assertEqual(new_vars.get('email'), __email__)
            self.assertEqual(new_vars.get('license'), __license__)
        finally:
            if vars_exist:
                setattr(env, '_vars', prev_vars)
            else:
                delattr(env, '_vars')

    def test_get_var(self) -> None:
        cases = [Case(args=(key, )) for key in self.app_vars]
        self.assertCaseTrue(env.get_var, cases)

    def test_get_vars(self) -> None:
        envvars = env.get_vars()
        self.assertTrue(set(self.app_vars) <= envvars.keys())

    def test_get_encoding(self) -> None:
        self.assertIsInstance(env.get_encoding(), str)

    def test_get_hostname(self) -> None:
        self.assertIsInstance(env.get_hostname(), str)

    def test_get_osname(self) -> None:
        self.assertIsInstance(env.get_osname(), str)

    def test_get_username(self) -> None:
        self.assertIsInstance(env.get_username(), str)

    def test_get_cwd(self) -> None:
        self.assertTrue(env.get_cwd().is_dir())

    def test_get_home(self) -> None:
        self.assertTrue(env.get_home().is_dir())

    def test_clear_filename(self) -> None:
        self.assertEqual(env.clear_filename('3/\nE{$5}.e'), '3E5.e')

    def test_match_paths(self) -> None:
        paths: PathLikeList = [
            pathlib.Path('a.b'), pathlib.Path('b.a'), pathlib.Path('c/a.b'),
            pathlib.Path('a/b/c')]
        val = env.match_paths(paths, 'a.*')
        self.assertEqual(val, [pathlib.Path('a.b')])
        val = env.match_paths(paths, '*.a')
        self.assertEqual(val, [pathlib.Path('b.a')])
        val = env.match_paths(paths, 'c/*')
        self.assertEqual(val, [pathlib.Path('c/a.b')])
        val = env.match_paths(paths, 'a/*/c')
        self.assertEqual(val, [pathlib.Path('a/b/c')])

    def test_join_path(self) -> None:
        val = env.join_path(('a', ('b', 'c')), 'd')
        self.assertEqual(val, pathlib.Path('a/b/c/d'))

    def test_expand(self) -> None:
        udict = {'var1': 'a/%var2%', 'var2': 'b'}
        val = env.expand('%var1%/c', 'd', udict=udict)
        self.assertEqual(val, pathlib.Path('a/b/c/d'))

    def test_get_dirname(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.get_dirname(*path)
        self.assertEqual(val, str(pathlib.Path('a/b/c/d')))

    def test_filename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.filename(*path)
        self.assertEqual(val, 'base.ext')

    def test_basename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.basename(*path)
        self.assertEqual(val, 'base')

    def test_fileext(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.fileext(*path)
        self.assertEqual(val, 'ext')

    def test_mkdir(self) -> None:
        dirpath = env.get_temp_dir()
        env.mkdir(dirpath)
        self.assertTrue(dirpath.is_dir())
        dirpath.rmdir()

    def test_is_dir(self) -> None:
        dirpath = env.get_temp_dir()
        dirpath.mkdir()
        self.assertTrue(env.is_dir(dirpath))
        dirpath.rmdir()
        self.assertFalse(env.is_dir(dirpath))

    def test_touch(self) -> None:
        dirpath = env.get_temp_dir()
        filepath = dirpath / 'test'
        env.touch(filepath)
        self.assertTrue(filepath.is_file())
        filepath.unlink()
        dirpath.rmdir()

    def test_copytree(self) -> None:
        root = env.get_temp_dir()
        root.mkdir()
        source = root / 'source'
        source.mkdir()
        (source / 'file').touch()
        (source / 'dir').mkdir()
        target = root / 'target'
        target.mkdir()
        env.copytree(source, target)
        self.assertTrue((target / 'file').is_file())
        (source / 'file').unlink()
        (target / 'file').unlink()
        self.assertTrue((target / 'dir').is_dir())
        (source / 'dir').rmdir()
        (target / 'dir').rmdir()
        source.rmdir()
        target.rmdir()

    def test_is_file(self) -> None:
        file = env.get_temp_dir()
        file.touch()
        self.assertTrue(env.is_file(file))
        file.unlink()
        self.assertFalse(env.is_file(file))

    def test_rmdir(self) -> None:
        dirpath = env.get_temp_dir()
        dirpath.mkdir()
        env.rmdir(dirpath)
        self.assertFalse(dirpath.is_dir())
