# coding: utf-8
"""
Credentials are responsible for authenticating and authorizing a user on
a remote side. Credentials object is usually passed to the API constructor.

Credentials instance works as a passthrough filter: accept request parameters,
modify or extend them according to authorization protocol used, and return
these modified parameters to the consumer class (usually, connections).

Derivatives must implement sign(...) method which accepts initial request
parameters and returns SignedRequest object in return. Or any other alike
object that obeys SignedRequest protocol, i.e. provides these properties:
    url, method, headers, postdata.

Dependencies must be imported on demand only, i.e. when credential is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).
"""

#!!! add support for realm

class SignedRequest(object):
    """
    Signed request, literally. Returned from credentials instance as a
    result of signing initial request parameters with user credentials.
    Should not provide write ablities except as for constructor.
    These is no need to derive it, since this one works fine enough.
    """

    def __init__(self, url, method, headers, postdata):
        super(SignedRequest, self).__init__()
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



class Credentials(object):
    """
    Base class for authentication and authroization schemas.
    Descendants must implement sign(...) method, which accepts
    a bunch of request parameters, signs them as required, and
    return SignedRequest read-only object.
    """

    def sign(self, method, url, parameters, headers):
        raise NotImplemented()

class BasicCredentials(Credentials):
    """
    Basic HTTP authorization schema. Does not sign anything, but just adds
    new header to the request. Twitter has deprecated it for API requests.
    But it still officially works with streams (though not recommended).
    """

    def __init__(self, username, password):
        super(BasicCredentials, self).__init__()
        self.username = username
        self.password = password

    def sign(self, method, url, parameters, headers):
        # On-demand import to avoid errors when this credentials schema is not used.
        import base64

        # Add basic auth HTTP header.
        headers.update({
            'Authorization': 'Basic ' + base64.b64encode('%s:%s' % (self.username, self.password)),
        })

        return SignedRequest(url=url, method=method, headers=headers, postdata=None)



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

    def __init__(self, consumer_key, consumer_secret, access_token_key=None, access_token_secret=None):
        super(OAuthCredentials, self).__init__()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

    def sign(self, method, url, parameters, headers):
        # On-demand import to avoid errors when this credentials schema is not used.
        import oauth2 as oauth
        import time

        # Pack our credentials into oauth native classes.

        # Fulfill request parameters with oauth-specific ones.
        parameters.update({
            'oauth_version': '1.0',
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': self.access_token_key,
        })

        # Sign the request. It is good idea to keep all oauth call here.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(self.access_token_key, self.access_token_secret)
        request = oauth.Request(method=method, url=url, parameters=parameters)
        request.sign_request(signature_method, consumer, token)

        # Modify request parameters with signed ones. Use only one way to pass
        # signature (either post body or query string; if our encoding were
        # something other than application/x-www-form-urlencoded, we would use
        # HTTP header then).
        postdata = None
        if method == 'GET':
            url = request.to_url()
        else:# assume that we are always application/x-www-form-urlencoded.
            postdata = request.to_postdata()
#       else:# this is for someting other than application/x-www-form-urlencoded.
#           headers.update(request.to_header())

        # Return signed read-only request object as required by credentials protocol.
        return SignedRequest(url=url, method=method, headers=headers, postdata=postdata)


class OAuthConsumerCredentials(OAuthCredentials):
    def __init__(self, consumer_key, consumer_secret):
        super(OAuthConsumerCredentials, self).__init__(consumer_key, consumer_secret)

class OAuthRequestCredentials(OAuthCredentials):
    def __init__(self, consumer_key, consumer_secret, request_token_key, request_token_secret):
        super(OAuthRequestCredentials, self).__init__(consumer_key, consumer_secret, request_token_key, request_token_secret)

class OAuthAccessCredentials(OAuthCredentials):
    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
        super(OAuthAccessCredentials, self).__init__(consumer_key, consumer_secret, access_token_key, access_token_secret)
