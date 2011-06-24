# coding: utf-8
"""
Transports are responsible for networking activities of the API. Transport object
is usually passed to the API constructor and is used for its requests and streams.

There can be few networking layers and libraries, and the developers are free
to choose which one to use. They can also make their own transport class to
utilize their own underling library.

All derived connections must either inherit from Transport class, or at least
implement its protocol. Protocol consists of the open(request) method on the main
transport class, and read(), readline(), close() methods of returned file-like object.

Request is a signed request object as created by credentials; it has read-only
properties to use: method, url, headers, postdata. These properties must be passed
to the remote side as is, with no modifications and extensions, since they are signed.

Dependencies must be imported on demand only, i.e. when transport is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).
"""


__all__ = ['urllib2Transport', 'DEFAULT_TRANSPORT']


#
# Base classes and their protocols.
#

class TransportError(Exception):
    def __init__(self, msg, http_code, http_text):
        super(TransportError, self).__init__(msg)
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

class Transport(object):
    """
    Base transport class. Should never be instantiated directly.
    Descendants must implement open(request) method and return
    file-like object with the same protocol as in File class above.
    """
    def __init__(self):
        super(Transport, self).__init__()
        self.check() # raise if required libraries are not installed.
    
    def __call__(self, request):
        raise NotImplemented()
    
    @classmethod
    def check(self):
        raise NotImplemented()

#
# Transports via urllib2.
#

class urllib2Transport(Transport):
    """
    Transport implementation with urllib2 library. Returns library's native
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
                raise TransportError(e.msg, e.getcode(), e.read())
        finally:
            #FIXME: Restore default values after file object is instantiated.
            socket._fileobject.default_bufsize = old_default_bufsize
        
        return handle
    
    @classmethod
    def check(cls):
        import urllib2, urllib

#
# Transports via httplib.
# ??? does it support streaming at all?
#

class httplibTransport(Transport):
    pass

#
# Transports via pycurl.
#

class pycurlTransport(Transport):
    pass

#
# Automatically detect which connection to use as a default, depending on what
# libraries do you have installed. Note that this is an instance of the transport,
# not the transport class. Each and every API call performed with no transport
# specified will use this one.
#
for transport_class in [urllib2Transport, httplibTransport, pycurlTransport]:
    try:
        DEFAULT_TRANSPORT = transport_class()
        break
    except Exception, e:
        DEFAULT_TRANSPORT = None
