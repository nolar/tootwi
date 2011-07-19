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

class Codec(object):
    def __call__(self, data):
        raise NotImplemented()

class FormCodec(Codec):
    """
    Decodes application/x-www-form-urlencoded response. It is used in OAuth
    authorization ("three-stage dance"). No extension is added to the URL.
    """
    def __call__(self, data):
        assert isinstance(data, basestring)
        import urlparse
        return dict(urlparse.parse_qsl(data, keep_blank_values=True, strict_parsing=True))

class JsonCodec(Codec):
    """
    Decodes JSON responses. To retrieve this format, ".json" extension should be
    added to the url. See API.normalize_url() for more information on extensions.
    
    The decoded result can be either dict or list. If the incoming data is an empty
    string, then returns None; empty strings are used in streams as keep-alives.
    """
    extension = 'json'
    def __call__(self, data):
        assert isinstance(data, basestring)
        import json
        return json.loads(data, 'utf8') if data.strip() else None
