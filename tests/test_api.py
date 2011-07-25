#!/usr/bin/env python
try:
    import unittest2 as unittest # python-2 external dependency
except:
    import unittest # python-3 native module


FAKE_OPERATION = ('GET', '/nowhere/')


class APITest(unittest.TestCase):
    def setUp(self):
        from tootwi import API
        self.api = API()


class APIInvokeOperationTests(APITest):
    def test_invoke_with_no_operation(self):
        from tootwi.errors import OperationValueError
        with self.assertRaisesRegexp(TypeError, r'takes at least 2 arguments \(1 given\)'):
            self.api.invoke()
    
    def test_invoke_with_noniterable_operation(self):
        from tootwi.errors import OperationValueError
        with self.assertRaises(OperationValueError):
            self.api.invoke(123)
    
    def test_invoke_with_empty_operation(self):
        from tootwi.errors import OperationValueError
        with self.assertRaises(OperationValueError):
            self.api.invoke(tuple())
    
    def test_invoke_with_underfilled_operation(self):
        from tootwi.errors import OperationValueError
        with self.assertRaises(OperationValueError):
            self.api.invoke(('method',))
    
    def test_invoke_with_overfilled_operation(self):
        from tootwi.errors import OperationValueError
        with self.assertRaises(OperationValueError):
            self.api.invoke(('method', 'url', 'format', 'dummy'))
    
    def test_invoke_with_properly_sized_operation(self):
        from tootwi.api import Invocation
        invocation = self.api.invoke((' gEt ', 'fake-operation'))
        self.assertIsInstance(invocation, Invocation)
        self.assertEqual(invocation.method, 'GET')
        self.assertIn('://api.twitter.com/', invocation.url)
        self.assertIn('/fake-operation', invocation.url)
        # Normalization is thoroughly tested elsewhere.
        # Here, check if it is at all called (i.e. url is changed).
        # The exact url value depends on use_ssl, format, etc - ignore them here.


class APIInvokeFormatsTests(APITest):
    def test_invoke_with_format_absent(self):
        from tootwi.formats import Format, JsonFormat
        invocation = self.api.invoke(FAKE_OPERATION)
        self.assertIsInstance(invocation.format, Format)
        self.assertIsInstance(invocation.format, JsonFormat)
    
    def test_invoke_with_format_as_class(self):
        from tootwi.formats import Format, FormFormat
        invocation = self.api.invoke(FAKE_OPERATION + (FormFormat,))
        self.assertIsInstance(invocation.format, Format)
        self.assertIsInstance(invocation.format, FormFormat)
    
    def test_invoke_with_format_as_instance(self):
        from tootwi.formats import Format, FormFormat
        format = FormFormat()
        invocation = self.api.invoke(FAKE_OPERATION + (format,))
        self.assertIsInstance(invocation.format, Format)
        self.assertIsInstance(invocation.format, FormFormat)
        self.assertIs(invocation.format, format)
    
    def test_with_format_as_function(self):
        def fn(data): pass
        from tootwi.formats import Format, ExternalFormat
        invocation = self.api.invoke(FAKE_OPERATION + (fn,))
        self.assertIsInstance(invocation.format, Format)
        self.assertIsInstance(invocation.format, ExternalFormat)
        self.assertIs(invocation.format._cb, fn)#??? accessing protected member


class APIInvokeParametersTests(APITest):
    def test_invoke_with_no_parameters(self):
        from tootwi.api import Invocation
        from tootwi.formats import Format
        invocation = self.api.invoke(FAKE_OPERATION)
        self.assertIsInstance(invocation, Invocation)
        self.assertDictEqual(invocation.parameters, {})
    
    def test_invoke_with_mixed_parameters(self):
        from tootwi.api import Invocation
        from tootwi.formats import Format
        invocation = self.api.invoke(FAKE_OPERATION, {'c':789}, a=123, b=456)
        self.assertIsInstance(invocation, Invocation)
        self.assertDictEqual(invocation.parameters, {'a':123, 'b':456, 'c':789})


class APINormalizationTests(APITest):
    
    def test_normalize_method_with_nonstrings(self):
        #??? ValueError or tootwi.errors.FormatValueError?
        with self.assertRaises(ValueError):
            self.api.normalize_method(None)
        with self.assertRaises(ValueError):
            self.api.normalize_method(1234)
        with self.assertRaises(ValueError):
            self.api.normalize_method('  ')
    
    def test_normalize_method_spaces_and_case(self):
        self.assertEqual(self.api.normalize_method(' gEt  '), 'GET' )
        self.assertEqual(self.api.normalize_method(' PoSt '), 'POST')
    
    def test_normalize_url(self):
        from tootwi import API
        normal_api = API(use_ssl=False)
        secure_api = API(use_ssl=True)
        
        self.assertEqual(normal_api.normalize_url( 'method'        ), 'http://api.twitter.com/1/method')
        self.assertEqual(normal_api.normalize_url( 'method',  None ), 'http://api.twitter.com/1/method')
        self.assertEqual(normal_api.normalize_url( 'method',  'ext'), 'http://api.twitter.com/1/method.ext')
        self.assertEqual(normal_api.normalize_url( 'method', '.ext'), 'http://api.twitter.com/1/method.ext')
        self.assertEqual(normal_api.normalize_url('/method'        ), 'http://api.twitter.com/method')
        self.assertEqual(normal_api.normalize_url('/method',  None ), 'http://api.twitter.com/method')
        self.assertEqual(normal_api.normalize_url('/method',  'ext'), 'http://api.twitter.com/method.ext')
        self.assertEqual(normal_api.normalize_url('/method', '.ext'), 'http://api.twitter.com/method.ext')
        self.assertEqual(normal_api.normalize_url('proto://server/method'        ), 'proto://server/method')
        self.assertEqual(normal_api.normalize_url('proto://server/method',  None ), 'proto://server/method')
        self.assertEqual(normal_api.normalize_url('proto://server/method',  'ext'), 'proto://server/method.ext')
        self.assertEqual(normal_api.normalize_url('proto://server/method', '.ext'), 'proto://server/method.ext')
        
        self.assertEqual(secure_api.normalize_url( 'method'        ), 'https://api.twitter.com/1/method')
        self.assertEqual(secure_api.normalize_url( 'method',  None ), 'https://api.twitter.com/1/method')
        self.assertEqual(secure_api.normalize_url( 'method',  'ext'), 'https://api.twitter.com/1/method.ext')
        self.assertEqual(secure_api.normalize_url( 'method', '.ext'), 'https://api.twitter.com/1/method.ext')
        self.assertEqual(secure_api.normalize_url('/method'        ), 'https://api.twitter.com/method')
        self.assertEqual(secure_api.normalize_url('/method',  None ), 'https://api.twitter.com/method')
        self.assertEqual(secure_api.normalize_url('/method',  'ext'), 'https://api.twitter.com/method.ext')
        self.assertEqual(secure_api.normalize_url('/method', '.ext'), 'https://api.twitter.com/method.ext')
        self.assertEqual(secure_api.normalize_url('proto://server/method'        ), 'proto://server/method')
        self.assertEqual(secure_api.normalize_url('proto://server/method',  None ), 'proto://server/method')
        self.assertEqual(secure_api.normalize_url('proto://server/method',  'ext'), 'proto://server/method.ext')
        self.assertEqual(secure_api.normalize_url('proto://server/method', '.ext'), 'proto://server/method.ext')


class APIOverallTests(unittest.TestCase):
    def test_headers_go_to_invocation(self):
        from tootwi import API
        api = API(headers={'hello':'world', 'empty':''})
        invocation = api.invoke(FAKE_OPERATION)
        self.assertDictContainsSubset({'hello':'world', 'empty':''}, invocation.headers)
    
    def test_headers_cleaned_from_nones(self):
        from tootwi import API
        api = API(headers={'empty':None})
        invocation = api.invoke(FAKE_OPERATION)
        self.assertNotIn('empty', invocation.headers)


if __name__ == '__main__':
    unittest.main()
