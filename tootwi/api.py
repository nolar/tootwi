import contextlib
from .connectors import DEFAULT_CONNECTOR

class Request(object):
    """
    Signed request, literally. Returned from credentials instance as a
    result of signing initial request parameters with user credentials.
    Should not provide write ablities except as for constructor.
    These is no need to derive it, since this one works fine enough.
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
    # A string to use as a library's User-Agent header for HTTP requests and streams.
    # Developer can specify their own User-Agent header when constructing a stream
    # or a request; in that case library's User-Agent is appended to the end of 
    # developer's one. Otherwise, library's User-Agent is used alone.
    USER_AGENT = 'tootwi/0.0' # tootwi is for truly object-oriented twitter
    
    # Default base URL to use when called method is relative (e.g., "statuses/public_timeline.json").
    # Can be overridden per API instance with a constructor argument. See there for more info.
    DEFAULT_API_BASE = 'https://api.twitter.com/'
    DEFAULT_API_VERSION = '1'
    
    def __init__(self, connector=None, throttler=None, headers=None, api_base=None, api_version=None):
        super(API, self).__init__()
        self.connector = connector if connector is not None else DEFAULT_CONNECTOR
        self.throttler = throttler # ??? default throttler?
        self.headers = headers if headers is not None else {}
        self.api_base = api_base if api_base is not None else self.DEFAULT_API_BASE
        self.api_version = api_version if api_version is not None else self.DEFAULT_API_VERSION

    def call(self, request, decoder=None):
        """
        Single request scenario (connect, send, recv, close).
        
        Only one resulting object can be received per call. Once the response
        is received, parsed and filtered through callback, the connection
        is closed and the result is returned.
        
        Intended usage:
            item = api.call((method, url), parameters)
            do_something(item)
        """
        
        if self.throttler:
            self.throttler.wait() # blocking wait
        
        with contextlib.closing(self.connector.open(request)) as handle:
            try:
                print('Requesting...')#!!!
                line = handle.read()
                data = decoder(line)
                print('DONE...')#!!!
                return data
            finally:
                pass
    
    def flow(self, request, decoder=None):
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

        #!!! flows/streams are cnceptually non-close-able when exception happens inside for cycle (i.e., outside of generator).
        with contextlib.closing(self.connector.open(request)) as handle:
            try:
                print('Iterating...')#!!!
                while True:
                    line = handle.readline()
                    data = decoder(line)
                    yield data
                print('DONE...')#!!!
            finally:
                pass
    
    def normalize_url(self, url):
        assert isinstance(url, basestring)
        
        if '://' in url:
            return url
        elif url.startswith('/'):
            return '/'.join([self.api_base.strip('/'), url.strip('/')])
        else:
            return '/'.join([self.api_base.strip('/'), self.api_version.strip('/'), url.strip('/')])
