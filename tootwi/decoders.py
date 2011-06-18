# coding: utf-8

class Decoder(dict):
    extension = None
    
    def __init__(self, data):
        decoded = self.decode(data)
        super(Decoder, self).__init__(decoded)
    
    def decode(self, data):
        raise NotImplemented()

class JsonDecoder(Decoder):
    extension = '.json'
    
    def decode(self, data):
        import json
        assert isinstance(data, basestring)
        return json.loads(data, 'utf8') if data.strip() else {}

# application/x-www-form-urlencoded
class FormDecoder(Decoder):
    extension = ''
    
    def decode(self, data):
        assert isinstance(data, basestring)
        import urlparse
        return dict(urlparse.parse_qsl(data, keep_blank_values=True, strict_parsing=True))

#todo XmlDecoder
#todo RssDecoder
