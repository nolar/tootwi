# coding: utf-8
"""
Credentials are the main classes in the library. End users (developers) work
with them directly. They are required for each and every API call performed,
directly or indirectly.

Primary responsibility of credentials is to authenticate and authorize a user
on remote side, and to perform actions on his/her behalf. Depending on required
access level and available keys&secrets, the developers use one of these classes:

* ApplicationCredentials - when a user does not matter, and we work anonymously;
* TemporaryCredentials - when the application is in process of authorization;
* TokenCredentials - when user authorized the application and we want their data;
* BasicCredentials - authorization by username & password (officially deprecated).

An instance of one of credentials classes is usually passed as a backbone
parameter to auxilary entities, such as models, streams, etc. They use this
instance to perform actual calls to Twitter (using call() and flow() methods).

Derivatives of the base class must implement sign(...) method which accepts
initial request parameters and returns Request object in return. Or any other
alike object that obeys Request protocol, i.e. provides these properties:
    url, method, headers, postdata.

Dependencies must be imported on demand only, i.e. when credential is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).
"""

from .api import Request, API
from .models import Account
from .decoders import JsonDecoder, FormDecoder


class Credentials(object):
    """
    Base class for authroization schemas and strategies.
    
    Instances of descendants of this class are passed as a first argument to models,
    streams and other API proxying entities. To support them and to make call syntax
    easier, this class provides methods to perform API calls. By default, these methods
    delegate API calls to utilitary API class.
    
    Descendants must implement at least sign() method, which accepts a bunch
    of request parameters, signs them as required, and returns Request instance.
    """
    
    def __init__(self, api=None):
        super(Credentials, self).__init__()
        self.api = api if api is not None else API()
    
    #??? make it protected? rename to _prepare().
    def prepare(self, target, parameters, decoder):
        """
        Internal utilitary function to unify preparation of arguments for
        call() and flow() methods, since the logic is the same, but their
        code can not be unified (one is regular call, another is generator).
        """
        
        # Make parameters and headers to be dictionaries, prepopulate if necessary.
        # Headers can also be populated by linked API instance, so ask it for data too.
        parameters = dict(parameters) if parameters is not None else {}
        headers = {}
        headers = self.api.normalize_headers(headers)
        
        # Remove Nones from parameters and headers, if for some reason they occurred there.
        parameters = dict([(k,v) for k,v in parameters.items() if v is not None])
        headers = dict([(k,v) for k,v in headers.items() if v is not None])
        
        # Normalize HTTP requisites:
        # Make method uppercased verb word.
        # Make url absolute; add format extension if it is not there yet; resolve parameters.
        (method, url) = target
        method = method.strip().upper()
        url = self.api.normalize_url(url)
        url = url if url.endswith(decoder.extension) else url + decoder.extension
        url = url % parameters #NB: extra keys will be ignored; missed ones will cause exception.
        
        # The result MUST be in the same order as accepted by Credentials.sign().
        return (method, url, parameters, headers)
    
    def sign(self, method, url, parameters, headers):
        """
        Must be overriden in descendant classes.
        Returns Request instance, signed and unmutable.
        """
        raise NotImplemented()
    
    def call(self, target, parameters=None, decoder=JsonDecoder):
        """
        Delegates the single-data call to API instance.
        Returns decoded object.
        """
        return self.api.call(self.sign(*self.prepare(target, parameters, decoder)), decoder)
    
    def flow(self, target, parameters=None, decoder=JsonDecoder):
        """
        Delegates the multi-data flow to API instance.
        Returns generator, which yields decoded objects.
        """
        return self.api.flow(self.sign(*self.prepare(target, parameters, decoder)), decoder)


class OAuthCredentials(Credentials):
    """
    Base class for OAuth authorization schemas, which derive from this class
    to add their specific behaviors and constructor parameters.
    
    todo: we accept consumer & token in the base class now. make that descendants can define
    todo: their own way to store credentials, and provide them to the common sign() method.
    todo: and do not store credentials here, since this is an abstract class.
    """
    
    def __init__(self, consumer_key, consumer_secret, token_key, token_secret, api=None):
        super(OAuthCredentials, self).__init__(api=api)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_key = token_key
        self.token_secret = token_secret

    def sign(self, method, url, parameters, headers):
        """
        Creates and signs the request with OAuth credentials. Also add extra
        parameters required for OAuth specification (such as a timestamp, etc).
        """
        
        # On-demand import to avoid errors when this credentials schema is not used.
        import oauth2 as oauth
        import time
        
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
    """
    OAuth authorization schema, which contains only consumer credentials, thus
    not linked to any account temporarily or permanently. Consumer credentials
    are provided on an application page (see https://dev.twitter.com/apps).
    Application can initiate "three-stage dance" of user authorization. Also,
    it still can access anonymous information, such as public streams, etc.
    """
    
    REQUEST_TOKEN = ('POST', '/oauth/request_token') #NB: no version
    
    def __init__(self, consumer_key, consumer_secret, api=None):
        super(ApplicationCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=None, token_secret=None)
    
    def request(self, callback=None):
        """
        Requests for temporary credentials for user authorization.
        This is stage 1 out of 3 in "thee-strage dance".
        
        Callback is an URL, where user will be redirected to when successfuly
        authorized the application. If callback is None, then out-of-band mode
        will be used and you should ask user for a pin code to finalize authorization.
        
        Returns fulfilled TemporaryCredentials in case of success, so you can
        use it immedialy for user redirection and/or verification.
        """
        result = self.call(self.REQUEST_TOKEN, dict(oauth_callback = callback), decoder=FormDecoder)
        return TemporaryCredentials(api=self.api,
            consumer_key = self.consumer_key,
            consumer_secret = self.consumer_secret,
            request_token_key = result['oauth_token'],
            request_token_secret = result['oauth_token_secret'],
            callback_confirmed = result['oauth_callback_confirmed'].lower() in ['1', 'true'],
            )


class TemporaryCredentials(OAuthCredentials):
    """
    OAuth authorization schema, which contains consumer credentials and temporary
    request token. It is used as an intermediate stage in "three-stage dance" when
    the request for authorization was made, but not yet confirmed by the user.
    """
    
    VERIFY_TOKEN  = ('POST', '/oauth/access_token') #NB: no version
    VERIFICATION_URL = '/oauth/authorize' #NB: no version
    
    def __init__(self, consumer_key, consumer_secret, request_token_key, request_token_secret, callback_confirmed=None, api=None):
        super(TemporaryCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=request_token_key, token_secret=request_token_secret)
        self.callback_confirmed = callback_confirmed
    
    @property
    def url(self):
        """
        Returns the URL where user should be directed to for authorization.
        This page is stage 2 out of 3 in "three-stage dance". The page is located
        at Twitter's official domain and shows Twitter's official certificate,
        so user can trust it (if askes to log in, for example).
        """
        return self.api.normalize_url(self.VERIFICATION_URL) + '?oauth_token=%s' % self.token_key #!!!todo: urlencode
    
    def confirm(self, verifier):
        """
        Confirms temporary credentials and retrieves final access token for
        the active user. This is stage 3 out of 3 in "three-stage dance".
        
        Verifier is either a pin code (if no callback has been given)
        or more complex string from callback HTTP request (usually comes
        in query string as "oauth_verifier").
        
        Returns fulfilled TokenCredentials in case of success, so you can
        use it immedialy for API calls or models.
        """
        result = self.call(self.VERIFY_TOKEN, dict(oauth_verifier = verifier), decoder=FormDecoder)
        return TokenCredentials(api=self.api,
            consumer_key = self.consumer_key,
            consumer_secret = self.consumer_secret,
            access_token_key = result['oauth_token'],
            access_token_secret = result['oauth_token_secret'],
            )
        #??? what can we do with result['user_id'], result['screen_name']?


class TokenCredentials(OAuthCredentials):
    """
    OAuth authorization schema, which contains both consumer and access token
    credentials. This is the most frequently used schema for API call on behalf
    of a user, who authorized the application in the "three-stage dance".
    Access token is usually stored along with user information permanently.
    """
    
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, api=None):
        super(TokenCredentials, self).__init__(api=api,
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            token_key=access_token_key, token_secret=access_token_secret)
    
    @property
    def account(self):
        """
        Returns account model for user's credentials. One exact token credentials
        are always semantically linked strictly to one exact user account (this is
        one-to-one link, not even one-to-zero!). But for code organization, it is
        better to keep all model-related definitions in the models module, rather
        than bringing them here into credentials class.
        """
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
        """
        Creates and signs the request with HTTP Basic authorization header.
        Does not alter or takes attention to any other parameters; so this
        is not truly signature, but mostly extension of the request.
        """
        
        # On-demand import to avoid errors when this credentials schema is not used.
        import base64
        
        # Add basic auth HTTP header.
        headers.update({
            'Authorization': 'Basic ' + base64.b64encode('%s:%s' % (self.username, self.password)),
        })
        
        return Request(url=url, method=method, headers=headers, postdata=None)
