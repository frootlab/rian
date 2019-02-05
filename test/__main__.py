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
import os
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

import test
from nemoa.base import env, pkg
from nemoa.core import ui

#
# Public Module Functions
#

def main() -> None:
    """Launch unittests."""
    argv = sys.argv[1:]
    module = argv[0] if argv else None

    ui.info(f"testing nemoa {env.get_var('version')}")
    cur_level = ui.get_notification_level()
    ui.set_notification_level('CRITICAL')

    # Search and filter TestCases
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    cases = pkg.search(
        module=test, classinfo=unittest.TestCase, val='reference', errors=True)
    for ref in cases.values():
        if module:
            if not hasattr(ref, 'module'):
                continue
            if not hasattr(ref.module, '__name__'):
                continue
            if not fnmatch.fnmatch(ref.module.__name__, f'*{module}*'):
                continue
        suite.addTests(loader.loadTestsFromTestCase(ref))

    # Initialize TestRunner and run TestCases
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2)
    try:
        runner.run(suite)
    finally:
        ui.set_notification_level(cur_level)

if __name__ == "__main__":
    main()
