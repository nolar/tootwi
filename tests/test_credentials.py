#!/usr/bin/env python
import unittest2 as unittest

#
# Notes on these tests:
#
# call() and flow() methods involve network activity and are tested in scenarios.
# Here we test only pure protocols of the classes themselves. So we do not even
# need real credentials, but can use fake one, just strings.
#
# Test cases are very similar, since most functionality is in abstract parent classes,
# but classes has different constructor signatures. So instead of repeating ourselves,
# tests are organized into mix-ins and are combined into real test cases, which usually
# contain onl setUp() method (though they can contain class-specific tests too).
#

class CreationFailsWithoutConsumerMixin(object):
    def test_creation_fails_with_no_consumer(self):
        with self.assertRaises(TypeError):
            self.credentials_class()
    
    def test_creation_fails_with_no_consumer_key(self):
        with self.assertRaises(TypeError):
            self.credentials_class(consumer_secret='consumer_secret')
    
    def test_creation_fails_with_no_consumer_secret(self):
        with self.assertRaises(TypeError):
            self.credentials_class(consumer_key='consumer_key')


class CreationFailsWithoutTokenMixin(object):
    def test_creation_fails_with_no_token(self):
        with self.assertRaises(TypeError):
            self.credentials_class('consumer_key', 'consumer_secret')
    
    def test_creation_fails_with_no_token_key(self):
        with self.assertRaises(TypeError):
            self.credentials_class('consumer_key', 'consumer_secret', token_secret='token_secret')
    
    def test_creation_fails_with_no_token_secret(self):
        with self.assertRaises(TypeError):
            self.credentials_class('consumer_key', 'consumer_secret', token_key='token_key')


class CreationFailsWithoutUsernamePasswordMixin(object):
    def test_creation_fails_with_no_login(self):
        with self.assertRaises(TypeError):
            self.credentials_class()
    
    def test_creation_fails_with_no_username(self):
        with self.assertRaises(TypeError):
            self.credentials_class(password='password')
    
    def test_creation_fails_with_no_password(self):
        with self.assertRaises(TypeError):
            self.credentials_class(username='username')


class CreationWorksWithConsumerOnlyMixin(object):
    def create_credentials(self, *args, **kwargs): # also used for CommonCredentialsMixin
        self.credentials = self.credentials_class('consumer_key', 'consumer_secret', *args, **kwargs)
    
    def test_creation_with_consumer_only(self):
        self.create_credentials()
        self.assertEqual(self.credentials.consumer_key, 'consumer_key')
        self.assertEqual(self.credentials.consumer_secret, 'consumer_secret')


class CreationWorksWithConsumerAndTokenMixin(object):
    def create_credentials(self, *args, **kwargs): # also used for CommonCredentialsMixin
        self.credentials = self.credentials_class('consumer_key', 'consumer_secret', 'token_key', 'token_secret', *args, **kwargs)
    
    def test_creation_with_consumer_and_token(self):
        self.create_credentials()
        self.assertEqual(self.credentials.consumer_key, 'consumer_key')
        self.assertEqual(self.credentials.consumer_secret, 'consumer_secret')
        self.assertEqual(self.credentials.token_key, 'token_key')
        self.assertEqual(self.credentials.token_secret, 'token_secret')


class CreationWorksWithUsernamePasswordMixin(object):
    def create_credentials(self, *args, **kwargs): # also used for CommonCredentialsMixin
        self.credentials = self.credentials_class('username', 'password', *args, **kwargs)
    
    def test_creation_with_username_password(self):
        self.create_credentials()
        self.assertEqual(self.credentials.username, 'username')
        self.assertEqual(self.credentials.password, 'password')


class CommonCredentialsMixin(object):
    def test_creation_with_implicit_api(self):
        from tootwi import API
        self.create_credentials()
        self.assertIsInstance(self.credentials.api, API)
    
    def test_creation_with_explicit_api(self):
        from tootwi import API
        api = API()
        self.create_credentials(api=api)
        self.assertIsInstance(self.credentials.api, API)
        self.assertIs(self.credentials.api, api)
    
    def test_sign_works_at_all(self):
        from tootwi.api import WebRequest
        self.create_credentials()
        request = self.credentials.sign(self.credentials.api.invoke((' gEt ', '/method')))
        self.assertIsInstance(request, WebRequest)
        self.assertEqual('GET', request.method)
        self.assertIn('api.twitter.com/method', request.url)
        #??? how to check for auth parameter, that can be in query/postdata/headers?

#
# Here real test-cases go, built as combination of applicable mix-ins.
#

class ApplicationCredentialsTests(unittest.TestCase,
        CreationFailsWithoutConsumerMixin,
        CreationWorksWithConsumerOnlyMixin,
        CommonCredentialsMixin):
    def setUp(self, *args, **kwargs):
        from tootwi import ApplicationCredentials
        self.credentials_class = ApplicationCredentials

class TemporaryCredentialsTests(unittest.TestCase,
        CreationFailsWithoutConsumerMixin,
        CreationFailsWithoutTokenMixin,
        CreationWorksWithConsumerAndTokenMixin,
        CommonCredentialsMixin):
    def setUp(self, *args, **kwargs):
        from tootwi import TemporaryCredentials
        self.credentials_class = TemporaryCredentials

class TokenCredentialsTests(unittest.TestCase,
        CreationFailsWithoutConsumerMixin,
        CreationFailsWithoutTokenMixin,
        CreationWorksWithConsumerAndTokenMixin,
        CommonCredentialsMixin):
    def setUp(self, *args, **kwargs):
        from tootwi import TokenCredentials
        self.credentials_class = TokenCredentials

class BasicCredentialsTests(unittest.TestCase,
        CreationFailsWithoutUsernamePasswordMixin,
        CreationWorksWithUsernamePasswordMixin,
        CommonCredentialsMixin):
    def setUp(self, *args, **kwargs):
        from tootwi import BasicCredentials
        self.credentials_class = BasicCredentials
    
    def test_authorization_header(self):
        import base64
        self.create_credentials()
        request = self.credentials.sign(self.credentials.api.invoke((' gEt ', '/method')))
        self.assertTrue('Authorization' in request.headers)
        self.assertTrue(request.headers['Authorization'].startswith('Basic '))
        self.assertEqual(request.headers['Authorization'], 'Basic ' + base64.b64encode('%s:%s' % ('username', 'password')))
        self.assertEqual(request.headers['Authorization'], 'Basic dXNlcm5hbWU6cGFzc3dvcmQ=')


if __name__ == '__main__':
    unittest.main()
