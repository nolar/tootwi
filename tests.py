import unittest2 as unittest
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

class ApplicationCredentialsTest(unittest.TestCase):
    
    def testCreationWithNoConsumer(self):
        from tootwi import ApplicationCredentials
        with self.assertRaises(TypeError):
            application_credentials = ApplicationCredentials()
    
    def testCreationWithNoConsumerKey(self):
        from tootwi import ApplicationCredentials
        with self.assertRaises(TypeError):
            application_credentials = ApplicationCredentials(consumer_secret=CONSUMER_SECRET)
    
    def testCreationWithNoConsumerSecret(self):
        from tootwi import ApplicationCredentials
        with self.assertRaises(TypeError):
            application_credentials = ApplicationCredentials(consumer_key=CONSUMER_KEY)
    
    def testCreationWithImplicitAPI(self):
        from tootwi import ApplicationCredentials
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        self.assertEqual(application_credentials.consumer_key, CONSUMER_KEY)
        self.assertEqual(application_credentials.consumer_secret, CONSUMER_SECRET)
    
    def testCreationWithExplicitAPI(self):
        from tootwi import ApplicationCredentials, API
        api = API()
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET, api=api)
        self.assertEqual(application_credentials.consumer_key, CONSUMER_KEY)
        self.assertEqual(application_credentials.consumer_secret, CONSUMER_SECRET)


class TemporaryCredentialsTest(unittest.TestCase):
    pass


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
        from tootwi import ApplicationCredentials, OAuthCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(OAuthCallbackError):
            temporary_credentials = application_credentials.request('')
    
    def testRequestForAuthorizationWithBadFormatCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials, OAuthCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(OAuthCallbackError):
            temporary_credentials = application_credentials.request(self.BAD_FORMAT_CALLBACK)
    
    def testRequestForAuthorizationWithBadFormatCallback(self):
        #!!! Assuming the callback domain is authorized and is of valid format (not localhost).
        from tootwi import ApplicationCredentials, OAuthCallbackError
        application_credentials = ApplicationCredentials(CONSUMER_KEY, CONSUMER_SECRET)
        with self.assertRaises(OAuthCallbackError):
            temporary_credentials = application_credentials.request(self.UNAUTHORIZED_CALLBACK)


class OAuthConfirmScenarioTest(unittest.TestCase):
    pass


class OtherStuff(unittest.TestCase):
    pass
#        #FIXME!!! we are testing more than just an API here, not good
#        #public_timeline = PublicTimeline(application_credentials)
#        #first_status = list(public_timeline)
#    
#    def testAnonymousCReated(self):
#        api = Anonymous()
##       timeline = api.getPublicTimelime()
##       self.assertTrue(len(timelime) > 0, msg="Public timeline is empty -- quite unbelievable.")
#
#    def testAccountCreatedDirecty(self):
#        api = Account(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
#                token_key=ACCOUNT_TOKEN_KEY, token_secret=ACCOUNT_TOKEN_SECRET)
#
#    def testAccountCreatedWithApplication(self):
#        app = Application(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
#        api = Account(app, token_key=ACCOUNT_TOKEN_KEY, token_secret=ACCOUNT_TOKEN_SECRET)



if __name__ == '__main__':
    unittest.main()
