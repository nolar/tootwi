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


if __name__ == '__main__':
    unittest.main()
