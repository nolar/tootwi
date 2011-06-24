# coding: utf-8
"""
Utilitary classes to contain extended and/or prepared information when performing
API calls in credentials classes.

todo: unite them???
"""

import contextlib
from .transports import DEFAULT_TRANSPORT, TransportError
from .errors import CredentialsWrongError, RequestTargetError, RequestParametersError, RequestCallbackError, RequestAccessError

class Request(object):
    """
    Signed request, literally. It is created in credentials instance as
    a result of signing request parameters with user credentials. Since
    all the request's properties are already signed and cannot be changed,
    they are made read-only; the only way to specify them is a constructor.
    These is no need to derive this class, since this one is usually enough.
    """
    
    def __init__(self, url, method, headers, postdata):
        super(Request, self).__init__()
        self._url = url
        self._method = method
        self._headers = headers
        self._postdata = postdata
    
    @property
    def url(self):
        return self._url
    
    @property
    def method(self):
        return self._method
    
    @property
    def headers(self):
        return self._headers
    
    @property
    def postdata(self):
        return self._postdata


class API(object):
    """
    API class is used as a container for common information on API itself, such as
    version, base url, protocol used (http vs https), extra headers, etc. Instances
    of this class could be passed to the constructors of credential classes. When not
    passed, default instance is automatically created with all its default settings.
    If you do not know whether to specify API instance or not to specify, then do not.
    The developers may instantiate as many API instances with different parameters
    as it is required for their business logic.
    """
    
    # A string to use as a library's User-Agent header for HTTP requests and streams.
    # Developer can specify their own User-Agent header when constructing a stream
    # or a request; in that case library's User-Agent is appended to the end of 
    # developer's one. Otherwise, library's User-Agent is used alone.
    USER_AGENT = 'tootwi/0.0' # tootwi is for truly object-oriented twitter
    
    def __init__(self, transport=None, throttler=None, headers={}, use_ssl=True, api_host='api.twitter.com', api_version='1'):
        super(API, self).__init__()
        self.transport = transport if transport is not None else DEFAULT_TRANSPORT
        self.throttler = throttler # ??? default throttler?
        self.headers = headers
        self.use_ssl = use_ssl
        self.api_host = api_host if api_host is not None else self.DEFAULT_API_HOST
        self.api_version = api_version if api_version is not None else self.DEFAULT_API_VERSION
    
    def call(self, request, decoder):
        """
        Single request scenario (connect, send, recv, close).
        
        Only one resulting object can be received per call. Once the response
        is received, parsed and filtered through callback, the connection
        is closed and the result is returned.
        
        Intended usage:
            item = api.call((method, url), parameters)
            do_something(item)
        """
        
        if self.throttler is not None:
            self.throttler.wait() # blocking wait
        if isinstance(decoder, type):
            decoder = decoder()
        
        # Error might raise at any stage: connect, send, recv, parse, close -- all is the same for us.
        try:
            with contextlib.closing(self.transport(request)) as handle:
                print('Requesting...')#!!!
                line = handle.read()
                data = decoder(line)
                print('DONE...')#!!!
                return data
        except TransportError, e:
            self.handle_transport_error(e)
    
    def flow(self, request, decoder):
        """
        Data flow scenario (connect, send, recv line by line, close).
        
        Iteration over a stream is a sequental access to each of the message there.
        Each recieved line is parsed as a separate result object, filtered through
        the callback, then yielded.
        
        Intended usage:
            for item in api.flow((method, url), parameters):
                do_something(item)
        
        """
        if self.throttler:
            self.throttler.wait() # blocking wait
        if isinstance(decoder, type):
            decoder = decoder()
        
        #!!! flows/streams are cnceptually non-close-able when exception happens inside for cycle (i.e., outside of generator).
        # Error might raise at any stage: connect, send, recv, parse, close -- all is the same for us.
        try:
            with contextlib.closing(self.transport(request)) as handle:
                print('Iterating...')#!!!
                while True:
                    line = handle.readline()
                    data = decoder(line)
                    yield data
                print('DONE...')#!!!
        except TransportError, e:
            self.handle_transport_error(e)
    
    def normalize_url(self, url, extension=None):
        assert isinstance(url, basestring)
        assert isinstance(extension, basestring) or extension is None
        
        #NB: We do not cut extension if it is already in the url.
        #NB: This is a problem of developer who specifies methods such a way.
        schema = 'https' if self.use_ssl else 'http'
        extension = unicode(extension).strip('.') if extension else ''
        extension = '.' + extension if extension else extension
        if '://' in url:
            return '%s%s' % (url, extension)
        elif url.startswith('/'):
            return '%s://%s/%s%s' % (schema, self.api_host, url.strip('/'), extension)
        else:
            return '%s://%s/%s/%s%s' % (schema, self.api_host, self.api_version, url.strip('/'), extension)
    
    def normalize_headers(self, headers):
        assert isinstance(headers, dict)
        
        # Add User-Agent header to the headers. Append if there is one already.
        #??? what if it has came in lower or upper case?
        headers['User-Agent'] = ' '.join([s for s in [headers.get('User-Agent'), self.USER_AGENT] if s])
        
        return headers
    
    def handle_transport_error(self, e):
        """
        Since this class is responsible for URL structure, thus taking responsibility
        of the protocol conventions, it is also responsible for knowledge of what
        responses can contain, and thus performing error analysis and parsing.
        This can change in the future, since proper responsible class is not obvious.
        It can be a transport (down the stack), or a credentials (up the stack).
        TODO: rethink responsibilities.
        """
        # Assuming TransportError is a concept of HTTP error and has status code and response text.
        #TODO: more checks
        if False: # just to use "elif" for all other conditions.
            pass
        elif 'Failed to validate oauth signature and token' in e.text: # plaintext response
            raise CredentialsWrongError('Failed to validate oauth signature and token')
        elif 'Desktop applications only support the oauth_callback value \'oob\'' in e.text: # xml response
            raise RequestCallbackError('Desktop applications only support the oauth_callback value \'oob\'')
        elif e.code == 401:
            raise RequestAccessError(e.text or 'Requested operation is not permitted with these credentials.')
        elif e.code == 404:
            raise RequestTargetError(e.text or 'Requested operation does not exist or URL is malformed.')
        else:
            # If we do not know what is the error in our semantics, then it is not our headache.
            #import pdb; pdb.set_trace()
            raise e
