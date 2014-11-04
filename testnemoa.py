import unittest
import sys
sys.path.append('./package')
import nemoa

class NemoaTestCase(unittest.TestCase):

    def setUp(self):
        nemoa.log('set', mode = 'silent')
        self.workspace = nemoa.open('unittest')
        pass

    def test_list_workspaces(self):
        nemoa.log('set', mode = 'silent')
        workspaces = nemoa.workspaces()
        test = isinstance(workspaces, list)
        self.assertTrue(test)

    def test_dataset_import_tab(self):
        test = nemoa.type.is_dataset(nemoa.dataset.open('test'))
        self.assertTrue(test)

    def test_network_import_ini(self):
        test = nemoa.type.is_network(nemoa.network.open('multilayer'))
        self.assertTrue(test)

    def test_system_import_ini(self):
        test = nemoa.type.is_system(nemoa.system.open('dbn'))
        self.assertTrue(test)

    def test_model_create_dbn(self):
        model = nemoa.model.create(
            dataset = 'test', network = 'multilayer', system = 'dbn')
        test = nemoa.type.is_model(model)
        self.assertTrue(test)

    def test_model_import_npz(self):
        test = nemoa.type.is_model(nemoa.model.open('test'))
        self.assertTrue(test)

if __name__ == '__main__':
    unittest.main()
