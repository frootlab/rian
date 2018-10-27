# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.base'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import tempfile
import datetime
from pathlib import Path
import numpy as np
from nemoa.base import check, env, nbase, binary, nclass, ndict, nfunc, nmodule
from nemoa.base import npath, table, literal
from nemoa.test import ModuleTestCase, Case
from nemoa.types import Any, Function, Module, PathLikeList

class TestBare(ModuleTestCase):
    """Testcase for the module nemoa.base.bare."""

    module = 'nemoa.base.bare'


class TestCheck(ModuleTestCase):
    """Testcase for the module nemoa.base.check."""

    module = 'nemoa.base.check'

    def test_has_type(self) -> None:
        self.assertNoneRaises(TypeError, check.has_type, [
            Case(args=('', 0, int)),
            Case(args=('', '', str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict))])
        self.assertAllRaises(TypeError, check.has_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list))])

    def test_has_opt_type(self) -> None:
        self.assertNoneRaises(TypeError, check.has_opt_type, [
            Case(args=('', None, int)),
            Case(args=('', None, str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict))])
        self.assertAllRaises(TypeError, check.has_opt_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list))])

    def test_is_callable(self) -> None:
        self.assertNoneRaises(TypeError, check.is_callable, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])
        self.assertAllRaises(TypeError, check.has_type, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_class(self) -> None:
        self.assertNoneRaises(TypeError, check.is_class, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])
        self.assertAllRaises(TypeError, check.is_class, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_subclass(self) -> None:
        self.assertNoneRaises(TypeError, check.is_subclass, [
            Case(args=('', int, object)),
            Case(args=('', dict, dict)),
            Case(args=('', list, object)),
            Case(args=('', str, str))])
        self.assertAllRaises(TypeError, check.is_subclass, [
            Case(args=('', int, str)),
            Case(args=('', dict, list)),
            Case(args=('', object, float)),
            Case(args=('', str, complex))])

    def test_is_subset(self) -> None:
        self.assertNoneRaises(ValueError, check.is_subset, [
            Case(args=('', set(), '', set())),
            Case(args=('', {1}, '', {1, 2})),
            Case(args=('', {2}, '', {1, 2})),
            Case(args=('', {2, 1}, '', {1, 2}))])
        self.assertAllRaises(ValueError, check.is_subset, [
            Case(args=('', {1}, '', set())),
            Case(args=('', {2}, '', {1})),
            Case(args=('', {1, 2}, '', {1})),
            Case(args=('', {1, 2, 3}, '', set()))])

    def test_is_positive(self) -> None:
        self.assertNoneRaises(ValueError, check.is_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])
        self.assertAllRaises(ValueError, check.is_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_is_negative(self) -> None:
        self.assertNoneRaises(ValueError, check.is_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])
        self.assertAllRaises(ValueError, check.is_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_positive(self) -> None:
        self.assertNoneRaises(ValueError, check.is_not_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])
        self.assertAllRaises(ValueError, check.is_not_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_negative(self) -> None:
        self.assertNoneRaises(ValueError, check.is_not_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])
        self.assertAllRaises(ValueError, check.is_not_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_has_attr(self) -> None:
        self.assertNoneRaises(AttributeError, check.has_attr, [
            Case(args=('', 'format')),
            Case(args=(0, 'real')),
            Case(args=(1j, 'imag'))])
        self.assertAllRaises(AttributeError, check.has_attr, [
            Case(args=(list(), 'keys')),
            Case(args=(0, ''))])

class TestEnv(ModuleTestCase):
    """Testcase for the module nemoa.base.env."""

    module = 'nemoa.base.env'

    def setUp(self) -> None:
        self.sys_dirs = ['home', 'cwd']
        self.app_dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        self.dist_dirs = ['site_package_dir']
        self.pkg_dirs = ['package_dir', 'package_data_dir']
        self.app_vars = [
            'name', 'author', 'version', 'license', 'encoding', 'hostname',
            'username', 'osname']

    def is_dir_valid(
            self, dirname: str, path: Path, appname: str,
            appauthor: str) -> bool:
        if dirname in self.sys_dirs: # Check system directories
            return True
        if dirname in self.app_dirs: # Check application dir
            return appname in str(path) and appauthor in str(path)
        if dirname in self.dist_dirs: # Check distribution dir
            return appname in str(path)
        if dirname in self.pkg_dirs: # Check package dir
            # TODO (patrick.michl@gmail.com): Check if root package name is in
            # str(path)
            return True
        return False

    def is_dirs_valid(self, d: dict, appname: str, appauthor: str) -> bool:
        keys = set(
            self.sys_dirs + self.app_dirs + self.dist_dirs + self.pkg_dirs)
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
                path = Path(env.get_dir(key))
                is_valid = self.is_dir_valid(key, path, app_name, app_author)
                self.assertTrue(is_valid)

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
        self.assertAllTrue(env.get_var, cases)

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

class TestNbase(ModuleTestCase):
    """Testcase for the module nemoa.base.nbase."""

    module = 'nemoa.base.nbase'

    def test_ObjectIP(self) -> None:
        obj = nbase.ObjectIP()
        obj.name = 'test'
        self.assertTrue(obj.get('config') == {'name': 'test'})
        obj.path = ('%site_data_dir%', 'test')
        self.assertNotIn('%', obj.path)

class TestBinary(ModuleTestCase):
    """Testcase for the module nemoa.base.binary."""

    module = 'nemoa.base.binary'

    def test_as_bytes(self) -> None:
        self.assertEqual(binary.as_bytes(b'test'), b'test')
        self.assertEqual(binary.as_bytes('test'), b'test')
        self.assertEqual(binary.as_bytes(bytearray(b'test')), b'test')
        self.assertEqual(binary.as_bytes(memoryview(b'test')), b'test')

    def test_compress(self) -> None:
        data = binary.compress(b'test', level=0)
        self.assertEqual(data, b'x\x01\x01\x04\x00\xfb\xfftest\x04]\x01\xc1')
        data = binary.compress(b'test', level=1)
        self.assertEqual(data, b'x\x01+I-.\x01\x00\x04]\x01\xc1')
        data = binary.compress(b'test', level=9)
        self.assertEqual(data, b'x\xda+I-.\x01\x00\x04]\x01\xc1')

    def test_decompress(self) -> None:
        for level in range(-1, 10):
            data = binary.compress(b'test', level=level)
            self.assertEqual(binary.decompress(data), b'test')

    def test_encode(self) -> None:
        data = binary.encode(b'test', encoding='base64')
        self.assertEqual(data, b'dGVzdA==')
        data = binary.encode(b'test', encoding='base32')
        self.assertEqual(data, b'ORSXG5A=')
        data = binary.encode(b'test', encoding='base16')
        self.assertEqual(data, b'74657374')

    def test_decode(self) -> None:
        for encoding in ['base64', 'base32', 'base16', 'base85']:
            data = binary.encode(b'test', encoding=encoding)
            self.assertEqual(binary.decode(data, encoding=encoding), b'test')

    def test_pack(self) -> None:
        data = binary.pack({True: 1}, encoding='base64')
        self.assertEqual(data, b'gAN9cQCISwFzLg==')
        data = binary.pack(None, encoding='base32')
        self.assertEqual(data, b'QABU4LQ=')
        data = binary.pack(True, encoding='base16', compression=9)
        self.assertEqual(data, b'78DA6B60EED00300034B013A')

    def test_unpack(self) -> None:
        o1 = None
        o2 = [None, True, 1, .0, 1+1j, 'a', b'b', type]
        o3 = {True: 1, 'a': [.5, (1j, ), None]}
        tests = [(o1, None, None), (o2, None, None), (o3, None, None)]
        for obj, enc, comp in tests:
            data = binary.pack(obj, encoding=enc, compression=comp)
            iscomp = isinstance(comp, int)
            self.assertEqual(binary.unpack(data, compressed=iscomp), obj)

class TestNmodule(ModuleTestCase):
    """Testcase for the module nemoa.base.nmodule."""

    module = 'nemoa.base.nmodule'

    def setUp(self) -> None:
        self.this = nmodule.get_instance(__name__)
        self.parent = nmodule.get_instance('nemoa.base')

    def test_get_curname(self) -> None:
        self.assertEqual(nmodule.get_curname(), __name__)

    def test_get_caller(self) -> None:
        self.assertEqual(nmodule.get_caller(), __name__ + '.test_get_caller')

    def test_crop_functions(self) -> None:
        name = nmodule.crop_functions.__name__
        fullname = nmodule.crop_functions.__module__ + '.' + name
        cropped = nmodule.crop_functions(prefix='crop_', ref=nmodule)
        self.assertIn('functions', cropped)

    def test_get_root(self) -> None:
        self.assertEqual(nmodule.get_root().__name__, 'nemoa')

    def test_get_parent(self) -> None:
        self.assertEqual(nmodule.get_parent().__name__, 'nemoa.base')

    def test_get_submodule(self) -> None:
        sub = nmodule.get_submodule('__test__', ref=self.parent)
        self.assertIsInstance(sub, Module)

    def test_get_submodules(self) -> None:
        subs = nmodule.get_submodules(ref=self.parent)
        self.assertIn(__name__, subs)

    def test_get_instance(self) -> None:
        ref = nmodule.get_instance(__name__)
        self.assertIsInstance(ref, Module)
        self.assertEqual(getattr(ref, '__name__'), __name__)

    def test_get_caller_ref(self) -> None:
        ref = nmodule.get_caller_ref()
        self.assertIsInstance(ref, Module)

    def test_get_attr(self) -> None:
        self.assertEqual(nmodule.get_attr('__name__'), __name__)

    def test_get_functions(self) -> None:
        name = nmodule.get_functions.__name__
        fullname = nmodule.get_functions.__module__ + '.' + name
        self.assertIn(fullname, nmodule.get_functions(ref=nmodule))
        count = len(nmodule.get_functions(ref=nmodule, name=''))
        self.assertEqual(count, 0)
        count = len(nmodule.get_functions(ref=nmodule, name=name))
        self.assertEqual(count, 1)

    def test_search(self) -> None:
        count = len(nmodule.search(ref=nmodule, name='search'))
        self.assertEqual(count, 1)

class TestNclass(ModuleTestCase):
    """Testcase for the module nemoa.base.nclass."""

    module = 'nemoa.base.nclass'

    @staticmethod
    def get_test_object() -> Any:
        class Base:
            @nclass.attributes(name='a', group=1)
            def geta(self) -> None:
                pass
            @nclass.attributes(name='b', group=2)
            def getb(self) -> None:
                pass
            @nclass.attributes(name='b', group=2)
            def setb(self) -> None:
                pass
        return Base()

    def test_attributes(self) -> None:
        obj = self.get_test_object()
        self.assertEqual(getattr(obj.geta, 'name', None), 'a')
        self.assertEqual(getattr(obj.getb, 'name', None), 'b')

    def test_methods(self) -> None:
        obj = self.get_test_object()
        names = nclass.methods(obj, pattern='get*').keys()
        self.assertEqual(names, {'geta', 'getb'})
        names = nclass.methods(obj, pattern='*b').keys()
        self.assertEqual(names, {'getb', 'setb'})

class TestNfunc(ModuleTestCase):
    """Testcase for the module nemoa.base.nfunc."""

    module = 'nemoa.base.nfunc'

    def test_splitargs(self) -> None:
        self.assertEqual(
            nfunc.splitargs("f(1., 'a', b = 2)"),
            ('f', (1.0, 'a'), {'b': 2}))

    def test_get_summary(self) -> None:
        text = nfunc.get_summary(nfunc.get_summary)
        self.assertEqual(text, 'Get summary line of a function')

    def test_get_instance(self) -> None:
        func = nfunc.get_instance(nfunc.__name__ + '.get_instance')
        self.assertIsInstance(func, Function)

    def test_get_kwds(self) -> None:
        kwds = nfunc.get_kwds(nfunc.get_kwds)
        self.assertEqual(kwds, {'default': None})
        kwds = nfunc.get_kwds(nfunc.get_kwds, default={})
        self.assertEqual(kwds, {})
        kwds = nfunc.get_kwds(nfunc.get_kwds, default={'default': True})
        self.assertEqual(kwds, {'default': True})

class TestNdict(ModuleTestCase):
    """Testcase for the module nemoa.base.ndict."""

    module = 'nemoa.base.ndict'

    def test_select(self) -> None:
        self.assertTrue(
            ndict.select({'a1': 1, 'a2': 2, 'b1': 3}, pattern='a*') \
            == {'a1': 1, 'a2': 2})

    def test_groupby(self) -> None:
        self.assertEqual(
            ndict.groupby(
                {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a'),
            {
                0: {1: {'a': 0}, 2: {'a': 0}},
                1: {3: {'a': 1}}, None: {4: {}}})

    def test_flatten(self) -> None:
        self.assertEqual(
            ndict.flatten({1: {'a': {}}, 2: {'b': {}}}),
            {'a': {}, 'b': {}})
        self.assertEqual(
            ndict.flatten({1: {'a': {}}, 2: {'b': {}}}, group='id'),
            {'a': {'id': 1}, 'b': {'id': 2}})

    def test_merge(self) -> None:
        self.assertEqual(
            ndict.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3}),
            {'a': 1, 'b': 2, 'c': 3})

    def test_crop(self) -> None:
        self.assertEqual(
            ndict.crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a'),
            {'1': 1, '2': 2})

    def test_strkeys(self) -> None:
        self.assertEqual(
            ndict.strkeys({(1, 2): 3, None: {True: False}}),
            {('1', '2'): 3, 'None': {'True': False}})

    def test_sumjoin(self) -> None:
        self.assertEqual(
            ndict.sumjoin({'a': 1}, {'a': 2, 'b': 3}), {'a': 3, 'b': 3})
        self.assertEqual(
            ndict.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True}),
            {1: 'ab', 2: 2})

class TestTable(ModuleTestCase):
    """Testcase for the module nemoa.base.table."""

    module = 'nemoa.base.table'

    def test_addcols(self) -> None:
        src = np.array(
            [('a'), ('b')], dtype=[('z', 'U4')])
        tgt = np.array(
            [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        new = table.addcols(tgt, src, 'z')
        self.assertEqual(new['z'][0], 'a')

class TestLiteral(ModuleTestCase):
    """Testcase for the module nemoa.base.literal."""

    module = 'nemoa.base.literal'

    def test_as_path(self) -> None:
        self.assertAllEqual(literal.as_path, [
            Case(args=('a/b/c', ), value=Path('a/b/c')),
            Case(args=('a\\b\\c', ), value=Path('a/b/c')),
            Case(args=('%home%/test', ), value=Path.home() / 'test')])

    def test_as_datetime(self) -> None:
        val = datetime.datetime.now()
        self.assertEqual(literal.as_datetime(str(val)), val)

    def test_as_list(self) -> None:
        self.assertAllEqual(literal.as_list, [
            Case(args=('a, 2, ()', ), value=['a', '2', '()']),
            Case(args=('[1, 2, 3]', ), value=[1, 2, 3])])

    def test_as_tuple(self) -> None:
        self.assertAllEqual(literal.as_tuple, [
            Case(args=('a, 2, ()', ), value=('a', '2', '()')),
            Case(args=('(1, 2, 3)', ), value=(1, 2, 3))])

    def test_as_set(self) -> None:
        self.assertAllEqual(literal.as_set, [
            Case(args=('a, 2, ()', ), value={'a', '2', '()'}),
            Case(args=('{1, 2, 3}', ), value={1, 2, 3})])

    def test_as_dict(self) -> None:
        self.assertAllEqual(literal.as_dict, [
            Case(args=("a = 'b', b = 1", ), value={'a': 'b', 'b': 1}),
            Case(args=("'a': 'b', 'b': 1", ), value={'a': 'b', 'b': 1})])

    def test_decode(self) -> None:
        self.assertAllEqual(literal.decode, [
            Case(args=(str('t'), 'str'), value='t'),
            Case(args=(str(True), 'bool'), value=True),
            Case(args=(str(1), 'int'), value=1),
            Case(args=(str(.5), 'float'), value=.5),
            Case(args=(str(1+1j), 'complex'), value=1+1j)])

class TestNpath(ModuleTestCase):
    """Testcase for the module nemoa.base.npath."""

    module = 'nemoa.base.npath'

    def test_clear(self) -> None:
        self.assertEqual(npath.clear('3/\nE{$5}.e'), '3E5.e')

    def test_match(self) -> None:
        paths: PathLikeList = [Path('a.b'), Path('b.a'), Path('c/a.b')]
        val = npath.match(paths, 'a.*')
        self.assertEqual(val, [Path('a.b')])
        val = npath.match(paths, '*.a')
        self.assertEqual(val, [Path('b.a')])
        val = npath.match(paths, 'c\\*')
        self.assertEqual(val, [Path('c/a.b')])
        val = npath.match(paths, 'c/*')
        self.assertEqual(val, [Path('c/a.b')])

    def test_join(self) -> None:
        val = npath.join(('a', ('b', 'c')), 'd')
        self.assertEqual(val, Path('a/b/c/d'))

    def test_expand(self) -> None:
        udict = {'var1': 'a/%var2%', 'var2': 'b'}
        val = npath.expand('%var1%/c', 'd', udict=udict)
        self.assertEqual(val, Path('a/b/c/d'))

    def test_dirname(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.dirname(*path)
        self.assertEqual(val, str(Path('a/b/c/d')))

    def test_filename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.filename(*path)
        self.assertEqual(val, 'base.ext')

    def test_basename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.basename(*path)
        self.assertEqual(val, 'base')

    def test_fileext(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.fileext(*path)
        self.assertEqual(val, 'ext')

    def test_mkdir(self) -> None:
        dirpath = Path(tempfile.TemporaryDirectory().name)
        npath.mkdir(dirpath)
        self.assertTrue(dirpath.is_dir())
        dirpath.rmdir()

    def test_is_dir(self) -> None:
        dirpath = Path(tempfile.TemporaryDirectory().name)
        dirpath.mkdir()
        self.assertTrue(npath.is_dir(dirpath))
        dirpath.rmdir()
        self.assertFalse(npath.is_dir(dirpath))

    def test_touch(self) -> None:
        dirpath = Path(tempfile.TemporaryDirectory().name)
        filepath = dirpath / 'test'
        npath.touch(filepath)
        self.assertTrue(filepath.is_file())
        filepath.unlink()
        dirpath.rmdir()

    def test_copytree(self) -> None:
        root = Path(tempfile.TemporaryDirectory().name)
        root.mkdir()
        source = root / 'source'
        source.mkdir()
        (source / 'file').touch()
        (source / 'dir').mkdir()
        target = root / 'target'
        target.mkdir()
        npath.copytree(source, target)
        self.assertTrue((target / 'file').is_file())
        (source / 'file').unlink()
        (target / 'file').unlink()
        self.assertTrue((target / 'dir').is_dir())
        (source / 'dir').rmdir()
        (target / 'dir').rmdir()
        source.rmdir()
        target.rmdir()

    def test_is_file(self) -> None:
        file = Path(tempfile.NamedTemporaryFile().name)
        file.touch()
        self.assertTrue(npath.is_file(file))
        file.unlink()
        self.assertFalse(npath.is_file(file))

    def test_rmdir(self) -> None:
        dirpath = Path(tempfile.TemporaryDirectory().name)
        dirpath.mkdir()
        npath.rmdir(dirpath)
        self.assertFalse(dirpath.is_dir())
