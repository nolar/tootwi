# coding: utf-8

class Decoder(object):
    extension = None
    
    def __call__(self, data):
        raise NotImplemented()

class JsonDecoder(Decoder):
    extension = '.json'
    
    def __call__(self, data):
        import json
        assert isinstance(data, basestring)
        return json.loads(data, 'utf8') if data.strip() else {}

# application/x-www-form-urlencoded
class FormDecoder(Decoder):
    extension = ''
    
    def __call__(self, data):
        assert isinstance(data, basestring)
        import urlparse
        return dict(urlparse.parse_qsl(data, keep_blank_values=True, strict_parsing=True))

#todo XmlDecoder
#todo RssDecoder
