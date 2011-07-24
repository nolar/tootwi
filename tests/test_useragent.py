#!/usr/bin/env python
import unittest2 as unittest
import os, sys, contextlib

FAKE_OPERATION = ('GET', '/nowhere/')


class UserAgentAutomaticGenerationTest(unittest.TestCase):
    """
    This testcase tests User-Agent generation depending on presence or absence
    of version file, which is usually generated with setup.py & version.py.
    
    The class tries to preserve original version file and to restore it when
    the tests have finished. In case of unexpected error (OS level usually),
    it could happen so that original version file is deleted or replaced with
    test content. To restore it, call `setup.py version`.
    
    Because of the complexity of surrounding routines, these tests are moved
    to separate testcase class, far away from usual API class tests.
    """
    
    def setUp(self):
        # We have to import the module/package first to find its path, since
        # it can be anywhere on the sys.path, not only in our paent folder.
        import tootwi
        self.version_file_path   = os.path.join(os.path.dirname(tootwi.__file__), '_version.py')
        self.version_file_binary = os.path.join(os.path.dirname(tootwi.__file__), '_version.pyc')
        self.version_file_exists = os.path.exists(self.version_file_path)
        self.version_file_backup = None
    
    def unloadModules(self):
        """
        Unload the related modules and clear the cache. They could be loaded either
        in the setUp() for path retrieval, or somewhere else in this script(!) run.
        """
        for name in filter(lambda s: s.startswith('tootwi'), sys.modules.keys()):
            del sys.modules[name]
    
    def removeVersionFile(self):
        if os.path.exists(self.version_file_path):
            self.version_file_backup = '%s.testbackup' % self.version_file_path
            while os.path.exists(self.version_file_backup):
                self.version_file_backup += '~'
            os.rename(self.version_file_path, self.version_file_backup)
            if os.path.exists(self.version_file_binary):
                os.unlink(self.version_file_binary)
    
    def replaceVersionFile(self, content):
        self.removeVersionFile()
        with contextlib.closing(file(self.version_file_path, 'w')) as f:
            f.write(content)
        
    def tearDown(self):
        # If we have version file, but it was not present initially, or is replaced, then unlink curent one.
        if os.path.exists(self.version_file_path) and (not self.version_file_exists or self.version_file_backup):
            os.unlink(self.version_file_path)
            if os.path.exists(self.version_file_binary):
                os.unlink(self.version_file_binary)
        
        # Restore version file from backup, if present.
        if self.version_file_backup is not None:
            os.rename(self.version_file_backup, self.version_file_path)
    
    def test_user_agent_with_original_version_file_if_present(self):
        try:
            from tootwi._version import __version__ as expected_version
        except ImportError:
            return # skip
        
        import tootwi
        api = tootwi.API()
        invocation = api.invoke(FAKE_OPERATION)
        self.assertIn('User-Agent', invocation.headers)
        self.assertEqual('tootwi/' + expected_version, invocation.headers['User-Agent'])
    
    def test_user_agent_when_version_file_absents(self):
        self.removeVersionFile()
        self.unloadModules()
        import tootwi
        api = tootwi.API()
        invocation = api.invoke(FAKE_OPERATION)
        self.assertIn('User-Agent', invocation.headers)
        self.assertEqual('tootwi/unknown', invocation.headers['User-Agent'])
    
    def test_user_agent_when_version_file_presents(self):
        self.replaceVersionFile("__version__='test'")
        self.unloadModules()
        import tootwi
        api = tootwi.API()
        invocation = api.invoke(FAKE_OPERATION)
        self.assertIn('User-Agent', invocation.headers)
        self.assertEqual('tootwi/test', invocation.headers['User-Agent'])


class UserAgentCaseInsensitivityTest(unittest.TestCase):
    """
    Here we test that API can work with any User-Agent header,
    no matter if it is lower-, upper-, mixed or camel-cased.
    """
    
    def common_user_agent_test(self, user_agent_key):
        from tootwi import API
        user_agent_val = 'test-user-agent/1.2.3'
        tootwi_own_val = 'tootwi/'
        api = API(headers={ user_agent_key: user_agent_val })
        invocation = api.invoke(FAKE_OPERATION)
        self.assertIn(user_agent_key, invocation.headers)
        self.assertIn(user_agent_val, invocation.headers[user_agent_key])
        self.assertIn(tootwi_own_val, invocation.headers[user_agent_key])
    
    def test_user_agent_with_no_key(self):
        from tootwi import API
        user_agent_key = 'User-Agent' # default expected
        tootwi_own_val = 'tootwi/'
        api = API()
        invocation = api.invoke(FAKE_OPERATION)
        self.assertIn(user_agent_key, invocation.headers)
        self.assertIn(tootwi_own_val, invocation.headers[user_agent_key])
    
    def test_user_agent_with_mixedcase_key(self):
        self.common_user_agent_test('User-Agent')
    
    def test_user_agent_with_lowercase_key(self):
        self.common_user_agent_test('user-agent')
    
    def test_user_agent_with_uppercase_key(self):
        self.common_user_agent_test('USER-AGENT')


if __name__ == '__main__':
    unittest.main()
