# coding: utf-8
"""
Credentials are responsible for authenticating and authorizing a user on
a remote side. Credentials object is usually passed to the API constructor.

Credentials instance works as a passthrough filter: accept request parameters,
modify or extend them according to authorization protocol used, and return
these modified parameters to the consumer class (usually, connections).

Derivatives must implement sign(...) method which accepts initial request
parameters and returns Request object in return. Or any other alike
object that obeys Request protocol, i.e. provides these properties:
    url, method, headers, postdata.

Dependencies must be imported on demand only, i.e. when credential is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).
"""


import contextlib
from .models import Account
from .decoders import JsonDecoder, FormDecoder
from .api import Request, API

#??? move serialization to the separate classes (serializers.py?): JsonSerializer, XmlSerializer, RssSerializer, etc

#!!! check of headers work and do not break signature.

#!!! move stream urls outside (where to?). they donot belong to API entity itself.

#!!! add support for realm

#!!! move into separate modules, and put imports to top as normally


class Credentials(object):
    """
    Base class for authentication and authroization schemas.
    Descendants must implement sign(...) method, which accepts
    a bunch of request parameters, signs them as required, and
    return Request read-only object.
    """
    
    def __init__(self, api=None):
        super(Credentials, self).__init__()
        self.api = api if api is not None else API()
    
    def sign(self, method, url, parameters, headers):
        raise NotImplemented()
    
    def call(self, target, parameters=None, decoder=JsonDecoder):
        return self.api.call(self.sign(*self.prepare(target, parameters, decoder)), decoder)
    
    def flow(self, target, paramaters=None, decoder=JsonDecoder):
        return self.api.flow(self.sign(*self.prepare(target, parameters, decoder)), decoder)
    
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
        headers = dict(self.api.headers) if self.api.headers is not None else {} #!!! not good we go into API internals
        
        (method, url) = target
        method = method.upper()
        
        # Make url absolute. Add format extension if it is not there yet.
        url = self.api.normalize_url(url)
        url = url if url.endswith(decoder.extension) else url + decoder.extension
        url = url % parameters #todo!!! catch unknown keys? or pass-throw
        
        # Add User-Agent header to the headers.
        #??? what if it has came in lower or upper case?
        #??? why is this here and not in connectors.py? because we cannnot alter headers after signed!
        #self.headers['User-Agent'] = ' '.join([s for s in [self.headers.get('User-Agent'), self.USER_AGENT] if s])
        
        # The result MUST be in the same order as accepted by Credentials.sign().
        return (method, url, parameters, headers)


class OAuthCredentials(Credentials):
    """
    OAuth authorization schema. Highl recommened for all Twitter API calls and streams.
    Accepts mandatory consumer key and optional access token key.

    Consumer key and secret are provided on an application page (see https://dev.twitter.com/apps).

    Access token key and secret is a result of complicated rithual, and are user-specific
    (i.e., each user has its own access token key and secret for each application).
    Access token is optional for public requests (such as public timeline), and for initial
    access authorization rithual itself. For all other requests it is required.
    """

#!!! implement methods for three-stage authorization to receive access token keys.

    def __init__(self, consumer_key, consumer_secret, token_key, token_secret, api=None):
        super(OAuthCredentials, self).__init__(api=api)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_key = token_key
        self.token_secret = token_secret

    def sign(self, method, url, parameters, headers):
        # On-demand import to avoid errors when this credentials schema is not used.
        import oauth2 as oauth
        import time
        
        # Pack our credentials into oauth native classes.
        
        # Fulfill request parameters with oauth-specific ones.
        parameters.update({
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_version': '1.0',
            'oauth_timestamp': int(time.time()),
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': self.token_key,
            })
        
        # Sign the request. It is good idea to keep all oauth call here.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        if self.consumer_key is None or self.consumer_secret is None:
            consumer = None
        else:
            consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        #!!! this token difference must be implemented in overriden descendants, rather than with "if".
        if self.token_key is None or self.token_secret is None:
            token = None
        else:
            token = oauth.Token(self.token_key, self.token_secret)
        request = oauth.Request(method=method, url=url, parameters=parameters)
        request.sign_request(signature_method, consumer, token)
        
        # Modify request parameters with signed ones. Use only one way to pass
        # signature (either post body or query string; if our encoding were
        # something other than application/x-www-form-urlencoded, we would use
        # HTTP header then).
        #!!!TODO: make header auth default, override as oauth_mode in constructor
        postdata = None
        if method == 'GET':
            url = request.to_url()
        else:# assume that we are always application/x-www-form-urlencoded.
            postdata = request.to_postdata()
#       else:# this is for someting other than application/x-www-form-urlencoded.
#           headers.update(request.to_header())
        
        # Return signed read-only request object as required by credentials protocol.
        return Request(url=url, method=method, headers=headers, postdata=postdata)


class ApplicationCredentials(OAuthCredentials):
    REQUEST_TOKEN = ('POST', '/oauth/request_token') #NB: no version
    
    def __init__(self, consumer_key, consumer_secret, api=None):
        super(ApplicationCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=None, token_secret=None)
    
    def request(self, callback=None):
        result = self.call(self.REQUEST_TOKEN, dict(
                oauth_callback = callback,
            ), decoder=FormDecoder)
        return TemporaryCredentials(api=self.api,
            consumer_key = self.consumer_key,
            consumer_secret = self.consumer_secret,
            request_token_key = result['oauth_token'],
            request_token_secret = result['oauth_token_secret'],
            callback_confirmed = result['oauth_callback_confirmed'].lower() == 'true',
            )

class TemporaryCredentials(OAuthCredentials):
    VERIFY_TOKEN  = ('POST', '/oauth/access_token') #NB: no version
    VERIFICATION_URL = '/oauth/authorize'
    
    def __init__(self, consumer_key, consumer_secret, request_token_key, request_token_secret, callback_confirmed=None, api=None):
        super(TemporaryCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=request_token_key, token_secret=request_token_secret)
        self.callback_confirmed = callback_confirmed
    
    def verify(self, verifier):
        result = self.call(self.VERIFY_TOKEN, dict(
                oauth_verifier = verifier,
            ), decoder=FormDecoder)
        return TokenCredentials(api=self.api,
            consumer_key = self.consumer_key,
            consumer_secret = self.consumer_secret,
            access_token_key = result['oauth_token'],
            access_token_secret = result['oauth_token_secret'],
            )
        #??? what can we do with result['user_id'], result['screen_name']?
    
    @property
    def url(self):
        return self.api.normalize_url(self.VERIFICATION_URL) + '?oauth_token=%s' % self.token_key #!!!todo: urlencode

class TokenCredentials(OAuthCredentials):
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, api=None):
        super(TokenCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=access_token_key, token_secret=access_token_secret)
    
    #??? or to put account methods here directly? is it good to bring exact urls into this abstraction?
    @property
    def account(self):
        return Account(self)

class BasicCredentials(Credentials):
    """
    Basic HTTP authorization schema. Does not sign anything, but just adds
    new header to the request. Twitter has deprecated it for API requests.
    But it still officially works with streams (though not recommended).
    """
    
    def __init__(self, username, password, api=None):
        super(BasicCredentials, self).__init__(api=api)
        self.username = username
        self.password = password
    
    def sign(self, method, url, parameters, headers):
        # On-demand import to avoid errors when this credentials schema is not used.
        import base64
        
        # Add basic auth HTTP header.
        headers.update({
            'Authorization': 'Basic ' + base64.b64encode('%s:%s' % (self.username, self.password)),
        })
        
        return Request(url=url, method=method, headers=headers, postdata=None)
