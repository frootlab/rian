# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

_WORKSPACE = None

def main(workspace, *args, **kwargs):
    _WORKSPACE = workspace

    # initialize the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    try: import nemoa.session.__test__
    except ImportError: pass
    else: suite.addTests(loader.loadTestsFromModule(nemoa.session.__test__))
    try: import nemoa.dataset.__test__
    except ImportError: pass
    else: suite.addTests(loader.loadTestsFromModule(nemoa.dataset.__test__))
    try: import nemoa.network.__test__
    except ImportError: pass
    else: suite.addTests(loader.loadTestsFromModule(nemoa.network.__test__))
    try: import nemoa.system.__test__
    except ImportError: pass
    else: suite.addTests(loader.loadTestsFromModule(nemoa.system.__test__))
    try: import nemoa.model.__test__
    except ImportError: pass
    else: suite.addTests(loader.loadTestsFromModule(nemoa.model.__test__))

    # initialize a runner, pass it your suite and run it
    nemoa.log('testing nemoa ' + nemoa.__version__)
    runner = unittest.TextTestRunner(verbosity = 2)
    result = runner.run(suite)

    return result
