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

import fnmatch
import io
import os

import unittest
import sys
from typing import IO, Optional, Tuple, Union

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

import tests

from nemoa.base import env, pkg
from nemoa.core import ui

ClassInfo = Union[type, Tuple[type, ...]]

def run(
        module: Optional[str] = None, classinfo: ClassInfo = unittest.TestCase,
        stream: IO[str] = io.StringIO(),
        verbosity: int = 2) -> unittest.TestResult:
    """Search and run Unittest."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    cases = pkg.search(module=tests, classinfo=classinfo, val='reference')
    for ref in cases.values():
        if module:
            if not hasattr(ref, 'module'):
                continue
            if not hasattr(ref.module, '__name__'):
                continue
            if not fnmatch.fnmatch(ref.module.__name__, f'*{module}*'):
                continue
        suite.addTests(loader.loadTestsFromTestCase(ref))
    return unittest.TextTestRunner( # type: ignore
        stream=stream, verbosity=verbosity).run(suite)

def main() -> None:
    """Launch unittests."""
    argv = sys.argv[1:]
    if argv:
        module = argv[0]
    else:
        module = None

    ui.info(f"testing nemoa {env.get_var('version')}")
    cur_level = ui.get_notification_level()
    ui.set_notification_level('CRITICAL')
    try:
        run(module=module, stream=sys.stderr)
    finally:
        ui.set_notification_level(cur_level)

if __name__ == "__main__":
    main()
