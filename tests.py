import unittest2 as unittest
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

class FormCodecTest(unittest.TestCase):
    def setUp(self):
        from tootwi.codecs import FormCodec
        self.codec = FormCodec()
    
    def test_creation_with_no_arguments(self):
        from tootwi.codecs import Codec
        self.assertIsInstance(self.codec, Codec)
        self.assertEqual(self.codec.extension, None)
    
    def test_decoding_of_none_sample_fails(self):
        from tootwi.errors import CodecValueIsNotStringError
        with self.assertRaises(CodecValueIsNotStringError):
            result = self.codec.decode(None)
    
    def test_decoding_of_empty_sample(self):
        sample = ' '
        result = self.codec.decode(sample)
        self.assertEqual(result, {})
    
    def test_decoding_of_ascii_sample(self):
        sample = 'a=123&b=456'
        result = self.codec.decode(sample)
        self.assertEqual(result, {'a':'123', 'b': '456'})
    
    def test_decoding_of_unicode_sample(self):
        output = u'\u043f\u0440\u0438\u0432\u0435\u0442' # russian 'privet' ('hello')
        sample = 'a=%s&b=%s%s' % (output, output, output)
        result = self.codec.decode(sample)
        self.assertEqual(result, {'a':output, 'b': output+output})
    
    def test_decoding_of_urlencoded_sample(self):
        output = u'\u043f\u0440\u0438\u0432\u0435\u0442' # russian 'privet' ('hello')
        sample = 'a=%25&b=%20%30&c=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82'
        result = self.codec.decode(sample)
        self.assertEqual(result, {'a':'%', 'b': ' 0', 'c': output})
    
    

class JsonCodecTest(unittest.TestCase):
    def setUp(self):
        from tootwi.codecs import JsonCodec
        self.codec = JsonCodec()
    
    def test_creation_with_no_arguments(self):
        from tootwi.codecs import Codec
        self.assertIsInstance(self.codec, Codec)
        self.assertEqual(self.codec.extension, 'json')
    
    def test_decoding_of_none_sample_fails(self):
        from tootwi.errors import CodecValueIsNotStringError
        with self.assertRaises(CodecValueIsNotStringError):
            result = self.codec.decode(None)
    
    def test_decoding_of_empty_sample(self):
        sample = ' '
        result = self.codec.decode(sample)
        self.assertEqual(result, None)
    
    def test_decoding_of_unicode_sample(self):
        output = u'\u043f\u0440\u0438\u0432\u0435\u0442' # russian 'privet' ('hello')
        result = self.codec.decode('"' + output.encode('utf8') + '"')
        self.assertEqual(result, output)
    
    def test_decoding_of_dict_sample(self):
        sample = ''' {"a":123, "b":456, "c":[1,2,3], "hello": "world"} '''
        result = self.codec.decode(sample)
        self.assertEqual(result, {'a':123, 'b':456, 'c':[1,2,3], 'hello':'world'})
    
    def test_decoding_of_list_sample(self):
        sample = ''' [1,2,"hello", "world", 1,2] '''
        result = self.codec.decode(sample)
        self.assertEqual(result, [1,2,'hello','world',1,2])


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
