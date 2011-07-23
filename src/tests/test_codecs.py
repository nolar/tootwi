#!/usr/bin/env python
import settings # must have! it contains sys.path adjustments.
import unittest2 as unittest

class ExternalCodecTest(unittest.TestCase):
    def callback(self, data):
        return [1,2,3]
    
    def setUp(self):
        from tootwi.codecs import ExternalCodec
        self.codec = ExternalCodec(self.callback)
    
    def test_creation(self):
        from tootwi.codecs import Codec
        self.assertIsInstance(self.codec, Codec)
        self.assertEqual(self.codec.extension, None)
    
    def test_decoding_of_none_sample_fails(self):
        from tootwi.errors import CodecValueIsNotStringError
        with self.assertRaises(CodecValueIsNotStringError):
            result = self.codec.decode(None)
    
    def test_decoding_of_empty_sample(self):
        result = self.codec.decode('')
        self.assertEqual(result, None)
    
    def test_decoding_of_space_sample(self):
        result = self.codec.decode(' ')
        self.assertEqual(result, None)
    
    def test_decoding_of_ascii_sample(self):
        result = self.codec.decode('our callback ignores all values')
        self.assertEqual(result, [1,2,3])


class FormCodecTest(unittest.TestCase):
    def setUp(self):
        from tootwi.codecs import FormCodec
        self.codec = FormCodec()
    
    def test_creation(self):
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
    
    def test_creation(self):
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


if __name__ == '__main__':
    unittest.main()
