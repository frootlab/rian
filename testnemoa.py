import unittest
import sys
sys.path.append('./package')
import nemoa

class TestNemoa(unittest.TestCase):

    def setUp(self):
        pass

    def test_list_workspaces(self):
        nemoa.log('set', mode = 'silent')
        workspaces = nemoa.workspaces()
        test = isinstance(workspaces, list)
        self.assertEqual(test, True)

    def test_dataset_import_tab(self):
        nemoa.log('set', mode = 'silent')
        workspace = nemoa.open('unittest')
        test = nemoa.type.is_dataset(nemoa.dataset.open('test'))
        self.assertEqual(test, True)

    def test_network_import_ini(self):
        nemoa.log('set', mode = 'silent')
        workspace = nemoa.open('unittest')
        test = nemoa.type.is_network(nemoa.network.open('test'))
        self.assertEqual(test, True)

    def test_model_import_npz(self):
        nemoa.log('set', mode = 'silent')
        workspace = nemoa.open('unittest')
        test = nemoa.type.is_model(nemoa.model.open('test'))
        self.assertEqual(test, True)

    def test_model_create_dbn(self):
        nemoa.log('set', mode = 'silent')
        workspace = nemoa.open('unittest')
        model = nemoa.model.create(
            dataset = 'test', network = 'test', system = 'dbn')
        test = nemoa.type.is_model(model)
        self.assertEqual(test, True)

if __name__ == '__main__':
    unittest.main()
