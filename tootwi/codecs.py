# coding: utf-8
"""
Codecs parse API responses depending on what format is used. Usually APIs are
implemented with JSON. Some requests, such as OAuth authorization, are returned
as application/x-www-form-urlencoded directly in the response body.

In addition to decoding, codecs provide extension to be added to URLs when
making a request. Extension must be an attribute of the codec, even if the
codec is a regular function (function can have attributes in Python). If no
extension is specified, then no extension is added to the URL (same as if it
was None or an empty string).
"""

from .errors import ExternalCodecCallableError, CodecValueIsNotStringError


class Codec(object):
    def decode(self, data):
        raise NotImplemented()


class ExternalCodec(Codec):
    def __init__(self, cb):
        super(ExternalCodec, self).__init__()
        if not callable(cb):
            raise ExternalCodecCallableError("External codec requires callable argument.")
        self.cb = cb
    
    def decode(self, data):
        return self.cb(data)


class FormCodec(Codec):
    """
    Decodes application/x-www-form-urlencoded response. It is used in OAuth
    authorization ("three-stage dance"). No extension is added to the URL.
    """
    extension = None
    def decode(self, data):
        import urlparse
        if not isinstance(data, basestring):
            raise CodecValueIsNotStringError("Cannot decode value which is not string.")
        data = data.strip()
        vals = dict(urlparse.parse_qsl(data, keep_blank_values=True, strict_parsing=True)) if data else {}
        return dict([(self.force_unicode(k), self.force_unicode(v)) for k,v in vals.items()])
    
    def force_unicode(self, s, encoding='utf8'):
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, encoding)




class JsonCodec(Codec):
    """
    Decodes JSON responses. To retrieve this format, ".json" extension should be
    added to the url. See API.normalize_url() for more information on extensions.
    
    The decoded result can be either dict or list. If the incoming data is an empty
    string, then returns None; empty strings are used in streams as keep-alives.
    """
    extension = 'json'
    def decode(self, data):
        import json
        if not isinstance(data, basestring):
            raise CodecValueIsNotStringError("Cannot decode value which is not string.")
        data = data.strip()
        return json.loads(data, 'utf8') if data else None
