# coding: utf-8
"""
Utilitary classes to contain extended and/or prepared information when performing
API calls in credentials classes.
"""

import contextlib
from .transports import DEFAULT_TRANSPORT, TransportError
from .formats import Format, ExternalFormat, JsonFormat
from .errors import CredentialsWrongError, CredentialsValueError, OperationNotPermittedError, OperationNotFoundError, OperationValueError, ParametersCallbackError

# Retrieve version information if available, to use in User-Agent header in API class.
try:
    from ._version import __version__
except ImportError:
    __version__ = 'unknown'


class Invocation(object):
    def __init__(self, url, method, parameters, headers, format):
        super(Invocation, self).__init__()
        self._url = url
        self._method = method
        self._headers = headers
        self._parameters = parameters
        self._format = format
    
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
    def parameters(self):
        return self._parameters
    
    @property
    def format(self):
        return self._format


class SignedRequest(object):
    """
    Signed request, literally. It is created in credentials instance as
    a result of signing request parameters with user credentials. Since
    all the request's properties are already signed and cannot be changed,
    they are made read-only; the only way to specify them is a constructor.
    These is no need to derive this class, since this one is usually enough.
    """
    
    def __init__(self, url, method, headers, postdata, format):
        super(SignedRequest, self).__init__()
        self._url = url
        self._method = method
        self._headers = headers
        self._postdata = postdata
        self._format = format
    
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
    
    @property
    def format(self):
        return self._format


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
    USER_AGENT = 'tootwi/%s' % __version__
    
    def __init__(self, transport=None, throttler=None, headers=None, default_format=None, use_ssl=True, api_host='api.twitter.com', api_version='1'):
        super(API, self).__init__()
        self.transport = transport if transport is not None else DEFAULT_TRANSPORT
        self.throttler = throttler # ??? default throttler?
        self.use_ssl = use_ssl
        self.api_host = api_host if api_host is not None else self.DEFAULT_API_HOST
        self.api_version = api_version if api_version is not None else self.DEFAULT_API_VERSION
        self.default_format = default_format or JsonFormat
        self.headers = dict(headers) if headers is not None else {}
    
    def invoke(self, operation, parameters=None, **kwargs):
        """
        Internal utilitary function to unify preparation of arguments for
        call() and flow() methods, since the logic is the same, but their
        code can not be unified (one is regular call, another is generator).
        """
        
        # Make parameters and headers to be dictionaries, prepopulate if necessary.
        # Headers can also be populated by linked API instance, so ask it for data too.
        parameters = dict(parameters) if parameters is not None else {}
        headers = dict(self.headers)
        
        parameters.update(kwargs)
        
        # Add User-Agent header to the headers. Append if there is one already.
        lowered_keys = dict(map(lambda s: (s.lower(), s), headers.keys()))
        user_agent_key = lowered_keys.get('user-agent', 'User-Agent')
        headers[user_agent_key] = ' '.join([s for s in [headers.get(user_agent_key), self.USER_AGENT] if s])
        
        # Remove Nones from parameters and headers, if for some reason they occurred there.
        parameters = dict([(k,v) for k,v in parameters.items() if v is not None])
        headers = dict([(k,v) for k,v in headers.items() if v is not None])
        
        # Check that operation is of proper format and split it into method and url.
        try:
            operation = tuple(operation)
        except TypeError: # not a tuple or other iterale
            raise OperationValueError('Operation must be a tuple of two elements.')
        
        if len(operation) == 3:
            (method, url, format) = operation
        elif len(operation) == 2:
            (method, url) = operation
            format = None
        else:
            raise OperationValueError('Operation must be a tuple of two elements.')
        
        # Normalize coded and make it Format class instance, no matter what it originally is.
        # If this is a class, then instantiate it. Note it could be non-Format class too.
        # If this is something except Format instance, assume it is a callable/function.
        if format is None:
            format = self.default_format
        if isinstance(format, type):
            format = format()
        if not isinstance(format, Format):
            format = ExternalFormat(format)
        
        # Normalize HTTP requisites (method & url).
        # Make method uppercased verb word.
        # Make url absolute; add format extension if it is not there yet; resolve parameters.
        method = self.normalize_method(method)
        url = self.normalize_url(url, format.extension)
        url = url % parameters #NB: extra keys will be ignored; missed ones will cause exception.
        
        # The result MUST be in the same order as accepted by Credentials.sign().
        return Invocation(url, method, parameters, headers, format)
    
    def call(self, request):
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
        
        # Error might raise at any stage: connect, send, recv, parse, close -- all is the same for us.
        try:
            with contextlib.closing(self.transport(request)) as handle:
                line = handle.read()
                data = request.format.decode(line)
                return data
        except TransportError, e:
            self.handle_transport_error(e)
    
    def flow(self, request):
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
        
        # Error might raise at any stage: connect, send, recv, parse, close -- all is the same for us.
        try:
            with contextlib.closing(self.transport(request)) as handle:
                while True:
                    line = handle.readline()
                    data = request.format.decode(line)
                    yield data
        except TransportError, e:
            self.handle_transport_error(e)
    
    def normalize_method(self, method):
        """
        API assumes that method is always uppercased verb. This is very important
        for signing the request, since the verb is one of the elements to be signed.
        This is API's responsibility to normalize all values to protocol values, since
        these are API's restrictions and convention; also, the API owns the settings.
        """
        if not isinstance(method, basestring) or not method.strip():
            raise ValueError("Method is expected to be a non-empty string.")
        return method.strip().upper()
    
    def normalize_url(self, url, extension=None):
        # This method is also used in TemporaryCredentials.url building.
        
        if not isinstance(url, basestring) or not url.strip():
            raise ValueError("URL is expected to be a non-empty string.")
        if extension is not None and not isinstance(extension, basestring):
            raise ValueError("Extension is expected to be a string or None.")
        
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
    
    def handle_transport_error(self, e):
        """
        Since this class is responsible for URL structure, thus taking responsibility
        of the protocol conventions, it is also responsible for knowledge of what
        responses can contain, and thus performs error analysis and parsing.
        """
        # Assuming TransportError is a concept of HTTP error and has status code and response text.
        #TODO: more checks for more diverse errors
        if False: # just to use "elif" for all other conditions.
            pass
        elif 'Failed to validate oauth signature and token' in e.text: # plaintext response
            raise CredentialsWrongError('Failed to validate oauth signature and token')
        elif 'Desktop applications only support the oauth_callback value \'oob\'' in e.text: # xml response
            raise ParametersCallbackError('Desktop applications only support the oauth_callback value \'oob\'')
        elif e.code == 401:
            raise OperationNotPermittedError(e.text or 'Requested operation is not permitted with these credentials.')
        elif e.code == 404:
            raise OperationNotFoundError(e.text or 'Requested operation does not exist or URL is malformed.')
        else:
            # If we do not know what the error is in our semantics, then it is not our problem.
            raise e
