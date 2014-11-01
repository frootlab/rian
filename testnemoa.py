import unittest
import sys
sys.path.append('./package')
import nemoa

class TestNemoa(unittest.TestCase):

    def setUp(self):
        pass

    def test_list_workspaces(self):
        self.assertEqual(1, 1)

    def test_list_workspaces2(self):
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
