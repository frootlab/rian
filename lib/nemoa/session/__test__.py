# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.mode = nemoa.get('mode')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        nemoa.set('mode', self.mode)

    def test_nemoa_config_about(self):
        test = isinstance(nemoa.about(), str)
        self.assertTrue(test)

    def test_nemoa_config_about_about(self):
        test = isinstance(nemoa.about('about'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_version(self):
        test = isinstance(nemoa.about('version'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_status(self):
        test = isinstance(nemoa.about('status'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_description(self):
        test = isinstance(nemoa.about('description'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_url(self):
        test = isinstance(nemoa.about('url'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_license(self):
        test = isinstance(nemoa.about('license'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_copyright(self):
        test = isinstance(nemoa.about('copyright'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_author(self):
        test = isinstance(nemoa.about('author'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_email(self):
        test = isinstance(nemoa.about('email'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_maintainer(self):
        test = isinstance(nemoa.about('maintainer'), str)
        self.assertTrue(test)

    def test_nemoa_config_about_credits(self):
        test = isinstance(nemoa.about('credits'), list)
        self.assertTrue(test)

    def test_nemoa_config_get_base(self):
        test = isinstance(nemoa.get('base'), str)
        self.assertTrue(test)

    def test_nemoa_config_get_default(self):
        test = isinstance(nemoa.get('default'), dict)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype(self):
        test = isinstance(nemoa.get('default', 'filetype'), dict)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype_dataset(self):
        filetype = nemoa.get('default', 'filetype', 'dataset')
        test = isinstance(filetype, str)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype_network(self):
        filetype = nemoa.get('default', 'filetype', 'network')
        test = isinstance(filetype, str)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype_system(self):
        filetype = nemoa.get('default', 'filetype', 'system')
        test = isinstance(filetype, str)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype_model(self):
        filetype = nemoa.get('default', 'filetype', 'model')
        test = isinstance(filetype, str)
        self.assertTrue(test)

    def test_nemoa_config_get_default_filetype_script(self):
        filetype = nemoa.get('default', 'filetype', 'script')
        test = isinstance(filetype, str)
        self.assertTrue(test)

    def test_nemoa_config_get_workspace(self):
        test = isinstance(nemoa.get('workspace'), str)
        self.assertTrue(test)

    def test_nemoa_config_list_bases(self):
        test = 'user' in nemoa.list('bases')
        self.assertTrue(test)

    def test_nemoa_config_list_workspaces(self):
        worktree = nemoa.list('workspaces')
        test = isinstance(worktree, dict) \
            and 'user' in worktree \
            and 'common' in worktree \
            and 'cwd' in worktree
        self.assertTrue(test)

    def test_nemoa_config_list_workspaces_common(self):
        workspaces = nemoa.list('workspaces', base = 'common')
        test = isinstance(workspaces, list)
        self.assertTrue(test)

    def test_nemoa_config_list_workspaces_user(self):
        workspaces = nemoa.list('workspaces', base = 'user')
        test = isinstance(workspaces, list) \
            and 'testsuite' in workspaces
        self.assertTrue(test)

    def test_nemoa_config_list_datasets(self):
        datasets = nemoa.list('datasets')
        test = isinstance(datasets, list) \
            and 'linear' in datasets \
            and 'logistic' in datasets \
            and 'sinus' in datasets
        self.assertTrue(test)

    def test_nemoa_config_list_networks(self):
        networks = nemoa.list('networks')
        test = isinstance(networks, list) \
            and 'deep' in networks \
            and 'shallow' in networks
        self.assertTrue(test)

    def test_nemoa_config_list_systems(self):
        systems = nemoa.list('systems')
        test = isinstance(systems, list) \
            and 'ann' in systems \
            and 'dbn' in systems \
            and 'grbm' in systems \
            and 'rbm' in systems
        self.assertTrue(test)

    def test_nemoa_config_list_models(self):
        models = nemoa.list('models')
        test = isinstance(models, list) and 'test' in models
        self.assertTrue(test)

    def test_nemoa_config_list_scripts(self):
        scripts = nemoa.list('scripts')
        test = isinstance(scripts, list) and 'unittest' in scripts
        self.assertTrue(test)

    def test_nemoa_config_path_basepath(self):
        test = isinstance(nemoa.path('basepath'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_baseconf(self):
        test = isinstance(nemoa.path('baseconf'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_datasets(self):
        test = isinstance(nemoa.path('datasets'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_networks(self):
        test = isinstance(nemoa.path('networks'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_systems(self):
        test = isinstance(nemoa.path('systems'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_models(self):
        test = isinstance(nemoa.path('models'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_scripts(self):
        test = isinstance(nemoa.path('scripts'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_cache(self):
        test = isinstance(nemoa.path('cache'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_inifile(self):
        test = isinstance(nemoa.path('inifile'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_logfile(self):
        test = isinstance(nemoa.path('logfile'), str)
        self.assertTrue(test)

    def test_nemoa_config_path_dataset(self):
        objtype = 'dataset'
        names = nemoa.list(objtype + 's')
        test = True
        for name in names:
            path = nemoa.path(objtype, name)
            test &= isinstance(path, str)
            if not test: break
        self.assertTrue(test)

    def test_nemoa_config_path_network(self):
        objtype = 'network'
        names = nemoa.list(objtype + 's')
        test = True
        for name in names:
            path = nemoa.path(objtype, name)
            test &= isinstance(path, str)
            if not test: break
        self.assertTrue(test)

    def test_nemoa_config_path_system(self):
        objtype = 'system'
        names = nemoa.list(objtype + 's')
        test = True
        for name in names:
            path = nemoa.path(objtype, name)
            test &= isinstance(path, str)
            if not test: break
        self.assertTrue(test)

    def test_nemoa_config_path_model(self):
        objtype = 'model'
        names = nemoa.list(objtype + 's')
        test = True
        for name in names:
            path = nemoa.path(objtype, name)
            test &= isinstance(path, str)
            if not test: break
        self.assertTrue(test)

    def test_nemoa_config_path_script(self):
        objtype = 'script'
        names = nemoa.list(objtype + 's')
        test = True
        for name in names:
            path = nemoa.path(objtype, name)
            test &= isinstance(path, str)
            if not test: break
        self.assertTrue(test)

    def test_nemoa_config_path_expand(self):
        valid = nemoa.path('expand', '%basepath%', '%workspace%',
            check = True)
        invalid = nemoa.path('expand', '%basepath%', '%workspace%',
            'invalid_path_name', check = True)
        test = valid and not invalid
        self.assertTrue(test)
