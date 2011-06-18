# coding: utf-8
"""
Main API class to be instantiated and used. Accepts few other utulitary classes
to its constructor, such as credentials, connection, throttler, etc. For information
on utilitary objects see their corresponding modules in separate .py files.
For information on the library itself, see README files.

The developers may instantiate as many API instances with the same credentials
or connection or throttler or any other combination of parameters, as it is required
for their business logic.

The main methods to use are call() and flow(). First one (call()) is for single
all-in-one requests where you read its whole output at once. Former one (flow())
is for stream, where you read and handle data as they go, potentially infinitely.
NB: These methods have almost the same code, but there is no way to unify them,
NB: since one of them is simple callable method, whilst the other one is a generator.

There is no need to inherit this class, since it is sufficient. Though you still can.

"""

import contextlib
from .decoders import JsonDecoder, FormDecoder
from .connections import DEFAULT_CONNECTION

#??? move serialization to the separate classes (serializers.py?): JsonSerializer, XmlSerializer, RssSerializer, etc

#!!! check of headers work and do not break signature.

#!!! move stream urls outside (where to?). they donot belong to API entity itself.


class API(object):

    # A string to use as a library's User-Agent header for HTTP requests and streams.
    # Developer can specify their own User-Agent header when constructing a stream
    # or a request; in that case library's User-Agent is appended to the end of 
    # developer's one. Otherwise, library's User-Agent is used alone.
    USER_AGENT = 'tootwi/0.0' # tootwi is for truly object-oriented twitter

    # Default base URL to use when called method is relative (e.g., "statuses/public_timeline.json").
    # Can be overridden per API instance with a constructor argument. See there for more info.
    DEFAULT_API_BASE = 'http://api.twitter.com/1/'

    def __init__(self, credentials, connection=None, throttler = None, headers = None, api_base=None):
        """
        * credentials are required.
        * connection is required. what_about_default???
        * throttler is optional.
        * headers is optional. User-Agent will be added/extended.

        @param api_base
        Base URL to use for requests with reative URL provided (such as "statuses/public_timeline.json").
        It will be concatenated with the method directly, so be sure to include trailing slash.
        Optional. Defaults to resonable official API version URL.

        """

        super(API, self).__init__()
        self.credentials = credentials
        self.connection = connection if connection is not None else DEFAULT_CONNECTION
        self.throttler = throttler # ??? default throttler?
        self.api_base = api_base if api_base is not None else self.DEFAULT_API_BASE
        self.headers = headers if headers is not None else {}

    def call(self, target, parameters=None, decoder=JsonDecoder):
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

        with contextlib.closing(self.connection.open(self.credentials.sign(*self.prepare(target, parameters, decoder)))) as handle:
            try:
                print('Requesting...')#!!!
                line = handle.read()
                data = decoder(line)
                print('DONE...')#!!!
                return data
            finally:
                pass

    def flow(self, target, parameters=None, decoder=JsonDecoder):
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
        with contextlib.closing(self.connection.open(self.credentials.sign(*self.prepare(target, parameters, decoder)))) as handle:
            try:
                print('Iterating...')#!!!
                while True:
                    line = handle.readline()
                    data = decoder(line)
                    yield data
                print('DONE...')#!!!
            finally:
                pass

    #??? make it protected? rename to _prepare().
    def prepare(self, target, parameters, decoder):
        """
        Internal utilitary function to unify preparation of arguments
        for call() and flow() methods, since the logic is the same,
        but their code can not be unified.
        """

        # Make parameters and headers to be dictionary, prepopulate if necessary.
        # Headers can also be prepopulated in the constructor if we'll wish so.
        parameters = dict(parameters) if parameters is not None else {}
        parameters = dict([(k,v) for k,v in parameters.items() if v is not None])
        headers = dict(self.headers) if self.headers is not None else {}

        (method, url) = target
        method = method.upper()

        # Make url absolute. Add format extension if it is not there yet.
        url = url if '://' in url else self.api_base + url
        url = url if url.endswith(decoder.extension) else url + decoder.extension
        url = url % parameters #todo!!! catch unknown keys? or pass-throw

        # Add User-Agent header to the headers.
        #??? what if it has came in lower or upper case?
        #??? why is this here and not in connections.py? because we cannnot alter headers after signed!
        #self.headers['User-Agent'] = ' '.join([s for s in [self.headers.get('User-Agent'), self.USER_AGENT] if s])

        # The result MUST be in the same order as accepted by Credentials.sign().
        return (method, url, parameters, headers)

    REQUEST_TOKEN = ('POST', 'https://api.twitter.com/oauth/request_token') #NB: no version
    VERIFY_TOKEN  = ('POST', 'https://api.twitter.com/oauth/access_token') #NB: no version
    
    def request(self, callback=None):#!!! it should be in OAuthConsumerCredentials
        result = self.call(self.REQUEST_TOKEN, dict(
                oauth_callback = callback,
            ), decoder=FormDecoder)
        url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s' % result['oauth_token'] #!!!todo: urlencode
        return url, result['oauth_token'], result['oauth_token_secret'], result['oauth_callback_confirmed']
    
    def verify(self, verifier):#!!! this must be in OAuthRequestCredentials
        result = self.call(self.VERIFY_TOKEN, dict(
                oauth_verifier = verifier,
            ), decoder=FormDecoder)
        return result['oauth_token'], result['oauth_token_secret'], result['user_id'], result['screen_name']
