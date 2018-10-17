# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import tempfile
from pathlib import Path

from nemoa.core import ntest
from nemoa.types import Any, Function, Module

class TestNapp(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.napp."""

    module = 'nemoa.core.napp'
    app_dirs = [
        'user_cache_dir', 'user_config_dir', 'user_data_dir',
        'user_log_dir', 'site_config_dir', 'site_data_dir']
    dist_dirs = ['site_package_dir']
    pkg_dirs = ['package_dir', 'package_data_dir']
    app_vars = ['name', 'author', 'version', 'license']

    def is_dir_valid(
            self, dirname: str, path: Path, appname: str,
            appauthor: str) -> bool:
        if dirname in self.app_dirs: # Check application dir
            return appname in str(path) and appauthor in str(path)
        if dirname in self.dist_dirs: # Check distribution dir
            return appname in str(path)
        if dirname in self.pkg_dirs: # Check package dir
            # TODO: check root package name
            return True
        return False

    def is_dirs_valid(self, d: dict, appname: str, appauthor: str) -> bool:
        # Check keys
        keys = set(self.app_dirs + self.dist_dirs + self.pkg_dirs)
        if not d.keys() == keys:
            return False
        for key in keys:
            if not self.is_dir_valid(key, d[key], appname, appauthor):
                return False
        return True

    def test_update_dirs(self) -> None:
        from nemoa.core import napp
        app_name = 'funniest'
        app_author = 'Flying Circus'
        dirs_exist = hasattr(napp, '_dirs')
        if dirs_exist:
            prev_dirs = getattr(napp, '_dirs').copy()
        napp.update_dirs(appname=app_name, appauthor=app_author)
        new_dirs = getattr(napp, '_dirs').copy()
        is_valid = self.is_dirs_valid(new_dirs, app_name, app_author)
        self.assertTrue(is_valid)
        if dirs_exist:
            setattr(napp, '_dirs', prev_dirs)
        else:
            delattr(napp, '_dirs')

    def test_get_dirs(self) -> None:
        from nemoa.core import napp
        app_name = napp.get_var('name') or 'no name'
        app_author = napp.get_var('author') or 'no author'
        app_dirs = napp.get_dirs()
        is_valid = self.is_dirs_valid(app_dirs, app_name, app_author)
        self.assertTrue(is_valid)

    def test_get_dir(self) -> None:
        from nemoa.core import napp
        app_name = napp.get_var('name') or 'no name'
        app_author = napp.get_var('author') or 'no author'
        keys = set(self.app_dirs + self.dist_dirs + self.pkg_dirs)
        for key in keys:
            with self.subTest(f"get_dir('{key}')"):
                path = Path(napp.get_dir(key))
                is_valid = self.is_dir_valid(key, path, app_name, app_author)
                self.assertTrue(is_valid)

    def test_update_vars(self) -> None:
        from nemoa.core import napp
        vars_exist = hasattr(napp, '_vars')
        if vars_exist:
            prev_vars = getattr(napp, '_vars').copy()
        napp.update_vars(__file__)
        new_vars = getattr(napp, '_vars').copy()
        self.assertEqual(new_vars.get('author'), __author__)
        self.assertEqual(new_vars.get('email'), __email__)
        self.assertEqual(new_vars.get('license'), __license__)
        if vars_exist:
            setattr(napp, '_vars', prev_vars)
        else:
            delattr(napp, '_vars')

    def test_get_var(self) -> None:
        from nemoa.core import napp
        for key in self.app_vars:
            with self.subTest(f"get_var('{key}')"):
                self.assertTrue(napp.get_var(key))

class TestNarray(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.narray."""

    module = 'nemoa.core.narray'

    def test_from_dict(self) -> None:
        from nemoa.core import narray
        from nemoa.types import NaN
        import numpy as np
        arr = np.array([[NaN, 1.], [NaN, NaN]])
        dic = {('a', 'b'): 1.}
        labels = (['a', 'b'], ['a', 'b'])
        self.assertTrue(
            np.allclose(
                narray.from_dict(dic, labels=labels), arr,
                equal_nan=True))

    def test_as_dict(self) -> None:
        from nemoa.core import narray
        from nemoa.types import NaN
        import numpy as np
        x = np.array([[NaN, 1.], [NaN, NaN]])
        labels = (['a', 'b'], ['a', 'b'])
        d = narray.as_dict(x, labels=labels)
        self.assertEqual(d, {('a', 'b'): 1.})

class TestNbase(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nbase."""

    module = 'nemoa.core.nbase'

    def test_ObjectIP(self) -> None:
        from nemoa.core import nbase
        obj = nbase.ObjectIP()
        obj.name = 'test'
        self.assertTrue(obj.get('config') == {'name': 'test'})
        obj.path = ('%site_data_dir%', 'test')
        self.assertNotIn('%', obj.path)

class TestNbytes(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nbytes."""

    module = 'nemoa.core.nbytes'

    def test_compress(self) -> None:
        from nemoa.core import nbytes
        data = nbytes.compress(b'test', level=0)
        self.assertEqual(data, b'x\x01\x01\x04\x00\xfb\xfftest\x04]\x01\xc1')
        data = nbytes.compress(b'test', level=1)
        self.assertEqual(data, b'x\x01+I-.\x01\x00\x04]\x01\xc1')
        data = nbytes.compress(b'test', level=9)
        self.assertEqual(data, b'x\xda+I-.\x01\x00\x04]\x01\xc1')

    def test_decompress(self) -> None:
        from nemoa.core import nbytes
        for level in range(-1, 10):
            data = nbytes.compress(b'test', level=level)
            self.assertEqual(nbytes.decompress(data), b'test')

    def test_encode(self) -> None:
        from nemoa.core import nbytes
        data = nbytes.encode(b'test', encoding='base64')
        self.assertEqual(data, b'dGVzdA==')
        data = nbytes.encode(b'test', encoding='base32')
        self.assertEqual(data, b'ORSXG5A=')
        data = nbytes.encode(b'test', encoding='base16')
        self.assertEqual(data, b'74657374')

    def test_decode(self) -> None:
        from nemoa.core import nbytes
        for encoding in ['base64', 'base32', 'base16', 'base85']:
            data = nbytes.encode(b'test', encoding=encoding)
            self.assertEqual(nbytes.decode(data, encoding=encoding), b'test')

    def test_pack(self) -> None:
        from nemoa.core import nbytes
        data = nbytes.pack({True: 1}, encoding='base64')
        self.assertEqual(data, b'gAN9cQCISwFzLg==')
        data = nbytes.pack(None, encoding='base32')
        self.assertEqual(data, b'QABU4LQ=')
        data = nbytes.pack(True, encoding='base16', compression=9)
        self.assertEqual(data, b'78DA6B60EED00300034B013A')

    def test_unpack(self) -> None:
        from nemoa.core import nbytes
        o1 = None
        o2 = [None, True, 1, .0, 1+1j, 'a', b'b', type]
        o3 = {True: 1, 'a': [.5, (1j, ), None]}
        tests = [(o1, None, None), (o2, None, None), (o3, None, None)]
        for obj, enc, comp in tests:
            data = nbytes.pack(obj, encoding=enc, compression=comp)
            iscomp = isinstance(comp, int)
            self.assertEqual(nbytes.unpack(data, compressed=iscomp), obj)

class TestNconsole(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nconsole."""

    module = 'nemoa.core.nconsole'

    def test_Getch(self) -> None:
        from nemoa.core import nconsole
        obj = nconsole.Getch() if callable(nconsole.Getch) else None
        self.assertIsInstance(obj, nconsole.GetchBase)

class TestNmodule(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nmodule."""

    module = 'nemoa.core.nmodule'

    def test_curname(self) -> None:
        from nemoa.core import nmodule
        self.assertEqual(nmodule.curname(), __name__)

    def test_caller(self) -> None:
        from nemoa.core import nmodule
        self.assertEqual(nmodule.caller(), __name__ + '.test_caller')

    def test_submodules(self) -> None:
        from nemoa.core import nmodule
        mref = nmodule.inst('nemoa.core')
        self.assertIn(nmodule.__name__, nmodule.submodules(mref))

    def test_inst(self) -> None:
        from nemoa.core import nmodule
        from typing import cast
        name = nmodule.__name__
        self.assertTrue(hasattr(nmodule.inst(name), '__name__'))
        self.assertEqual(cast(Module, nmodule.inst(name)).__name__, name)

    def test_get_functions(self) -> None:
        from nemoa.core import nmodule
        name = nmodule.get_functions.__name__
        fullname = nmodule.get_functions.__module__ + '.' + name
        self.assertIn(fullname, nmodule.get_functions(nmodule))
        self.assertEqual(len(nmodule.get_functions(nmodule, name='')), 0)
        self.assertEqual(len(nmodule.get_functions(nmodule, name=name)), 1)

    def test_search(self) -> None:
        from nemoa.core import nmodule
        self.assertEqual(len(nmodule.search(nmodule, name='search')), 1)

class TestNclass(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nclass."""

    module = 'nemoa.core.nclass'

    @staticmethod
    def get_test_object() -> Any:
        from nemoa.core import nclass
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

    def test_hasbase(self) -> None:
        from nemoa.core import nclass
        obj = self.get_test_object()
        self.assertTrue(nclass.hasbase(None, 'object'))
        self.assertTrue(nclass.hasbase(obj, 'Base'))

    def test_attributes(self) -> None:
        from nemoa.core import nclass
        obj = self.get_test_object()
        self.assertEqual(getattr(obj.geta, 'name', None), 'a')
        self.assertEqual(getattr(obj.getb, 'name', None), 'b')

    def test_methods(self) -> None:
        from nemoa.core import nclass
        obj = self.get_test_object()
        names = nclass.methods(obj, pattern='get*').keys()
        self.assertEqual(names, {'geta', 'getb'})
        names = nclass.methods(obj, pattern='*b').keys()
        self.assertEqual(names, {'getb', 'setb'})

class TestNfunc(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nfunc."""

    module = 'nemoa.core.nfunc'

    def test_about(self) -> None:
        from nemoa.core import nfunc
        about = nfunc.about(nfunc.about)
        self.assertEqual(about, 'Summary line of docstring of a function')

    def test_inst(self) -> None:
        from nemoa.core import nfunc
        func = nfunc.inst(nfunc.__name__ + '.inst')
        self.assertIsInstance(func, Function)

    def test_kwds(self) -> None:
        from nemoa.core import nfunc
        kwds = nfunc.kwds(nfunc.kwds)
        self.assertEqual(kwds, {'default': None})
        kwds = nfunc.kwds(nfunc.kwds, default={})
        self.assertEqual(kwds, {})
        kwds = nfunc.kwds(nfunc.kwds, default={'default': True})
        self.assertEqual(kwds, {'default': True})

class TestNdict(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.ndict."""

    module = 'nemoa.core.ndict'

    def test_select(self) -> None:
        from nemoa.core import ndict
        self.assertTrue(
            ndict.select({'a1': 1, 'a2': 2, 'b1': 3}, pattern='a*') \
            == {'a1': 1, 'a2': 2})

    def test_groupby(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.groupby(
                {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a'),
            {
                0: {1: {'a': 0}, 2: {'a': 0}},
                1: {3: {'a': 1}}, None: {4: {}}})

    def test_flatten(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.flatten({1: {'a': {}}, 2: {'b': {}}}),
            {'a': {}, 'b': {}})
        self.assertEqual(
            ndict.flatten({1: {'a': {}}, 2: {'b': {}}}, group='id'),
            {'a': {'id': 1}, 'b': {'id': 2}})

    def test_merge(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3}),
            {'a': 1, 'b': 2, 'c': 3})

    def test_crop(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a'),
            {'1': 1, '2': 2})

    def test_strkeys(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.strkeys({(1, 2): 3, None: {True: False}}),
            {('1', '2'): 3, 'None': {'True': False}})

    def test_sumjoin(self) -> None:
        from nemoa.core import ndict
        self.assertEqual(
            ndict.sumjoin({'a': 1}, {'a': 2, 'b': 3}), {'a': 3, 'b': 3})
        self.assertEqual(
            ndict.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True}),
            {1: 'ab', 2: 2})

class TestNsysinfo(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.nsysinfo."""

    module = 'nemoa.core.nsysinfo'

    def test_encoding(self) -> None:
        from nemoa.core import nsysinfo
        self.assertIsInstance(nsysinfo.encoding(), str)

    def test_hostname(self) -> None:
        from nemoa.core import nsysinfo
        self.assertIsInstance(nsysinfo.hostname(), str)

    def test_osname(self) -> None:
        from nemoa.core import nsysinfo
        self.assertIsInstance(nsysinfo.osname(), str)

    def test_username(self) -> None:
        from nemoa.core import nsysinfo
        self.assertIsInstance(nsysinfo.username(), str)

    def test_ttylib(self) -> None:
        from nemoa.core import nsysinfo
        self.assertIsInstance(nsysinfo.ttylib(), Module)

class TestNtable(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.ntable."""

    module = 'nemoa.core.ntable'

    def test_addcols(self) -> None:
        from nemoa.core import ntable
        from typing import cast
        import numpy as np
        tgt = np.array(
            [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        src = np.array(
            [('a'), ('b')], dtype=[('z', 'U4')])
        self.assertEqual(
            cast(Any, ntable.addcols(tgt, src, 'z'))['z'][0], 'a')

class TestNtext(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.ntext."""

    module = 'nemoa.core.ntext'

    def test_splitargs(self) -> None:
        from nemoa.core import ntext
        self.assertEqual(
            ntext.splitargs("f(1., 'a', b = 2)"),
            ('f', (1.0, 'a'), {'b': 2}))

    def test_aspath(self) -> None:
        from nemoa.core import ntext
        val = ntext.aspath('a/b/c')
        self.assertEqual(val, Path('a/b/c'))
        val = ntext.aspath('a\\b\\c')
        self.assertEqual(val, Path('a\\b\\c'))
        val = ntext.aspath('%home%/test')
        self.assertEqual(val, Path.home() / 'test')

    def test_aslist(self) -> None:
        from nemoa.core import ntext
        val = ntext.aslist('a, 2, ()')
        self.assertEqual(val, ['a', '2', '()'])
        val = ntext.aslist('[1, 2, 3]')
        self.assertEqual(val, [1, 2, 3])

    def test_astuple(self) -> None:
        from nemoa.core import ntext
        val = ntext.astuple('a, 2, ()')
        self.assertEqual(val, ('a', '2', '()'))
        val = ntext.astuple('(1, 2, 3)')
        self.assertEqual(val, (1, 2, 3))

    def test_asset(self) -> None:
        from nemoa.core import ntext
        val = ntext.asset('a, 2, ()')
        self.assertEqual(val, {'a', '2', '()'})
        val = ntext.asset('{1, 2, 3}')
        self.assertEqual(val, {1, 2, 3})

    def test_asdict(self) -> None:
        from nemoa.core import ntext
        val = ntext.asdict("a = 'b', b = 1")
        self.assertEqual(val, {'a': 'b', 'b': 1})
        val = ntext.asdict("'a': 'b', 'b': 1")
        self.assertEqual(val, {'a': 'b', 'b': 1})

    def test_astype(self) -> None:
        from nemoa.core import ntext
        tests = [
            ('t', 'str'), (True, 'bool'), (1, 'int'), (.5, 'float'),
            ((1+1j), 'complex')]
        for val, tname in tests:
            self.assertEqual(ntext.astype(str(val), tname), val)

class TestNpath(ntest.ModuleTestCase):
    """Testcase for the module nemoa.core.npath."""

    module = 'nemoa.core.npath'

    def test_cwd(self) -> None:
        from nemoa.core import npath
        self.assertTrue(Path(npath.cwd()).is_dir())

    def test_home(self) -> None:
        from nemoa.core import npath
        self.assertTrue(Path(npath.home()).is_dir())

    def test_clear(self) -> None:
        from nemoa.core import npath
        self.assertEqual(npath.clear('3/\nE{$5}.e'), '3E5.e')

    def test_match(self) -> None:
        from nemoa.core import npath
        from typing import cast
        paths = cast(Any, [Path('a.b'), Path('b.a'), Path('c/a.b')])
        self.assertEqual(
            npath.match(paths, 'a.*'), [Path('a.b')])
        self.assertEqual(
            npath.match(paths, '*.a'), [Path('b.a')])
        self.assertEqual(
            npath.match(paths, 'c\\*'), [Path('c/a.b')])
        self.assertEqual(
            npath.match(paths, 'c/*'), [Path('c/a.b')])

    def test_join(self) -> None:
        from nemoa.core import npath
        val = npath.join(('a', ('b', 'c')), 'd')
        self.assertEqual(val, Path('a/b/c/d'))

    def test_expand(self) -> None:
        from nemoa.core import npath
        udict = {'var1': 'a/%var2%', 'var2': 'b'}
        val = npath.expand('%var1%/c', 'd', udict=udict)
        self.assertEqual(val, str(Path('a/b/c/d')))

    def test_dirname(self) -> None:
        from nemoa.core import npath
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.dirname(*path)
        self.assertEqual(val, str(Path('a/b/c/d')))

    def test_filename(self) -> None:
        from nemoa.core import npath
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.filename(*path)
        self.assertEqual(val, 'base.ext')

    def test_basename(self) -> None:
        from nemoa.core import npath
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.basename(*path)
        self.assertEqual(val, 'base')

    def test_fileext(self) -> None:
        from nemoa.core import npath
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = npath.fileext(*path)
        self.assertEqual(val, 'ext')

    def test_mkdir(self) -> None:
        from nemoa.core import npath
        tempdir = Path(tempfile.TemporaryDirectory().name)
        npath.mkdir(tempdir)
        self.assertTrue(tempdir.is_dir())
        tempdir.rmdir()

    def test_isdir(self) -> None:
        from nemoa.core import npath
        tempdir = Path(tempfile.TemporaryDirectory().name)
        tempdir.mkdir()
        self.assertTrue(npath.isdir(tempdir))
        tempdir.rmdir()
        self.assertFalse(npath.isdir(tempdir))

    def test_isfile(self) -> None:
        from nemoa.core import npath
        file = Path(tempfile.NamedTemporaryFile().name)
        file.touch()
        self.assertTrue(npath.isfile(file))
        file.unlink()
        self.assertFalse(npath.isfile(file))

    def test_rmdir(self) -> None:
        from nemoa.core import npath
        tempdir = Path(tempfile.TemporaryDirectory().name)
        tempdir.mkdir()
        npath.rmdir(tempdir)
        self.assertFalse(tempdir.is_dir())

        # with self.subTest("cp"):
        #     self.assertTrue(True)
