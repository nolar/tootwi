#!/usr/bin/env python
import settings
import unittest2 as unittest


class OAuthRequestAuthorizationScenarioTests(unittest.TestCase):
    GOOD_CALLBACK = 'http://nolar.info.local/'
    BAD_FORMAT_CALLBACK = 'what? callback? what callback?'
    UNAUTHORIZED_CALLBACK = 'http://unauthorized.zone.example.com/'
    
    def test_request_for_authorization_with_no_callback(self):
        from tootwi import ApplicationCredentials, TemporaryCredentials
        application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        
        temporary_credentials = application_credentials.request()
        self.assertIsInstance(temporary_credentials, TemporaryCredentials)
        self.assertEqual(temporary_credentials.consumer_key, application_credentials.consumer_key)
        self.assertEqual(temporary_credentials.consumer_secret, application_credentials.consumer_secret)
        self.assertIsInstance(temporary_credentials.token_key, basestring)
        self.assertIsInstance(temporary_credentials.token_secret, basestring)
        self.assertTrue(temporary_credentials.token_key)
        self.assertTrue(temporary_credentials.token_secret)
        
        url = temporary_credentials.url
        self.assertIsInstance(url, basestring)
        self.assertTrue('http://' in url or 'https://' in url)
        self.assertTrue('://api.twitter.com/oauth/authorize?oauth_token=' in url)
    
    @unittest.skip("Something is bad with callbacks there.")#FIXME!!!
    def test_request_for_authorization_with_good_callback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials, TemporaryCredentials
        application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        temporary_credentials = application_credentials.request(self.GOOD_CALLBACK)
        self.assertIsInstance(temporary_credentials, TemporaryCredentials)
        self.assertTrue(temporary_credentials.callback_confirmed)
    
    @unittest.skip("Something is bad with callbacks there.")#FIXME!!!
    def test_request_for_authorization_with_empty_callback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request('')
    
    @unittest.skip("Something is bad with callbacks there.")#FIXME!!!
    def test_request_for_authorization_with_bad_format_callback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request(self.BAD_FORMAT_CALLBACK)
    
    @unittest.skip("Something is bad with callbacks there.")#FIXME!!!
    def test_request_for_authorization_with_unauthorized_callback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request(self.UNAUTHORIZED_CALLBACK)


class OAuthConfirmAuthorizationScenarioTests(unittest.TestCase):
    CALLBACK = 'http://nolar.info.local/'
    
    def setUp(self):
        from tootwi import ApplicationCredentials, TemporaryCredentials
        self.application_credentials = ApplicationCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.temporary_credentials = self.application_credentials.request()
    
    def test_confirm_authorization_with_no_verifier_fails(self):
        with self.assertRaises(TypeError):
            self.temporary_credentials.confirm()
    
    def test_confirm_authorization_with_empty_verifier_fails(self):
        from tootwi.errors import OperationNotPermittedError
        with self.assertRaises(OperationNotPermittedError):
            self.temporary_credentials.confirm('')
    
    def test_confirm_authorization_with_wrong_verifier_fails(self):
        from tootwi.errors import OperationNotPermittedError
        with self.assertRaises(OperationNotPermittedError):
            self.temporary_credentials.confirm('0123456789')
    
    @unittest.skip("Requires a lot of web page interaction (login, submit, etc).")#TODO later
    def test_confirm_authorization_with_pin_verifier_works(self):
        import urllib2
        content = urllib2.urlopen(self.temporary_credentials.url).read()
        # if it is a login page, then parse form, push login button
        # if it is a auth page, then parse form, push auth button
        # if it is a pin code page, then parse pin code
        # on ever step, remember cookies and form hidden values (this is a "session")
        #verifier = ...???...
        #self.temporary_credentials.confirm(verifier)
    
    @unittest.skip("Requires a lot of web page interaction (login, submit, etc).")#TODO later
    def test_confirm_authorization_with_callback_verifier_works(self):
        import urllib2
        content = urllib2.urlopen(self.temporary_credentials.url).read()
        # if it is a login page, then parse form, push login button
        # if it is a auth page, then parse form, push auth button
        # if it is a redirect, then parse verifier code
        # on ever step, remember cookies and form hidden values (this is a "session")
        #verifier = ...???...
        #self.temporary_credentials.confirm(verifier)


class OAuthTokenAccountScenarioTests(unittest.TestCase):
    def setUp(self):
        from tootwi import TokenCredentials
        self.token_credentials = TokenCredentials(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, settings.ACCESS_KEY, settings.ACCESS_SECRET)
    
    def test_account_model_creation(self):
        from tootwi.models import Model, Account, User, AccountUser
        
        account = self.token_credentials.account
        self.assertIsInstance(account, Model)
        self.assertIsInstance(account, Account)
        
        user = account.verify_credentials()
        self.assertIsInstance(user, Model)
        self.assertIsInstance(user, User)
        
        self.assertTrue(hasattr(user, 'id') and user.id)
        self.assertTrue(hasattr(user, 'name') and user.name)


#!!! test for errornous scenarios for each of the API.handle_transport_error() cases.


if __name__ == '__main__':
    unittest.main()
