# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import tempfile
from pathlib import Path

from nemoa.core import ntest

class TestCase(ntest.TestCase):
    """Testsuite for modules within the package 'nemoa.core'."""

    def test_core_napp(self) -> None:
        """Test module 'nemoa.core.napp'."""
        from nemoa.core import napp

        dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        for key in dirs:
            with self.subTest(f"get_dir('{key}')"):
                self.assertTrue(napp.get_dir(key))

        for key in ['name', 'author', 'version', 'license']:
            with self.subTest(f"get_var('{key}')"):
                self.assertTrue(napp.get_var(key))

    def test_core_narray(self) -> None:
        """Test module 'nemoa.core.narray'."""
        from nemoa.core import narray
        from nemoa.types import NaN
        import numpy as np

        arr = np.array([[NaN, 1.], [NaN, NaN]])
        dic = {('a', 'b'): 1.}
        labels = (['a', 'b'], ['a', 'b'])

        with self.subTest("from_dict"):
            self.assertTrue(
                np.allclose(
                    narray.from_dict(dic, labels=labels), arr,
                    equal_nan=True))

        with self.subTest("asdict"):
            self.assertTrue(
                narray.as_dict(arr, labels=labels) == {('a', 'b'): 1.})

    def test_core_nbase(self) -> None:
        """Test module 'nemoa.core.nbase'."""
        from nemoa.core import nbase

        with self.subTest("ObjectIP"):
            obj = nbase.ObjectIP()
            obj.name = 'test'
            self.assertTrue(
                obj.get('config') == {'name': 'test'})
            obj.path = ('%site_data_dir%', 'test')
            self.assertNotIn('%', obj.path)

    def test_core_nbytes(self) -> None:
        """Test module 'nemoa.core.bytes'."""
        from nemoa.core import nbytes

        with self.subTest('compress'):
            self.assertEqual(
                nbytes.compress(b'test', level=0),
                b'x\x01\x01\x04\x00\xfb\xfftest\x04]\x01\xc1')
            self.assertEqual(
                nbytes.compress(b'test', level=1),
                b'x\x01+I-.\x01\x00\x04]\x01\xc1')
            self.assertEqual(
                nbytes.compress(b'test', level=9),
                b'x\xda+I-.\x01\x00\x04]\x01\xc1')

        with self.subTest('decompress'):
            for level in range(-1, 10):
                self.assertEqual(
                    nbytes.decompress(
                        nbytes.compress(b'test', level=level)),
                    b'test')

        with self.subTest('encode'):
            self.assertEqual(
                nbytes.encode(b'test', encoding='base64'),
                b'dGVzdA==')
            self.assertEqual(
                nbytes.encode(b'test', encoding='base32'),
                b'ORSXG5A=')
            self.assertEqual(
                nbytes.encode(b'test', encoding='base16'),
                b'74657374')

        with self.subTest('decode'):
            for encoding in ['base64', 'base32', 'base16', 'base85']:
                data = nbytes.encode(b'test', encoding=encoding)
                self.assertEqual(
                    nbytes.decode(data, encoding=encoding), b'test')

        with self.subTest('pack'):
            self.assertEqual(
                nbytes.pack({True: 1}, encoding='base64'),
                b'gAN9cQCISwFzLg==')
            self.assertEqual(
                nbytes.pack(None, encoding='base32'),
                b'QABU4LQ=')
            self.assertEqual(
                nbytes.pack(True, encoding='base16', compression=9),
                b'78DA6B60EED00300034B013A')

        with self.subTest('unpack'):
            o1 = None
            o2 = [None, True, 1, .0, 1+1j, 'a', b'b', type]
            o3 = {True: 1, 'a': [.5, (1j, ), None]}
            tests = [
                (o1, None, None), (o2, None, None), (o3, None, None)]
            for obj, enc, comp in tests:
                data = nbytes.pack(obj, encoding=enc, compression=comp)
                iscomp = isinstance(comp, int)
                self.assertEqual(nbytes.unpack(data, compressed=iscomp), obj)

    def test_core_nconsole(self) -> None:
        """Test module 'nemoa.core.nconsole'."""
        from nemoa.core import nconsole

        with self.subTest("Getch"):
            Ref = nconsole.Getch
            obj = Ref() if callable(Ref) else None
            self.assertIsInstance(obj, nconsole.GetchBase)

    def test_core_nclass(self) -> None:
        """Test module 'nemoa.core.nclass'."""
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
        obj = Base()

        with self.subTest('hasbase'):
            self.assertTrue(nclass.hasbase(None, 'object'))
            self.assertTrue(nclass.hasbase(obj, 'Base'))

        with self.subTest('attributes'):
            self.assertEqual(getattr(obj.geta, 'name', None), 'a')
            self.assertEqual(getattr(obj.getb, 'name', None), 'b')

        with self.subTest('methods'):
            self.assertEqual(
                nclass.methods(obj, pattern='get*').keys(), {'geta', 'getb'})
            self.assertEqual(
                nclass.methods(obj, pattern='*b').keys(), {'getb', 'setb'})

    def test_core_nmodule(self) -> None:
        """Test module 'nemoa.core.nmodule'."""
        from nemoa.core import nmodule
        from nemoa.types import Module
        from typing import cast

        with self.subTest("curname"):
            self.assertEqual(nmodule.curname(), __name__)

        with self.subTest("caller"):
            self.assertEqual(
                nmodule.caller(), __name__ + '.test_core_nmodule')

        with self.subTest("submodules"):
            self.assertIn(
                nmodule.__name__,
                nmodule.submodules(nmodule.inst('nemoa.core')))

        with self.subTest("inst"):
            self.assertTrue(
                hasattr(
                    nmodule.inst(nmodule.__name__), '__name__'))
            self.assertEqual(
                cast(Module, nmodule.inst(nmodule.__name__)).__name__,
                nmodule.__name__)

        with self.subTest('get_functions'):
            func = nmodule.get_functions
            name = func.__name__
            fullname = func.__module__ + '.' + name
            self.assertIn(
                fullname, nmodule.get_functions(nmodule))
            self.assertEqual(
                len(nmodule.get_functions(nmodule, name='')), 0)
            self.assertEqual(
                len(nmodule.get_functions(nmodule, name=name)), 1)

        with self.subTest('search'):
            self.assertEqual(
                len(nmodule.search(nmodule, name='search')), 1)

    def test_core_nfunc(self) -> None:
        """Test module 'nemoa.core.nfunc'."""
        from nemoa.core import nfunc

        with self.subTest("about"):
            self.assertEqual(
                nfunc.about(nfunc.about),
                'Summary line of docstring of a function')

        with self.subTest("inst"):
            self.assertEqual(
                type(nfunc.inst(nfunc.__name__ + '.inst')).__name__,
                'function')

        with self.subTest("kwds"):
            self.assertEqual(
                nfunc.kwds(nfunc.kwds), {'default': None})
            self.assertEqual(
                nfunc.kwds(nfunc.kwds, default={}), {})
            self.assertEqual(
                nfunc.kwds(nfunc.kwds, default={'default': True}),
                {'default': True})

    def test_core_ndict(self) -> None:
        """Test module 'nemoa.core.ndict'."""
        from nemoa.core import ndict

        with self.subTest("select"):
            self.assertTrue(
                ndict.select({'a1': 1, 'a2': 2, 'b1': 3}, pattern='a*') \
                == {'a1': 1, 'a2': 2})

        with self.subTest("groupby"):
            self.assertEqual(
                ndict.groupby(
                    {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a'),
                {
                    0: {1: {'a': 0}, 2: {'a': 0}},
                    1: {3: {'a': 1}}, None: {4: {}}})

        with self.subTest("flatten"):
            self.assertEqual(
                ndict.flatten({1: {'a': {}}, 2: {'b': {}}}),
                {'a': {}, 'b': {}})
            self.assertEqual(
                ndict.flatten({1: {'a': {}}, 2: {'b': {}}}, group='id'),
                {'a': {'id': 1}, 'b': {'id': 2}})

        with self.subTest("merge"):
            self.assertEqual(
                ndict.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3}),
                {'a': 1, 'b': 2, 'c': 3})

        with self.subTest("crop"):
            self.assertEqual(
                ndict.crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a'),
                {'1': 1, '2': 2})

        with self.subTest("strkeys"):
            self.assertEqual(
                ndict.strkeys({(1, 2): 3, None: {True: False}}),
                {('1', '2'): 3, 'None': {'True': False}})

        with self.subTest("sumjoin"):
            self.assertEqual(
                ndict.sumjoin({'a': 1}, {'a': 2, 'b': 3}), {'a': 3, 'b': 3})
            self.assertEqual(
                ndict.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True}),
                {1: 'ab', 2: 2})

    def test_core_npath(self) -> None:
        """Test module 'nemoa.core.npath'."""
        from nemoa.core import npath

        from typing import cast, Any

        dpath = Path('a', 'b', 'c', 'd')
        dname = str(dpath)
        ptest = (('a', ('b', 'c')), 'd', 'base.ext')
        stdir = tempfile.TemporaryDirectory().name

        with self.subTest("cwd"):
            self.assertTrue(npath.cwd())

        with self.subTest("home"):
            self.assertTrue(npath.home())

        with self.subTest("clear"):
            self.assertEqual(npath.clear('3/\nE{$5}.e'), '3E5.e')

        with self.subTest("match"):
            paths = cast(Any, [Path('a.b'), Path('b.a'), Path('c/a.b')])
            self.assertEqual(
                npath.match(paths, 'a.*'), [Path('a.b')])
            self.assertEqual(
                npath.match(paths, '*.a'), [Path('b.a')])
            self.assertEqual(
                npath.match(paths, 'c\\*'), [Path('c/a.b')])
            self.assertEqual(
                npath.match(paths, 'c/*'), [Path('c/a.b')])

        with self.subTest("join"):
            self.assertEqual(npath.join(('a', ('b', 'c')), 'd'), dpath)

        with self.subTest("expand"):
            self.assertEqual(
                npath.expand(
                    '%var1%/c', 'd',
                    udict={'var1': 'a/%var2%', 'var2': 'b'}), dname)

        with self.subTest("dirname"):
            self.assertEqual(npath.dirname(*ptest), dname)

        with self.subTest("filename"):
            self.assertEqual(npath.filename(*ptest), 'base.ext')

        with self.subTest("basename"):
            self.assertEqual(npath.basename(*ptest), 'base')

        with self.subTest("fileext"):
            self.assertEqual(npath.fileext(*ptest), 'ext')

        with self.subTest("mkdir"):
            self.assertTrue(npath.mkdir(stdir))

        with self.subTest("isdir"):
            self.assertTrue(npath.isdir(stdir))

        with self.subTest("isfile"):
            self.assertFalse(npath.isfile(stdir))

        with self.subTest("rmdir"):
            self.assertTrue(npath.rmdir(stdir))

        # with self.subTest("cp"):
        #     self.assertTrue(True)

    def test_core_nsysinfo(self) -> None:
        """Test module 'nemoa.core.nsysinfo'."""
        from nemoa.core import nsysinfo

        from types import FunctionType, ModuleType
        ftypes = {
            'encoding': str,
            'hostname': str,
            'osname': str,
            'username': str,
            'ttylib': ModuleType}

        for fname, ftype in ftypes.items():
            with self.subTest(fname):
                func = getattr(nsysinfo, fname)
                # Check if function exists
                self.assertIsInstance(func, FunctionType)
                # Check type of returned value
                self.assertIsInstance(func(), ftype)

    def test_core_ntable(self) -> None:
        """Test module 'nemoa.core.ntable'."""
        from typing import cast
        from nemoa.core import ntable
        from nemoa.types import Any
        import numpy as np

        with self.subTest("addcols"):
            tgt = np.array(
                [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
            src = np.array(
                [('a'), ('b')], dtype=[('z', 'U4')])
            self.assertEqual(
                cast(Any, ntable.addcols(tgt, src, 'z'))['z'][0], 'a')

    def test_core_ntext(self) -> None:
        """Test module 'nemoa.core.ntext'."""
        from nemoa.core import ntext

        with self.subTest("splitargs"):
            self.assertEqual(
                ntext.splitargs("f(1., 'a', b = 2)"),
                ('f', (1.0, 'a'), {'b': 2}))

        with self.subTest("aspath"):
            self.assertEqual(ntext.aspath('a/b/c'), Path('a/b/c'))
            self.assertEqual(ntext.aspath('a\\b\\c'), Path('a\\b\\c'))
            self.assertEqual(
                ntext.aspath('%home%/test'),
                Path.home() / Path('test'))

        with self.subTest("aslist"):
            self.assertEqual(ntext.aslist('a, 2, ()'), ['a', '2', '()'])
            self.assertEqual(ntext.aslist('[1, 2, 3]'), [1, 2, 3])

        with self.subTest("astuple"):
            self.assertEqual(ntext.astuple('a, 2, ()'), ('a', '2', '()'))
            self.assertEqual(ntext.astuple('(1, 2, 3)'), (1, 2, 3))

        with self.subTest("asset"):
            self.assertEqual(ntext.asset('a, 2, ()'), {'a', '2', '()'})
            self.assertEqual(ntext.asset('{1, 2, 3}'), {1, 2, 3})

        with self.subTest("asdict"):
            self.assertEqual(
                ntext.asdict("a = 'b', b = 1"), {'a': 'b', 'b': 1})
            self.assertEqual(
                ntext.asdict("'a': 'b', 'b': 1"), {'a': 'b', 'b': 1})

        with self.subTest("astype"):
            examples = [
                ('t', 'str'), (True, 'bool'), (1, 'int'), (.5, 'float'),
                ((1+1j), 'complex')]
            for var, typ in examples:
                self.assertEqual(ntext.astype(str(var), typ), var)
