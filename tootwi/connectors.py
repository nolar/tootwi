# coding: utf-8
"""
Connectors are responsible for networking activities of the API. Connector object
is usually passed to the API constructor and is used for its requests and streams.

There can be few networking layers and libraries, and the developers are free
to choose which one to use. They can also make their own connector class to
utilize their own underling library.

All derived connections must either inherit from Connector class, or at least
implement its protocol. Protocol consists of the open(request) method on the main
connector class, and read(), readline(), close() methods of returned file-like object.

Request is a signed request object as created by credentials; it has read-only
properties to use: method, url, headers, postdata. These properties must be passed
to the remote side as is, with no modifications and extensions, since they are signed.

Dependencies must be imported on demand only, i.e. when connector is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).
"""


__all__ = ['urllib2Connector', 'DEFAULT_CONNECTOR']


#
# Base classes and their protocols.
#

class ConnectorError(Exception):
    def __init__(self, msg, http_code, http_text):
        super(ConnectorError, self).__init__(msg)
        self.code = http_code
        self.text = http_text


class File(object):
    """
    Base file-like object class/interface. Specific implementations can either
    derive from this class, or use their own native file-like objects.
    """
    def close(self):
        raise NotImplemented()
    def readline(self):
        raise NotImplemented()
    def read(self, length=None):
        raise NotImplemented()


class Connector(object):
    """
    Base connector class. Should never be instantiated directly.
    Descendants must implement open(request) method and return
    file-like object with the same protocol as in File class above.
    """
    def __init__(self):
        super(Connector, self).__init__()
        self.check() # raise if required libraries are not installed.
    
    def __call__(self, request):
        raise NotImplemented()
    
    @classmethod
    def check(self):
        raise NotImplemented()

#
# Connectors via urllib2.
#

class urllib2Connector(Connector):
    """
    Connector implementation with urllib2 library. Returns library's native
    file-like object, since it conforms to the protocol of the File class.
    """
    def __call__(self, request):
        # On-demand import to avoid errors when this connection is not used.
        import urllib2, urllib
        
        import socket;
        try:
            # Rough hack to make streams work properly. Default bufsize if 8192 bytes,
            # thus causing readline() to block until all the buffer is read, even if
            # there are lines available. Bad for low-volume connections because of the lag.
            old_default_bufsize = socket._fileobject.default_bufsize
            socket._fileobject.default_bufsize = 0 # zero is for no buffering
        
            # HTTP method will be automatically choosen based on presence or absence of the postdata.
            try:
                req = urllib2.Request(request.url,
                    request.postdata if request.method=='POST' else None,
                    headers=request.headers)
                handle = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                raise ConnectorError(e.msg, e.getcode(), e.read())
        finally:
            #FIXME: Restore default values after file object is instantiated.
            socket._fileobject.default_bufsize = old_default_bufsize
        
        return handle
    
    @classmethod
    def check(cls):
        import urllib2, urllib

#
# Connectors via httplib.
# ??? does it support streaming at all?
#

class httplibConnector(Connector):
    pass

#
# Connectors via pycurl.
#

class pycurlConnector(Connector):
    pass

#
# Automatically detect which connection to use as a default, depending on what
# libraries do you have installed. Note that this is an instance of the connector,
# not the connector class. Each and every API call performed with no connector
# specified will use this one.
#
for connector_class in [urllib2Connector, httplibConnector, pycurlConnector]:
    try:
        DEFAULT_CONNECTOR = connector_class()
        break
    except Exception, e:
        DEFAULT_CONNECTOR = None
