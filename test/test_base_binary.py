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
"""Unittests for module 'nemoa.base.binary'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import binary
import test

#
# Test Cases
#

class TestBinary(test.ModuleTest):
    module = binary

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
        cases = [(o1, None, None), (o2, None, None), (o3, None, None)]
        for obj, enc, comp in cases:
            data = binary.pack(obj, encoding=enc, compression=comp)
            iscomp = isinstance(comp, int)
            self.assertEqual(binary.unpack(data, compressed=iscomp), obj)
