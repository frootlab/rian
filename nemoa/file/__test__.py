# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.file'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
import tempfile
from pathlib import Path
import numpy as np
from nemoa.file import binfile, csv, ini, textfile
from nemoa.test import ModuleTestCase
from nemoa.types import List

class TestBinfile(ModuleTestCase):
    """Testcase for the module nemoa.file.binfile."""

    module = 'nemoa.file.binfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.gz')
        self.data = b'eJxrYK4tZDoiGBkGT0ZqotZJzt3/AbFpXoAgyI=='
        binfile.save(self.data, self.filepath)

    def test_openx(self) -> None:
        filepath = Path(tempfile.NamedTemporaryFile().name)
        with self.subTest(file=filepath):
            with binfile.openx(filepath, mode='w') as fh:
                fh.write(self.data)
            if filepath.is_file():
                with binfile.openx(filepath, mode='r') as fh:
                    data = fh.read()
                filepath.unlink()
                self.assertTrue(data == self.data)
        file = filepath.open(mode='wb')
        with self.subTest(file=file):
            with binfile.openx(file, mode='w') as fh:
                fh.write(self.data)
            if not file.closed:
                file.close()
                file = filepath.open(mode='rb')
                with binfile.openx(file, mode='r') as fh:
                    data = fh.read()
                if not file.closed:
                    file.close()
                    self.assertTrue(data == self.data)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        data = binfile.load(self.filepath)
        self.assertEqual(data, self.data)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestTextfile(ModuleTestCase):
    """Testcase for the module nemoa.file.textfile."""

    module = 'nemoa.file.textfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.txt')
        self.comment = "comment line"
        self.content = ['first content line', 'second content line']
        self.text = f"# {self.comment}\n\n" + '\n'.join(self.content)
        textfile.save(self.text, self.filepath)

    def test_openx(self) -> None:
        filepath = Path(tempfile.NamedTemporaryFile().name + '.txt')
        with self.subTest(file=filepath):
            with textfile.openx(filepath, mode='w') as fh:
                fh.write(self.text)
            if filepath.is_file():
                with textfile.openx(filepath, mode='r') as fh:
                    text = fh.read()
                filepath.unlink()
                self.assertTrue(text == self.text)
        file = filepath.open(mode='w')
        with self.subTest(file=file):
            with textfile.openx(file, mode='w') as fh:
                fh.write(self.text)
            if not file.closed:
                file.close()
                file = filepath.open(mode='r')
                with textfile.openx(file, mode='r') as fh:
                    text = fh.read()
                if not file.closed:
                    file.close()
                    self.assertTrue(text == self.text)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        text = textfile.load(self.filepath)
        self.assertEqual(text, self.text)

    def test_get_comment(self) -> None:
        comment = textfile.get_comment(self.filepath)
        self.assertEqual(comment, self.comment)

    def test_get_content(self) -> None:
        content = textfile.get_content(self.filepath)
        self.assertEqual(content, self.content)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestCsv(ModuleTestCase):
    """Testcase for the module nemoa.file.csv."""

    module = 'nemoa.file.csv'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.csv')
        self.comment = '-*- coding: utf-8 -*-'
        self.header = ('name', 'x', 'y')
        self.delimiter = ','
        self.values = [('row1', 1, 1.), ('row2', 2, 2.), ('row3', 3, 3.)]

        self.data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        self.rownames = list(self.data['label'].flat)
        csv.save_old(
            self.filepath, self.data, header=self.header,
            comment=self.comment, delimiter=self.delimiter)
        self.file = csv.File(self.filepath)

    def test_File(self) -> None:
        filepath = Path(tempfile.NamedTemporaryFile().name + '.csv')
        comment = '-*- coding: utf-8 -*-'
        header = ('name', 'id', 'value')
        delimiter = ','
        values: List[tuple] = [('r1', 1, 1.), ('r2', 2, 2.), ('r3', 3, 3.)]

        with self.subTest(method=csv.File.__init__):
            file = csv.File(
                filepath, header=header, comment=comment, delimiter=delimiter)
            self.assertIsInstance(file, csv.File)
        with self.subTest(method=csv.File.write):
            file.write(values)
            self.assertTrue(filepath.is_file())
            file.close()
            file = csv.File(filepath)
        with self.subTest(method=csv.File.delimiter):
            self.assertEqual(file.delimiter, delimiter)
        with self.subTest(method=csv.File.header):
            self.assertEqual(file.header, header)
        with self.subTest(method=csv.File.comment):
            self.assertEqual(file.comment, comment)
            file.close()
        filepath.unlink()

    def test_Reader(self) -> None:
        pass

    def test_Writer(self) -> None:
        pass

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_comment(self) -> None:
        self.assertEqual(self.file.comment, self.comment)

    def test_delim(self) -> None:
        self.assertEqual(self.file.delimiter, self.delimiter)

    def test_header(self) -> None:
        self.assertEqual(self.file.header, self.header)

    def test_hformat(self) -> None:
        self.assertEqual(self.file.hformat, csv.CSV_HFORMAT_RFC4180)

    def test_rownames(self) -> None:
        self.assertEqual(self.file.rownames, self.rownames)

    def test_namecol(self) -> None:
        self.assertEqual(self.file.namecol, 0)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()
        pass

class TestInifile(ModuleTestCase):
    """Testcase for the module nemoa.file.ini."""

    module = 'nemoa.file.ini'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.ini')
        self.comment = '-*- coding: utf-8 -*-'
        self.obj = {
            'n': {'a': 's', 'b': True, 'c': 1},
            'l1': {'a': 1}, 'l2': {'a': 2}}
        self.structure = {
            'n': {'a': str, 'b': bool, 'c': int},
            'l[0-9]*': {'a': int}}
        self.text = (
            "# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")
        ini.save(self.obj, self.filepath, comment=self.comment)

    def test_parse(self) -> None:
        parser = ConfigParser()
        setattr(parser, 'optionxform', lambda key: key)
        parser.read_string(self.text)
        obj = ini.parse(parser, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_encode(self) -> None:
        text = ini.encode(self.obj, comment=self.comment)
        self.assertEqual(text, self.text)

    def test_decode(self) -> None:
        obj = ini.decode(self.text, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        obj = ini.load(self.filepath, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_get_comment(self) -> None:
        comment = ini.get_comment(self.filepath)
        self.assertEqual(comment, self.comment)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()
