import unittest2 as unittest
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET


class OAuthRequestScenarioTest(unittest.TestCase):
    GOOD_CALLBACK = 'http://nolar.info.local/'
    BAD_FORMAT_CALLBACK = 'what? callback? what callback?'
    UNAUTHORIZED_CALLBACK = 'http://unauthorized.zone.example.com/'
    
    def testRequestForAuthorizationWithNoCallback(self):
        from tootwi import ApplicationCredentials, TemporaryCredentials
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        
        temporary_credentials = application_credentials.request()
        self.assertIsInstance(temporary_credentials, TemporaryCredentials)
        self.assertEqual(temporary_credentials.consumer_key, CONSUMER_KEY)
        self.assertEqual(temporary_credentials.consumer_secret, CONSUMER_SECRET)
        
        url = temporary_credentials.url
        self.assertTrue('http://' in url or 'https://' in url)
        self.assertTrue('://api.twitter.com/oauth/authorize?oauth_token=' in url)

    def testRequestForAuthorizationWithGoodCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials, TemporaryCredentials
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        temporary_credentials = application_credentials.request(self.GOOD_CALLBACK)
        self.assertTrue(isinstance(temporary_credentials, TemporaryCredentials))
        self.assertTrue(temporary_credentials.callback_confirmed)
    
    def testRequestForAuthorizationWithEmptyCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request('')
    
    def testRequestForAuthorizationWithBadFormatCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request(self.BAD_FORMAT_CALLBACK)
    
    def testRequestForAuthorizationWithUnauthorizedCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials
        from tootwi.errors import ParametersCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(ParametersCallbackError):
            temporary_credentials = application_credentials.request(self.UNAUTHORIZED_CALLBACK)


class OAuthConfirmScenarioTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
