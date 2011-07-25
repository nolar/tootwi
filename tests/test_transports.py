#!/usr/bin/env python
import unittest2 as unittest
import contextlib
from server import HTTPServer


class urllib2TransportTests(unittest.TestCase):
    def assertFileProtocol(self, f):
        self.assertTrue(hasattr(f, 'read') and callable(f.read))
        self.assertTrue(hasattr(f, 'readline') and callable(f.readline))
        self.assertTrue(hasattr(f, 'readlines') and callable(f.readlines))
        self.assertTrue(hasattr(f, 'close') and callable(f.close))
    
    def makeRequest(self, url, method='GET', postdata=None):
        from tootwi.api import SignedRequest as WebRequest#!!!
        return WebRequest(url, method, headers={'User-Agent':'tootwi-tests'}, postdata=postdata, format=None)
    
    def setUp(self):
        from tootwi.transports import urllib2Transport
        self.transport = urllib2Transport()
    
    def test_read_on_https(self):
        pattern = 'hello world!\nthis is a test server.'
        with HTTPServer(port=8888, use_ssl=True, content_body=pattern):
            with contextlib.closing(self.transport(self.makeRequest('https://localhost:8888/'))) as stream:
                self.assertFileProtocol(stream)
                
                content = stream.read()
                self.assertIsInstance(content, basestring)
                self.assertTrue(content, pattern)
    
    def test_read_on_http(self):
        pattern = 'hello world!\nthis is a test server.'
        with HTTPServer(port=8888, content_body=pattern):
            with contextlib.closing(self.transport(self.makeRequest('http://localhost:8888/'))) as stream:
                self.assertFileProtocol(stream)
                
                content = stream.read()
                self.assertIsInstance(content, basestring)
                self.assertEqual(content, pattern)
    
    def test_readlines_on_http(self):
        pattern = ['hello world!\n', 'this is a test server.']
        with HTTPServer(port=8888, content_body=''.join(pattern)):
            with contextlib.closing(self.transport(self.makeRequest('http://localhost:8888/'))) as stream:
                self.assertFileProtocol(stream)
                
                content = stream.readlines()
                self.assertIsInstance(content, list)
                self.assertListEqual(content, pattern)
    
    def test_post(self):
        pattern = 'POST RESPONSE: %s'
        postdata = 'hello world'
        expected = 'POST RESPONSE: hello world'
        with HTTPServer(port=8888, content_body=pattern):
            with contextlib.closing(self.transport(self.makeRequest('http://localhost:8888/', 'POST', postdata=postdata))) as stream:
                self.assertFileProtocol(stream)
                
                content = stream.read()
                self.assertIsInstance(content, basestring)
                self.assertEqual(content, expected)
    
    def test_transport_error_with_nonurl(self):
        with self.assertRaises(ValueError):
            self.transport(self.makeRequest('not a url at all'))
    
    def test_transport_error_with_unexistent_domain(self):
        with self.assertRaises(EnvironmentError):
            self.transport(self.makeRequest('http://unexistent.domain/'))
    
    def test_transport_error_with_specified_code(self):
        from tootwi.transports import TransportServerError
        with HTTPServer(port=8888, status_code=567, status_text="TEST FAILED"):
            with self.assertRaises(TransportServerError):#!!! check for 567 code and messages
                self.transport(self.makeRequest('http://localhost:8888/'))
    
    def test_bufsize_hack_disabled(self):
        pass#!!!TODO
    
    def test_bufsize_hack_enabled(self):
        pass#!!!TODO


if __name__ == '__main__':
    unittest.main()
